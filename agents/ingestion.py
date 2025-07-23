from langchain.document_loaders import PyPDFLoader, CSVLoader, Docx2txtLoader, TextLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
class IngestionAgent():
    def __init__(self):
        self.chunk_size = 1024
        self.chunk_overlap = 10

    def find_optimal_chunk(self, files, min_size=500, max_size=2000):
        total_text = ""
        for file in files:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                total_text += f.read()

        total_len = len(total_text)
        est_size = total_len // 50
        est_size = max(min_size, min(est_size, max_size))
        est_overlap = int(est_size * 0.1)
        self.chunk_size = est_size
        self.chunk_overlap = est_overlap

    def parse_document(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        print(f"Parsing: {ext}")

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".pptx":
            loader = UnstructuredPowerPointLoader(file_path)
        elif ext == ".csv":
            loader = CSVLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        split_docs = splitter.split_documents(docs)

        return split_docs

    def process(self, files):
        self.find_optimal_chunk(files)

        all_docs = []
        for file in files:
            docs = self.parse_document(file)
            all_docs.extend(docs)

        return {
            "sender": "IngestionAgent",
            "receiver": "RetrievalAgent",
            "type": "INGESTION_COMPLETE",
            "trace_id": "trace-001",
            "payload": {
                "documents": [doc.page_content for doc in all_docs]
            }
        }
