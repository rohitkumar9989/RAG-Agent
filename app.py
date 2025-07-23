import streamlit as st
import os

from agents.ingestion import IngestionAgent
from agents.retrienvalagent import RetrievalAgent
from agents.response import LLMResponseAgent

# Streamlit UI
st.set_page_config(page_title="Agentic RAG Chatbot", layout="wide")
st.title("Agentic RAG Chatbot (with MCP)")

# Upload documents
uploaded_files = st.file_uploader("Upload documents (PDF, PPTX, DOCX, CSV, TXT, MD):",
                                  type=["pdf", "pptx", "docx", "csv", "txt", "md"],
                                  accept_multiple_files=True)

if uploaded_files:
    saved_files = []
    for file in uploaded_files:
        file_path = os.path.join("tmp", file.name)
        os.makedirs("tmp", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        saved_files.append(file_path)

    st.success("Files uploaded!")

    mcp_list=[]
    # Process
    ingestion_agent = IngestionAgent()
    ingestion_context = ingestion_agent.process(saved_files)    

    mcp_list.append(ingestion_context)
    retrieval_agent = RetrievalAgent()
    retrieval_agent.build_vector_store(ingestion_context)

    llm_agent = LLMResponseAgent()

    query = st.text_input("Ask a question about your documents:")

    if st.button("Get Answer") and query:
        retrieval_context = retrieval_agent.retrieve(query)
        mcp_list.append(retrieval_context)
        llm_response = llm_agent.generate_response(retrieval_context)

        st.subheader("Answer")
        st.write(llm_response["payload"]["answer"])

        st.subheader("Source Context")
        for chunk in llm_response["payload"]["source_chunks"]:
            st.info(chunk)

    st.subheader("MCP FLOW")
    for c in mcp_list:
        st.success(c)
