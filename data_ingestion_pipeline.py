import os
import shutil
import time
import logging
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores.chroma import Chroma

logging.basicConfig(level=logging.INFO, format='[Ingestion Pipeline] %(message)s')
logger = logging.getLogger(__name__)

class IngestData:
    def __init__(self, db_path=None):
        self.DB_PATH = db_path or r".\src\core\vectorDB"
        logger.info(f"Initialized with DB_PATH: {self.DB_PATH}")

    def ingest(self, files):
        logger.info(f"Starting ingestion for files: {files}")
        start_time = time.process_time()

        # Clear database if exists
        if os.path.exists(self.DB_PATH):
            logger.info("Clearing database...")
            shutil.rmtree(self.DB_PATH)
            logger.info("Database cleared.")
        else:
            logger.info("No database to clear.")

        # Load and split documents
        all_chunks = []
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        for file_path in files:
            logger.info(f"Loading file: {file_path}")
            loader = PyPDFLoader(file_path=file_path)
            docs = loader.load()
            logger.info(f"Loaded {len(docs)} documents from {file_path}")
            chunks = text_splitter.split_documents(docs)
            logger.info(f"Split into {len(chunks)} chunks.")
            all_chunks.extend(chunks)
        logger.info(f"Total chunks to ingest: {len(all_chunks)}")

        # Ingest into vector DB
        if all_chunks:
            vectordb = Chroma.from_documents(all_chunks, OllamaEmbeddings(model="nomic-embed-text"), persist_directory=self.DB_PATH)
            logger.info(f"Adding {len(all_chunks)} new documents in the DB...")
            vectordb.persist()
            logger.info("Vector DB persisted.")
        else:
            logger.info("No documents to add.")

        logger.info(f"Process completed in {time.process_time() - start_time}s")
