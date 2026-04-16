from fastapi import FastAPI
from rag_pipeline import process_pdf, query_rag

app = FastAPI()

stores = {
    "single": {"texts": None, "index": None},
    "A": {"texts": None, "index": None},
    "B": {"texts": None, "index": None},
}

@app.post("/upload")
def upload(
    file_path: str,
    doc_id: str = "single",
    chunk_size: int = 300,
    chunk_overlap: int = 80,
):
    try:
        doc_id = doc_id.upper() if doc_id.lower() in ("a", "b") else "single"
        chunk_size = max(100, min(chunk_size, 1000))
        chunk_overlap = max(0, min(chunk_overlap, 300))
        if chunk_overlap >= chunk_size:
            chunk_overlap = max(0, chunk_size // 3)

        texts, index = process_pdf(
            file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        stores[doc_id] = {"texts": texts, "index": index}
        return {
            "status": "processed",
            "doc_id": doc_id,
            "chunks": len(texts),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "doc_id": doc_id}

@app.get("/query")
def query(q: str, doc_id: str = "single", top_k: int = 5):
    try:
        doc_id = doc_id.upper() if doc_id.lower() in ("a", "b") else "single"
        store = stores.get(doc_id)
        if not store or store["texts"] is None or store["index"] is None:
            return {"error": f"Document '{doc_id}' not uploaded"}

        top_k = max(1, min(top_k, 8))
        results = query_rag(q, store["texts"], store["index"], top_k=top_k)
        return {"doc_id": doc_id, "top_k": top_k, "results": results}
    except Exception as exc:
        return {"error": str(exc), "doc_id": doc_id}