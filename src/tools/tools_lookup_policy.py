import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from load_config import LoadConfig

CFG = LoadConfig()
# vectordb = Chroma(
#     collection_name=CFG.collection_name,
#     persist_directory=str(CFG.vectordb_dir),
#     embedding_function=OpenAIEmbeddings(model=CFG.embedding_model)
# )
# query = "Am I allowed to cancel my ticket?"
# docs = vectordb.similarity_search(query, k=CFG.k)
# test = "\n\n".join([doc.page_content for doc in docs])
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_API_BASE'] = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_BASE= os.environ.get("OPENAI_API_BASE")

@tool
def lookup_policy(query: str) -> str:
    """
    Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events.
    """
    vectordb = Chroma(
        collection_name=CFG.collection_name,
        persist_directory=str(CFG.vectordb_dir),
        embedding_function=OpenAIEmbeddings(
            model=CFG.embedding_model,
            base_url=OPENAI_API_BASE,
            api_key=OPENAI_API_KEY)
    )
    docs = vectordb.similarity_search(query, k=CFG.k)
    return "\n\n".join([doc.page_content for doc in docs])
