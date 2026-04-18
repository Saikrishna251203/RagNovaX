import json
import re
from datetime import datetime

import streamlit as st
# ================= HISTORY INIT =================
if "history" not in st.session_state:
    st.session_state.history = []

from db import (
    clear_history,
    delete_history_item,
    get_feedback_stats,
    get_history_with_ids,
    save_feedback,
    save_query,
)
from rag_pipeline import process_pdf, query_rag

st.set_page_config(page_title="RAGNova X", page_icon="🧠", layout="wide")

st.markdown(
    """
<style>
.block-container {padding-top: 1.2rem;}
.hero {
    background: radial-gradient(circle at top left, #312e81, #0f172a 55%);
    border: 1px solid #374151;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 12px;
}
.logo-badge {
    display: inline-block;
    border: 1px solid #6366f1;
    background: #111827;
    border-radius: 999px;
    padding: 6px 12px;
    font-weight: 600;
}
.card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 10px;
}
.stat-badge {
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    background: #111827;
}
</style>
""",
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "last_answer": "",
        "last_query": "",
        "last_sources": [],
        "last_confidence": "",
        "compare_answers": {"A": "", "B": ""},
        "compare_sources": {"A": [], "B": []},
        "compare_diff": "",
        "compare_table": "",
        "compare_verdict": "",
        "saved_highlight": None,
        "query_input": "",
        "compare_ready_a": False,
        "compare_ready_b": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def confidence_from_score(score):
    if score <= 0.45:
        return "High"
    if score <= 0.9:
        return "Medium"
    return "Low"


def build_answer(data):
    if not data:
        return "Not found in document", "Low"
    top_chunk, top_score = data[0]
    confidence = confidence_from_score(top_score)
    answer = f"Answer based on retrieved context:\n\n{top_chunk[:700]}"
    return answer, confidence


def normalize_terms(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    stop_words = {
        "the", "and", "for", "with", "this", "that", "from", "into", "your",
        "are", "was", "were", "have", "has", "had", "not", "but", "can", "all",
        "any", "what", "when", "where", "which", "will", "would", "should",
        "could", "about", "into", "onto", "than", "then", "them", "they",
    }
    return {w for w in words if len(w) > 3 and w not in stop_words}


def build_compare_summary(query, data_a, data_b):
    if not data_a or not data_b:
        return "Not enough data to compare both documents."

    chunk_a = data_a[0][0]
    chunk_b = data_b[0][0]
    terms_a = normalize_terms(chunk_a)
    terms_b = normalize_terms(chunk_b)
    shared = sorted(list(terms_a.intersection(terms_b)))[:8]
    only_a = sorted(list(terms_a - terms_b))[:8]
    only_b = sorted(list(terms_b - terms_a))[:8]

    shared_text = ", ".join(shared) if shared else "No strong overlap keywords"
    only_a_text = ", ".join(only_a) if only_a else "No strong unique keywords"
    only_b_text = ", ".join(only_b) if only_b else "No strong unique keywords"

    return (
        f"Question: {query}\n\n"
        f"Common focus in A and B: {shared_text}\n\n"
        f"What is more emphasized in Document A: {only_a_text}\n\n"
        f"What is more emphasized in Document B: {only_b_text}\n\n"
        f"Tip: Use source cards below to validate exact statements."
    )


def build_compare_table_and_verdict(data_a, data_b):
    if not data_a or not data_b:
        return "Not enough evidence to build comparison table.", "Upload both documents and retry."

    terms_a = normalize_terms(data_a[0][0])
    terms_b = normalize_terms(data_b[0][0])
    shared = sorted(list(terms_a.intersection(terms_b)))[:6]
    only_a = sorted(list(terms_a - terms_b))[:6]
    only_b = sorted(list(terms_b - terms_a))[:6]

    shared_text = "<br>".join(shared) if shared else "No strong overlap"
    only_a_text = "<br>".join(only_a) if only_a else "No strong unique terms"
    only_b_text = "<br>".join(only_b) if only_b else "No strong unique terms"

    table_md = (
        "| Common Focus | Only in Document A | Only in Document B |\n"
        "|---|---|---|\n"
        f"| {shared_text} | {only_a_text} | {only_b_text} |"
    )

    overlap_ratio = 0.0
    union_count = len(terms_a.union(terms_b))
    if union_count:
        overlap_ratio = len(terms_a.intersection(terms_b)) / union_count

    if overlap_ratio > 0.35:
        verdict = "High alignment: both documents emphasize largely similar concepts."
    elif overlap_ratio > 0.18:
        verdict = "Moderate alignment: documents overlap partially but differ in emphasis."
    else:
        verdict = "Low alignment: documents focus on distinct themes."

    return table_md, verdict


def add_highlight(mode_name):
    if not st.session_state.last_answer:
        return
    st.session_state.saved_highlight = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode_name,
        "query": st.session_state.last_query,
        "confidence": st.session_state.last_confidence,
        "answer": st.session_state.last_answer,
    }


init_state()
st.markdown(
    """
<div class='hero'>
<span class='logo-badge'>🧠 RAGNova X</span><br><br>
<b>AI Document Intelligence Studio</b><br>
Explainable RAG + PDF-vs-PDF comparison + feedback analytics + tunable retrieval parameters.
</div>
""",
    unsafe_allow_html=True,
)
with st.expander("⚡ New User Quick Start", expanded=False):
    st.markdown(
        """
1. Upload one PDF (or two PDFs in compare mode).
2. Ask a question or click a quick prompt.
3. Review answer, confidence, and source citations.
4. Save highlights and export session report.
"""
    )

# Sidebar
st.sidebar.title("Control Center")
chunk_size = st.sidebar.slider("Chunk Size", 150, 800, 300, 50)
chunk_overlap = st.sidebar.slider("Chunk Overlap", 0, 200, 80, 10)
top_k = st.sidebar.slider("Top-K Retrieval", 1, 8, 5, 1)

with st.sidebar.expander("Notes: Parameter Meaning", expanded=False):
    st.markdown(
        """
- `Chunk Size`: characters in each text block. Bigger chunks = more context.
- `Chunk Overlap`: shared characters between adjacent chunks. Helps continuity.
- `Top-K`: number of chunks retrieved per query. Higher = more evidence.
- `Score`: FAISS distance (lower is usually better).
- `Confidence`: derived from top score (High/Medium/Low).
"""
    )

# ================= HISTORY UI =================
st.sidebar.subheader("🕘 History")

if st.session_state.history:

    for i, item in enumerate(st.session_state.history):

        col1, col2 = st.sidebar.columns([4,1])

        # Click to reuse query
        if col1.button(item["q"][:30] + "...", key=f"hist_{i}"):
            st.session_state.query_input = item["q"]

        # Delete button
        if col2.button("❌", key=f"del_{i}"):
            st.session_state.history.pop(i)
            st.rerun()

else:
    st.sidebar.write("No history yet")

# Clear all
if st.sidebar.button("🗑 Clear All History"):
    st.session_state.history = []
    st.rerun()
    # ================= QUERY INPUT =================
query = st.text_input("Ask question", key="query_input")
ask = st.button("Ask")

if ask and query:

    answer = ""

    # -------- SINGLE --------
    if mode == "Single PDF Q&A":
        texts, index = st.session_state.get("single_store", ([], None))

        if not texts:
            st.error("Upload PDF first")
        else:
            data = query_rag(query, texts, index, 5)
            answer = data[0][0][:700] if data else "Not found"
            st.write(answer)

    # -------- MULTI --------
    elif mode == "Upload 2 PDFs (Multi-Doc)":
        texts, index = st.session_state.get("multi_store", ([], None))

        if not texts:
            st.error("Upload both PDFs")
        else:
            data = query_rag(query, texts, index, 5)
            answer = data[0][0][:700] if data else "Not found"
            st.write(answer)

    # -------- COMPARE --------
    elif mode == "Compare 2 PDFs":
        texts_a, index_a = st.session_state.get("A_store", ([], None))
        texts_b, index_b = st.session_state.get("B_store", ([], None))

        if not texts_a or not texts_b:
            st.error("Upload both PDFs")
        else:
            data_a = query_rag(query, texts_a, index_a, 5)
            data_b = query_rag(query, texts_b, index_b, 5)

            ans_a = data_a[0][0][:500] if data_a else "No result"
            ans_b = data_b[0][0][:500] if data_b else "No result"

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Answer A")
                st.write(ans_a)
            with col2:
                st.subheader("Answer B")
                st.write(ans_b)

            answer = f"A: {ans_a[:100]} | B: {ans_b[:100]}"

    # ===== SAVE HISTORY =====
    if answer:
        st.session_state.history.insert(0, {"q": query, "a": answer})

stats = get_feedback_stats()
st.sidebar.markdown("---")
st.sidebar.subheader("Insights")
st.sidebar.write(f"Total queries: {stats['total_queries']}")
st.sidebar.write(f"Feedback count: {stats['total_feedback']}")
st.sidebar.write(f"Positive rate: {stats['positive_rate']}%")
if stats["top_terms"]:
    st.sidebar.write("Top terms:")
    for term, count in stats["top_terms"]:
        st.sidebar.write(f"- {term} ({count})")

# Main top stats
s1, s2, s3, s4 = st.columns(4)
s1.markdown(f"<div class='stat-badge'><b>Chunk Size</b><br>{chunk_size}</div>", unsafe_allow_html=True)
s2.markdown(f"<div class='stat-badge'><b>Overlap</b><br>{chunk_overlap}</div>", unsafe_allow_html=True)
s3.markdown(f"<div class='stat-badge'><b>Top-K</b><br>{top_k}</div>", unsafe_allow_html=True)
s4.markdown(
    f"<div class='stat-badge'><b>Positive Feedback</b><br>{stats['positive_rate']}%</div>",
    unsafe_allow_html=True,
)
# ================= MODE =================
mode = st.radio(
    "Workspace Mode",
    ["Single PDF Q&A", "Upload 2 PDFs (Multi-Doc)", "Compare 2 PDFs"],
    horizontal=True
)

# ================= QUICK PROMPTS =================
st.write("Quick prompts")
q1, q2, q3, q4 = st.columns(4)

if q1.button("Summarize key points"):
    st.session_state.query_input = "Summarize the key points from this document."
if q2.button("List action items"):
    st.session_state.query_input = "List all action items mentioned."
if q3.button("Find deadlines"):
    st.session_state.query_input = "Find deadlines and dates in the document."
if q4.button("Risk highlights"):
    st.session_state.query_input = "What risks are described in this document?"

# ================= INIT =================
file_a, file_b = None, None

# ================= UPLOAD =================
st.subheader("📂 Upload PDFs")

# -------- SINGLE --------
if mode == "Single PDF Q&A":
    file_a = st.file_uploader("Upload PDF", type="pdf", key="single_pdf")

# -------- MULTI DOC --------
elif mode == "Upload 2 PDFs (Multi-Doc)":
    col1, col2 = st.columns(2)

    with col1:
        file_a = st.file_uploader("Upload PDF A", type="pdf", key="multi_a")
    with col2:
        file_b = st.file_uploader("Upload PDF B", type="pdf", key="multi_b")

    if not file_a or not file_b:
        st.info("Upload both PDFs to query across documents.")

# -------- COMPARE --------
elif mode == "Compare 2 PDFs":
    col1, col2 = st.columns(2)

    with col1:
        file_a = st.file_uploader("Upload PDF A", type="pdf", key="compare_a")
    with col2:
        file_b = st.file_uploader("Upload PDF B", type="pdf", key="compare_b")

    if not file_a or not file_b:
        st.warning("Upload both PDFs to compare.")

# ================= PROCESSING =================

# -------- SINGLE --------
if mode == "Single PDF Q&A" and file_a:
    with open("temp_single.pdf", "wb") as f:
        f.write(file_a.read())

    texts, index = process_pdf("temp_single.pdf", chunk_size, chunk_overlap)
    st.session_state["single_store"] = (texts, index)

    st.success(f"Processed: {len(texts)} chunks")

# -------- MULTI DOC --------
elif mode == "Upload 2 PDFs (Multi-Doc)" and file_a and file_b:
    with open("temp_a.pdf", "wb") as f:
        f.write(file_a.read())
    with open("temp_b.pdf", "wb") as f:
        f.write(file_b.read())

    texts_a, index_a = process_pdf("temp_a.pdf", chunk_size, chunk_overlap)
    texts_b, index_b = process_pdf("temp_b.pdf", chunk_size, chunk_overlap)

    # Merge both docs
    texts = texts_a + texts_b
    index = index_a  # (or rebuild combined index if needed)

    st.session_state["multi_store"] = (texts, index)

    st.success("Both PDFs merged & processed")

# -------- COMPARE --------
elif mode == "Compare 2 PDFs" and file_a and file_b:
    with open("temp_a.pdf", "wb") as f:
        f.write(file_a.read())
    with open("temp_b.pdf", "wb") as f:
        f.write(file_b.read())

    texts_a, index_a = process_pdf("temp_a.pdf", chunk_size, chunk_overlap)
    texts_b, index_b = process_pdf("temp_b.pdf", chunk_size, chunk_overlap)

    st.session_state["A_store"] = (texts_a, index_a)
    st.session_state["B_store"] = (texts_b, index_b)

    st.success("Both PDFs ready for comparison")

# ================= QUERY =================
query = st.text_input("Ask question", key="query_input")
ask = st.button("Ask")

if ask and query:

    # -------- SINGLE --------
    if mode == "Single PDF Q&A":
        texts, index = st.session_state.get("single_store", ([], None))

        if not texts:
            st.error("Upload PDF first")
        else:
            data = query_rag(query, texts, index, 5)
            answer = data[0][0][:700] if data else "Not found"
            st.write(answer)

    # -------- MULTI --------
    elif mode == "Upload 2 PDFs (Multi-Doc)":
        texts, index = st.session_state.get("multi_store", ([], None))

        if not texts:
            st.error("Upload both PDFs")
        else:
            data = query_rag(query, texts, index, 5)
            answer = data[0][0][:700] if data else "Not found"
            st.write(answer)

    # -------- COMPARE --------
    elif mode == "Compare 2 PDFs":
        texts_a, index_a = st.session_state.get("A_store", ([], None))
        texts_b, index_b = st.session_state.get("B_store", ([], None))

        if not texts_a or not texts_b:
            st.error("Upload both PDFs")
        else:
            data_a = query_rag(query, texts_a, index_a, 5)
            data_b = query_rag(query, texts_b, index_b, 5)

            ans_a = data_a[0][0][:500] if data_a else "No result"
            ans_b = data_b[0][0][:500] if data_b else "No result"

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Answer A")
                st.write(ans_a)

            with col2:
                st.subheader("Answer B")
                st.write(ans_b)