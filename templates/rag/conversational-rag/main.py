"""
Conversational RAG Template
RAG with persistent chat history — answers follow-up questions in context.

Usage:
    python main.py
"""

import os
from typing import List, Tuple
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()


class ConversationalRAG:
    """
    RAG system that remembers conversation history.
    Each answer is grounded in documents while being aware of prior turns.
    """

    def __init__(
        self,
        docs_path: str = "./docs/",
        persist_dir: str = "./chroma_db",
        model: str = "gpt-4o",
        memory_window: int = 5,
    ):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model=model, temperature=0.1)
        self.memory = ConversationBufferWindowMemory(
            k=memory_window,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )
        self.vectorstore = self._load_or_build_index(docs_path, persist_dir)
        self.chain = self._build_chain()

    def _load_or_build_index(self, docs_path: str, persist_dir: str) -> Chroma:
        if os.path.exists(persist_dir):
            print(f"Loading existing index from {persist_dir}")
            return Chroma(persist_directory=persist_dir, embedding_function=self.embeddings)

        print(f"Building index from {docs_path}...")
        loader = DirectoryLoader(docs_path, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
        chunks = splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=persist_dir,
        )
        print(f"Index built with {len(chunks)} chunks.")
        return vectorstore

    def _build_chain(self) -> ConversationalRetrievalChain:
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            memory=self.memory,
            return_source_documents=True,
            verbose=False,
        )

    def chat(self, question: str) -> dict:
        result = self.chain.invoke({"question": question})
        sources = list({doc.metadata.get("source", "unknown") for doc in result["source_documents"]})
        return {
            "answer": result["answer"],
            "sources": sources,
            "question": question,
        }

    def reset(self):
        self.memory.clear()
        print("Conversation history cleared.")


def main():
    print("Conversational RAG — type 'quit' to exit, 'reset' to clear history\n")

    rag = ConversationalRAG(docs_path="./sample_docs/")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() == "quit":
            break
        if question.lower() == "reset":
            rag.reset()
            continue

        result = rag.chat(question)
        print(f"\nAssistant: {result['answer']}")
        if result["sources"]:
            print(f"Sources: {', '.join(result['sources'])}")
        print()


if __name__ == "__main__":
    main()
