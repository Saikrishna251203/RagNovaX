from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def process_pdf(file, chunk_size=300, chunk_overlap=80):
    loader = PyPDFLoader(file)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(docs)

    texts = [c.page_content for c in chunks]
    embeddings = model.encode(texts)

    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(np.array(embeddings))

    return texts, index

def query_rag(query, texts, index, top_k=5):
    if not texts or index is None:
        return []

    top_k = max(1, min(top_k, len(texts)))
    q_embed = model.encode([query])
    D, I = index.search(np.array(q_embed), k=top_k)

    return [(texts[i], float(D[0][idx])) for idx, i in enumerate(I[0])]