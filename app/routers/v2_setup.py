from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

print("Loading ChromaDB...")


def setUpChromaDB():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    vector_store = Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
    )

    return vector_store
