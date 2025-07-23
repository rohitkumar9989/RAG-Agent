from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
load_dotenv()

os.environ["HF_TOKEN"]=os.getenv("HF_TOKEN")
class RetrievalAgent:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None

    def build_vector_store(self, mcp1):
        documents=mcp1["payload"]["documents"]
        self.vector_store = FAISS.from_texts(documents, self.embeddings)

    def retrieve(self, query, k=3):
        print (self.vector_store.similarity_search(query))
        results = self.vector_store.similarity_search_with_score(query)
        average=0
        for k in results:
          average+=k[-1]
        average=average/len(results)
        results = [r[0] for r in results if r[-1] >= average]
        print (results)
        return {
            "sender": "RetrievalAgent",
            "receiver": "LLMResponseAgent",
            "type": "RETRIEVAL_RESULT",
            "trace_id": "trace-001",
            "payload": {
                "retrieved_chunks": [r.page_content for r in results],
                "query": query
            }
        }
