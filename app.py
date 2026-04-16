import json
import re
from datetime import datetime

import requests
import streamlit as st

from db import (
    clear_history,
    delete_history_item,
    get_feedback_stats,
    get_history_with_ids,
    save_feedback,
    save_query,
)

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

st.sidebar.subheader("History")
if st.sidebar.button("Delete History"):
    clear_history()
    st.sidebar.success("History deleted")
    st.rerun()

for row_id, query_text in get_history_with_ids():
    c1, c2 = st.sidebar.columns([5, 1])
    c1.caption(query_text[:45] + ("..." if len(query_text) > 45 else ""))
    if c2.button("🗑️", key=f"del_hist_{row_id}", help="Delete this query"):
        delete_history_item(row_id)
        st.rerun()

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

mode = st.radio("Workspace Mode", ["Single Document Q&A", "Compare Two PDFs"], horizontal=True)

# Feature 1: Quick prompt chips
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

if mode == "Single Document Q&A":
    file = st.file_uploader("Upload PDF", type=["pdf"], key="single_upload")
    if file:
        with open("temp_single.pdf", "wb") as f:
            f.write(file.read())
        up = requests.post(
            "http://127.0.0.1:8000/upload",
            params={
                "file_path": "temp_single.pdf",
                "doc_id": "single",
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            },
            timeout=60,
        ).json()
        st.success(f"Document processed. Chunks created: {up.get('chunks', 0)}")
else:
    ca, cb = st.columns(2)
    with ca:
        file_a = st.file_uploader("Upload PDF A", type=["pdf"], key="upload_a")
    with cb:
        file_b = st.file_uploader("Upload PDF B", type=["pdf"], key="upload_b")

    if file_a:
        with open("temp_a.pdf", "wb") as f:
            f.write(file_a.read())
        try:
            resp_a = requests.post(
                "http://127.0.0.1:8000/upload",
                params={
                    "file_path": "temp_a.pdf",
                    "doc_id": "A",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                },
                timeout=60,
            )
            payload_a = resp_a.json() if resp_a.content else {}
            if resp_a.ok and payload_a.get("status") == "processed":
                st.session_state.compare_ready_a = True
                st.success("PDF A processed")
            else:
                st.session_state.compare_ready_a = False
                st.error(f"Failed to process PDF A: {payload_a.get('message', 'Backend error')}")
        except requests.RequestException:
            st.session_state.compare_ready_a = False
            st.error("Failed to process PDF A: backend not reachable. Start FastAPI first.")

    if file_b:
        with open("temp_b.pdf", "wb") as f:
            f.write(file_b.read())
        try:
            resp_b = requests.post(
                "http://127.0.0.1:8000/upload",
                params={
                    "file_path": "temp_b.pdf",
                    "doc_id": "B",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                },
                timeout=60,
            )
            payload_b = resp_b.json() if resp_b.content else {}
            if resp_b.ok and payload_b.get("status") == "processed":
                st.session_state.compare_ready_b = True
                st.success("PDF B processed")
            else:
                st.session_state.compare_ready_b = False
                st.error(f"Failed to process PDF B: {payload_b.get('message', 'Backend error')}")
        except requests.RequestException:
            st.session_state.compare_ready_b = False
            st.error("Failed to process PDF B: backend not reachable. Start FastAPI first.")

    missing_docs = []
    if not st.session_state.compare_ready_a:
        missing_docs.append("PDF A")
    if not st.session_state.compare_ready_b:
        missing_docs.append("PDF B")
    if missing_docs:
        st.info(f"Upload {', '.join(missing_docs)} to run compare query.")

query = st.text_input("Ask question", key="query_input")
ask = st.button("Ask")

if ask and query:
    save_query(query)
    st.session_state.last_query = query

    if mode == "Single Document Q&A":
        payload = requests.get(
            "http://127.0.0.1:8000/query",
            params={"q": query, "doc_id": "single", "top_k": top_k},
            timeout=60,
        ).json()
        if "error" in payload:
            st.error(payload["error"])
        else:
            data = payload["results"]
            answer, confidence = build_answer(data)
            st.session_state.last_answer = answer
            st.session_state.last_confidence = confidence
            st.session_state.last_sources = data[:3]
    else:
        if not st.session_state.compare_ready_a or not st.session_state.compare_ready_b:
            missing_docs = []
            if not st.session_state.compare_ready_a:
                missing_docs.append("PDF A")
            if not st.session_state.compare_ready_b:
                missing_docs.append("PDF B")
            st.error(f"Please upload {', '.join(missing_docs)} before compare query.")
            st.stop()

        res_a = requests.get(
            "http://127.0.0.1:8000/query",
            params={"q": query, "doc_id": "A", "top_k": top_k},
            timeout=60,
        ).json()
        res_b = requests.get(
            "http://127.0.0.1:8000/query",
            params={"q": query, "doc_id": "B", "top_k": top_k},
            timeout=60,
        ).json()
        if "error" in res_a or "error" in res_b:
            st.error("Compare documents are not ready. Re-upload PDF A and PDF B.")
        else:
            data_a = res_a["results"]
            data_b = res_b["results"]
            ans_a, _ = build_answer(data_a)
            ans_b, _ = build_answer(data_b)
            st.session_state.compare_answers = {"A": ans_a, "B": ans_b}
            st.session_state.compare_sources = {"A": data_a[:3], "B": data_b[:3]}
            st.session_state.compare_diff = build_compare_summary(query, data_a, data_b)
            table_md, verdict = build_compare_table_and_verdict(data_a, data_b)
            st.session_state.compare_table = table_md
            st.session_state.compare_verdict = verdict

if mode == "Single Document Q&A" and st.session_state.last_answer:
    st.subheader("Answer")
    st.markdown(f"<div class='card'>{st.session_state.last_answer}</div>", unsafe_allow_html=True)
    st.write(f"Confidence: **{st.session_state.last_confidence}**")

    src_col, fb_col = st.columns([2, 1])
    with src_col:
        st.subheader("Source Citations")
        for i, (chunk, score) in enumerate(st.session_state.last_sources, start=1):
            st.markdown(
                f"<div class='card'><b>{i}. Score: {round(score, 3)}</b><br>{chunk[:280]}...</div>",
                unsafe_allow_html=True,
            )
    with fb_col:
        st.subheader("Actions")
        if st.button("Useful"):
            save_feedback(st.session_state.last_query, st.session_state.last_answer, "up")
            st.success("Feedback saved")
        if st.button("Not useful"):
            save_feedback(st.session_state.last_query, st.session_state.last_answer, "down")
            st.success("Feedback saved")
        if st.button("Save Highlight"):
            add_highlight(mode)
            st.success("Saved to highlights")
        if st.button("Clear Summary"):
            st.session_state.last_answer = ""
            st.session_state.last_sources = []
            st.session_state.last_confidence = ""
            st.rerun()

if mode == "Compare Two PDFs" and st.session_state.compare_answers["A"]:
    st.subheader("Comparison")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Document A")
        st.markdown(f"<div class='card'>{st.session_state.compare_answers['A']}</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("### Document B")
        st.markdown(f"<div class='card'>{st.session_state.compare_answers['B']}</div>", unsafe_allow_html=True)
    st.markdown("### Difference Summary")
    st.markdown(f"<div class='card'>{st.session_state.compare_diff}</div>", unsafe_allow_html=True)
    st.markdown("### Structured Comparison Table")
    st.markdown(st.session_state.compare_table)
    st.success(f"Verdict: {st.session_state.compare_verdict}")

# Feature 2: Session report export
st.markdown("---")
st.subheader("Saved Highlight")
if st.session_state.saved_highlight:
    item = st.session_state.saved_highlight
    st.markdown(
        f"<div class='card'><b>{item['time']}</b> | {item['mode']}<br>"
        f"<b>Query:</b> {item['query']}<br>"
        f"<b>Confidence:</b> {item['confidence']}<br>"
        f"{item['answer'][:220]}...</div>",
        unsafe_allow_html=True,
    )
    st.download_button(
        "Download Highlight (JSON)",
        data=json.dumps(item, indent=2),
        file_name="knowflow_highlight.json",
        mime="application/json",
    )
else:
    st.info("No highlight saved yet. Use 'Save Highlight' after getting an answer.")