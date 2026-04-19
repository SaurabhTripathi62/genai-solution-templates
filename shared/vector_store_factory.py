"""
Vector Store Factory — swap between ChromaDB, Pinecone, and FAISS
without changing any other code in your pipeline.
"""

import os
from typing import Optional, List
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


SUPPORTED_STORES = ["chroma", "pinecone", "faiss"]
SUPPORTED_EMBEDDINGS = ["openai", "huggingface"]


class VectorStoreFactory:
    """
    Create any supported vector store with a consistent interface.

    Usage:
        store = VectorStoreFactory.create("chroma", persist_dir="./db")
        store = VectorStoreFactory.create("pinecone", index_name="prod")
        store = VectorStoreFactory.create("faiss", index_path="./faiss.index")
    """

    @staticmethod
    def get_embeddings(provider: str = "openai"):
        if provider == "openai":
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif provider == "huggingface":
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        raise ValueError(f"Unknown embedding provider: {provider}")

    @staticmethod
    def create(
        store_type: str,
        embedding_provider: str = "openai",
        **kwargs,
    ) -> VectorStore:

        if store_type not in SUPPORTED_STORES:
            raise ValueError(f"Store type '{store_type}' not supported. Choose from: {SUPPORTED_STORES}")

        embeddings = VectorStoreFactory.get_embeddings(embedding_provider)

        if store_type == "chroma":
            from langchain_community.vectorstores import Chroma
            persist_dir = kwargs.get("persist_dir", "./chroma_db")
            return Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings,
                collection_name=kwargs.get("collection_name", "default"),
            )

        elif store_type == "pinecone":
            from langchain_pinecone import PineconeVectorStore
            index_name = kwargs.get("index_name")
            if not index_name:
                raise ValueError("Pinecone requires 'index_name' parameter")
            return PineconeVectorStore(
                index_name=index_name,
                embedding=embeddings,
                pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            )

        elif store_type == "faiss":
            from langchain_community.vectorstores import FAISS
            index_path = kwargs.get("index_path")
            if index_path and os.path.exists(index_path):
                return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            return FAISS.from_texts(["initialising"], embeddings)

    @staticmethod
    def list_stores() -> List[str]:
        return SUPPORTED_STORES
