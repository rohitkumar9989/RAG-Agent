from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
class LLMResponseAgent:
    def __init__(self):
        self.llm = ChatGroq(model="deepseek-r1-distill-llama-70b")
        self.parser=StrOutputParser()
        self.store={}
    def generate_response(self, context_message):
        def get_session_history(session_id:str)->BaseChatMessageHistory:
            if session_id not in self.store:
                self.store[session_id]=ChatMessageHistory()

            return self.store[session_id]
        chunks = context_message["payload"]["retrieved_chunks"]
        query = context_message["payload"]["query"]

        context_text = "\n".join(chunks)
        prompt = f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"

        prompt=ChatPromptTemplate.from_messages([
            ("system", "You are an chatbot who prepares the answer based on the retrieved text chunks from query related database, answer them properly! Only generate the summary no need of other tags, as it would be directly show in UI!!"),
            ("human", f"Here are the retrieved chunks: <chunks>{1}</chunks>".format(chunks)),
            ("human",  "I have to following question from the retrieved chunks: \n<query>{query}</query>"),
            ("ai", "Here is a summarized report on the question {query}: ")
        ])
        chain= prompt | self.llm | self.parser

        messsage_history=RunnableWithMessageHistory(chain, get_session_history, input_messages_key="query")
        response=messsage_history.invoke({
            "query":query
        }, config={
            "configurable":{"session_id": "chat1"}
        })

        return {
            "sender": "LLMResponseAgent",
            "receiver": "UI",
            "type": "LLM_RESPONSE",
            "trace_id": context_message["trace_id"],
            "payload": {
                "answer": response,
                "source_chunks": chunks
            }
        }