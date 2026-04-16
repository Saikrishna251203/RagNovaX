## 🧠 RAGNova X 

AI Document Intelligence Studio for:
- PDF Q&A with source citations
- Compare two PDFs side-by-side
- Confidence scoring and feedback analytics
- Single saved highlight and exportable JSON

---

## 🎯 Problem Statement

Organizations and individuals often struggle to extract meaningful insights from large PDF documents such as reports, policies, contracts, or resumes. Traditional search methods fail to provide contextual answers, comparisons, and explainability.

**RAGNova X solves this by:**
- Enabling intelligent question-answering over PDFs
- Providing explainable answers with source citations
- Allowing side-by-side comparison of two documents
- Offering confidence scoring and feedback-driven insights


## ✨ Why This Project Stands Out
 
 
`RAGNova X` is not just a basic chatbot. It adds practical product features that recruiters look for:
- Explainable answers with evidence chunks and retrieval scores
- Adjustable RAG parameters (`chunk_size`, `chunk_overlap`, `top_k`)
- A/B document comparison workflow for real-world analysis (policy, contract, resume-vs-JD comparison)
- Built-in feedback loop and usage insights

---

## 🧠 Core Features

### 1. Single Document Q&A
- Upload one PDF and ask questions.
- Returns answer, confidence, and top citations.

### 2. Compare Two PDFs
- Upload PDF A and PDF B.
- Ask one question and get side-by-side answers.
- Includes difference summary.
- Uses separate vector indexes for each document to keep comparisons accurate.

### 3. Explainable Retrieval
- Shows top retrieved chunks with score.
- Confidence labels: High / Medium / Low.

### 4. Feedback + Insights
- Users can mark answers as Useful / Not useful.
- Sidebar shows:
  - Total queries
  - Feedback count
  - Positive rate
  - Top query terms
- History supports full delete and per-item delete.

### 5. Single Saved Highlight
- Save one best answer snapshot (latest highlight).
- Export that highlight as JSON.

---

## ⚙️ Parameter Notes (Beginner Friendly)

- **Chunk Size**: Number of characters per text chunk from the PDF  
  → Larger values keep more context

- **Chunk Overlap**: Shared characters between chunks  
  → Improves continuity

- **Top-K Retrieval**: Number of chunks retrieved per query  
  → Higher = more evidence (but can add noise)

- **Score**: FAISS distance (lower is better)

- **Confidence**: Derived from top retrieval score

---

## 🏗️ Tech Stack

- **Frontend + App Logic**: Streamlit  
- **RAG Pipeline**: LangChain loaders + text splitters  
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)  
- **Vector Search**: FAISS  
- **Database**: SQLite (`history.db`)

---

## 📁 Project Structure

- `app.py` - Streamlit UI + RAG execution
- `rag_pipeline.py` - PDF processing, chunking, embeddings, retrieval
- `db.py` - History, feedback, analytics
- `requirements.txt` - Dependencies

---

## 🚀 Local Setup

# 1) Create virtual env
python -m venv .venv

# 2) Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 3) Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
 ---

  ##

1. Open the application  
2. Adjust parameters:
   - Chunk Size  
   - Chunk Overlap  
   - Top-K Retrieval  

3. Upload a PDF  

4. Ask:
   - “Summarize key points”  

5. Show:
   - Answer  
   - Confidence level  
   - Source citations  

6. Click:
   - Useful / Not useful  

7. Show:
   - Sidebar insights updating (queries, feedback rate)  

8. Switch to **Compare Two PDFs**  

9. Upload:
   - PDF A  
   - PDF B  

10. Ask a common question  

11. Explain:
   - Same query runs on two separate vector indexes  
   - Outputs:
     - Side-by-side answers  
     - Difference summary  
     - Structured comparison table  

 ---

## 🧪 Demo Workflow (For Recruiters)
Open the application
Adjust parameters:
Chunk Size
Chunk Overlap
Top-K Retrieval
Upload a PDF
Ask:
“Summarize key points”
Show:
Answer
Confidence level
Source citations
Click:
Useful / Not useful
Show:
Sidebar insights updating (queries, feedback rate)
Switch to Compare Two PDFs
Upload:
PDF A
PDF B
Ask a common question
Explain:
Same query runs on two separate vector indexes
Outputs:
Side-by-side answers
Difference summary
Structured comparison table

---

## 🛠️ Troubleshooting
PDF not processing
Ensure file is a valid PDF
Re-upload the file
Compare not working
Upload BOTH PDF A and PDF B
Wait until both show “processed”
Empty or incorrect answers
Try increasing Top-K
Adjust Chunk Size
App not running
Ensure all dependencies installed
Restart Streamlit app

----

## ✅ Final Launch Order
Test project locally
Fix any errors
Capture screenshots (store in assets/ folder)
Push code to GitHub
Add screenshots to README
Push updated README
Deploy on Streamlit Cloud
Add deployed URL to README

----

 ## 🌐 Deployment Notes
This project is fully Streamlit-based (no backend required)
All processing happens locally within the app
Steps
Push code to GitHub
Go to https://share.streamlit.io
Select your repository and branch

Set main file as:

app.py
Click Deploy
Notes:
Ensure requirements.txt includes all dependencies
If deployment fails → restart app from dashboard

---

## 👩‍💻 About the Author
 ## ** TADEPALLI SAI KRISHNA **
## 🎓 Education
- B.Tech in Artificial Intelligence & Machine Learning (CGPA: 8.3/10)  
- Consistent academic performer with strong fundamentals in AI/ML  
 ## 🛠️ Skills & Expertise
Python, SQL
Large Language Models (LLMs), Prompt Engineering
Retrieval-Augmented Generation (RAG), AI Agents
FAISS, Vector Databases
 ## 🏆 Achievements
Ranked in the Top 1% globally on Unstop

 ## 📌 Goal

To build impactful solutions in AI, Machine Learning, and Large Language Models (LLMs)
