import sqlite3
from collections import Counter

# ================= INIT DB =================
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            answer TEXT,
            rating TEXT
        )
    """)

    conn.commit()
    conn.close()


# ================= SAVE QUERY =================
def save_query(query, answer):
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO history (query, answer) VALUES (?, ?)",
        (query, answer)
    )

    conn.commit()
    conn.close()


# ================= GET HISTORY =================
def get_history():
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    cur.execute("SELECT id, query FROM history ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()
    return data


def delete_history_item(row_id):
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    cur.execute("DELETE FROM history WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()


def clear_history():
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    cur.execute("DELETE FROM history")
    conn.commit()
    conn.close()


# ================= FEEDBACK =================
def save_feedback(query, answer, rating):
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO feedback (query, answer, rating) VALUES (?, ?, ?)",
        (query, answer, rating)
    )

    conn.commit()
    conn.close()


# ================= STATS =================
def get_feedback_stats():
    conn = sqlite3.connect("app.db", check_same_thread=False)
    cur = conn.cursor()

    # total queries
    cur.execute("SELECT COUNT(*) FROM history")
    total_queries = cur.fetchone()[0]

    # feedback
    cur.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM feedback WHERE rating='up'")
    positive = cur.fetchone()[0]

    positive_rate = (positive / total_feedback * 100) if total_feedback else 0

    # top terms
    cur.execute("SELECT query FROM history")
    terms = []
    for (q,) in cur.fetchall():
        for word in q.lower().split():
            if len(word) > 3:
                terms.append(word)

    top_terms = Counter(terms).most_common(5)

    conn.close()

    return {
        "total_queries": total_queries,
        "total_feedback": total_feedback,
        "positive_rate": round(positive_rate, 1),
        "top_terms": top_terms
    }