import sqlite3
from collections import Counter

# ================= INIT DB =================
import sqlite3

def init_db():
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            answer TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

conn = sqlite3.connect("history.db", check_same_thread=False)
cur = conn.cursor()

def get_feedback_stats():
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    try:
        cur.execute("SELECT COUNT(*) FROM history")
        count = cur.fetchone()[0]
    except:
        count = 0

    conn.close()
    return count

def save_query(q):
    cur.execute("INSERT INTO history VALUES (?)", (q,))
    conn.commit()

def get_history():
    cur.execute("SELECT query FROM history")
    return cur.fetchall()

def get_history_with_ids():
    cur.execute("SELECT rowid, query FROM history ORDER BY rowid DESC")
    return cur.fetchall()

def clear_history():
    cur.execute("DELETE FROM history")
    conn.commit()

def delete_history_item(row_id):
    cur.execute("DELETE FROM history WHERE rowid = ?", (row_id,))
    conn.commit()

def save_feedback(query, answer, rating):
    cur.execute(
        "INSERT INTO feedback(query, answer, rating) VALUES (?, ?, ?)",
        (query, answer, rating),
    )
    conn.commit()

def get_feedback_stats():
    cur.execute("SELECT COUNT(*) FROM history")
    total_queries = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM feedback WHERE rating = 'up'")
    positive_feedback = cur.fetchone()[0]

    positive_rate = 0.0
    if total_feedback:
        positive_rate = (positive_feedback / total_feedback) * 100

    cur.execute("SELECT query FROM history")
    terms = []
    for (query,) in cur.fetchall():
        for term in query.lower().split():
            cleaned = term.strip(".,!?;:\"'()[]{}")
            if len(cleaned) > 3:
                terms.append(cleaned)

    top_terms = Counter(terms).most_common(5)
    return {
        "total_queries": total_queries,
        "total_feedback": total_feedback,
        "positive_rate": round(positive_rate, 1),
        "top_terms": top_terms,
    }