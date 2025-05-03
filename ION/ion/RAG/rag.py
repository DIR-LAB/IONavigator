import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    VectorStoreIndex
)
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.response_synthesizers import ResponseMode
import shutil
from ion.Utils import setup_logger


rag_logger = setup_logger("rag")

def load_rag_index(rag_data_dir, rag_index_dir, embedding_model, reset_index=False):
    rag_logger.info(f"Loading RAG index from {rag_index_dir}")
    if reset_index:
        rag_logger.info(f"Removing existing RAG index at {rag_index_dir}")
        if os.path.exists(rag_index_dir):
            shutil.rmtree(rag_index_dir)
    if not os.path.exists(rag_index_dir):
        documents = SimpleDirectoryReader(rag_data_dir).load_data()
        rag_logger.info(f"Creating new RAG index at {rag_index_dir}")
        index = VectorStoreIndex.from_documents(documents, embedding_model=embedding_model)
        index.storage_context.persist(persist_dir=rag_index_dir)
    else:
        rag_logger.info(f"Loading existing RAG index at {rag_index_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=rag_index_dir)
        index = load_index_from_storage(storage_context)
    return index

def init_rag_query_engine(rag_config):
    rag_data_dir = rag_config["rag_source_data_dir"]
    rag_index_dir = rag_config["rag_index_dir"]
    embedding_model = rag_config["embedding_model"]
    reset_index = rag_config["reset_index"]
    rag_logger.info(f"Loading RAG index from {rag_index_dir}")
    index = load_rag_index(rag_data_dir, rag_index_dir, embedding_model, reset_index)
    rag_logger.info(f"Creating RAG query engine")
    query_engine = CitationQueryEngine.from_args(index, similarity_top_k=10, max_top_k=10, response_mode=ResponseMode.NO_TEXT)
    rag_logger.info(f"RAG query engine created")
    return query_engine


def retrieve_from_index(query_engine, search_query):
    rag_logger.info(f"Retrieving from RAG index")
    sources = query_engine.query(search_query).source_nodes
    rag_logger.info(f"Retrieved {len(sources)} sources from RAG index")
    return sources