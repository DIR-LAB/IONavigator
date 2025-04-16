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



def load_rag_index(rag_data_dir, rag_index_dir, embedding_model, reset_index=False):
    if reset_index:
        if os.path.exists(rag_index_dir):
            shutil.rmtree(rag_index_dir)
    if not os.path.exists(rag_index_dir):
        documents = SimpleDirectoryReader(rag_data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents, embedding_model=embedding_model)
        index.storage_context.persist(persist_dir=rag_index_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=rag_index_dir)
        index = load_index_from_storage(storage_context)
    return index

def init_rag_query_engine(rag_config):
    rag_data_dir = rag_config["rag_source_data_dir"]
    rag_index_dir = rag_config["rag_index_dir"]
    embedding_model = rag_config["embedding_model"]
    reset_index = rag_config["reset_index"]
    index = load_rag_index(rag_data_dir, rag_index_dir, embedding_model, reset_index)
    query_engine = CitationQueryEngine.from_args(index, similarity_top_k=10, max_top_k=10, response_mode=ResponseMode.NO_TEXT)
    return query_engine


def retrieve_from_index(query_engine, search_query):
    sources = query_engine.query(search_query).source_nodes
    return sources