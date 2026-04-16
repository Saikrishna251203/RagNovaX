# 🧠 RAGNova X (KnowFlow AI)

AI Document Intelligence Studio for:
- PDF Q&A with source citations
- Compare two PDFs side-by-side
- Confidence scoring and feedback analytics
- Single saved highlight and exportable JSON

---

## ✨ Why This Project Stands Out

`RAGNova X` is not just a basic chatbot. It adds practical product features that recruiters look for:
- Explainable answers with evidence chunks and retrieval scores
- Adjustable RAG parameters (`chunk_size`, `chunk_overlap`, `top_k`)
- A/B document comparison workflow for real-world analysis (policy, contract, and resume-vs-JD comparison)
- Built-in feedback loop and usage insights

---

## 🧠 Core Features

1. **Single Document Q&A**
   - Upload one PDF and ask questions.
   - Returns answer, confidence, and top citations.

2. **Compare Two PDFs**
   - Upload PDF A and PDF B.
   - Ask one question and get side-by-side answers.
   - Includes difference summary.
   - Uses separate vector indexes for each document to keep comparisons accurate.

3. **Explainable Retrieval**
   - Shows top retrieved chunks with score.
   - Confidence labels: High / Medium / Low.

4. **Feedback + Insights**
   - Users can mark answers as Useful / Not useful.
   - Sidebar shows total queries, feedback count, positive rate, top query terms.
   - History supports full delete and per-item delete with bin icon.

5. **Single Saved Highlight**
   - Save one best answer snapshot (latest highlight).
   - Export that highlight as JSON for demos or audit trails.

---

## ⚙️ Parameter Notes (Beginner Friendly)

- **Chunk Size**: Number of characters per text chunk from the PDF.
  - Larger values keep more context in each chunk.
- **Chunk Overlap**: Shared characters between adjacent chunks.
  - Helps maintain continuity across chunk boundaries.
- **Top-K Retrieval**: Number of chunks retrieved for each query.
  - Higher values provide more evidence, but may add noise.
- **Score**: FAISS distance (lower generally means better semantic match).
- **Confidence**: Derived from top retrieval score.

---

## 🏗️ Tech Stack

- **Frontend**: Streamlit
- **Backend API**: FastAPI + Uvicorn
- **RAG Core**: LangChain community loaders + text splitters
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Search**: FAISS
- **Persistence**: SQLite (`history.db`)

---

## 📁 Project Structure

- `app.py` - Streamlit UI, interactions, analytics display
- `api.py` - FastAPI endpoints for upload/query
- `rag_pipeline.py` - PDF processing, chunking, embedding, retrieval
- `db.py` - History + feedback storage and analytics
- `requirements.txt` - Python dependencies

---

## 🚀 Local Setup

```bash
# 1) Create virtual env
python -m venv .venv

# 2) Activate venv (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 3) Install deps
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Run backend
```bash
python -m uvicorn api:app --reload
```

### Run frontend (new terminal)
```bash
python -m streamlit run app.py
```

- FastAPI docs: `http://127.0.0.1:8000/docs`
- Streamlit app: `http://localhost:8501`

---

## 🧪 Demo Flow (For Recruiters)

1. Open app and show parameter panel (`Chunk Size`, `Overlap`, `Top-K`).
2. Upload a PDF and ask "Summarize key points".
3. Show answer + confidence + source citations.
4. Click Useful / Not useful and show insights update in sidebar.
5. Switch to Compare Two PDFs and ask one common question.
6. Explain that the same query runs on two separate indexes and outputs a difference summary.

---

## 🛠️ Troubleshooting

- **Failed to process PDF A / PDF B**
  - Make sure backend is running: `python -m uvicorn api:app --reload`
  - Re-upload both files if backend was restarted (indexes are in memory).
  - Verify backend is alive at `http://127.0.0.1:8000/docs`.

- **Compare query says document not ready**
  - Upload both PDF A and PDF B until each shows "processed".
  - Then ask your compare question again.



## ✅ Final Launch Order

Use this order for a clean portfolio release:
1. Test locally (backend + frontend).
2. Capture screenshots and keep them in a folder like `assets/`.
3. Push code to GitHub first.
4. Add screenshot links into this README and push again.
5. Deploy backend and frontend.
6. Update deployed URL(s) in this README.

---

## 🌐 Deployment Notes

You can deploy with:
- Streamlit Community Cloud (frontend)
- Render / Railway / Fly.io for FastAPI backend

For simple demo hosting, ensure backend URL used in `app.py` points to deployed API (instead of `127.0.0.1`).

### Streamlit Deploy Quick Steps
1. Push repo to GitHub.
2. Go to [https://share.streamlit.io](https://share.streamlit.io).
3. Select your repo, branch, and `app.py`.
4. Add any environment settings if needed.
5. Deploy and copy the app URL into README.

## 👩‍💻 Author

Built by **TADEPALLI SAI KRISHNA** as an AI/LLM portfolio project.
