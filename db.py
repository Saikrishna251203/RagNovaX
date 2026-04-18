import sqlite3
from collections import Counter

DB_NAME = "app.db"


# ================= CONNECTION =================
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


# ================= INIT DB =================
def init_db():
    conn = get_connection()
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
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO history (query, answer) VALUES (?, ?)",
            (query, answer)
        )

        conn.commit()
    except Exception as e:
        print("DB Error (save_query):", e)
    finally:
        conn.close()


# ================= GET HISTORY =================
def get_history():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, query FROM history ORDER BY id DESC")
        data = cur.fetchall()

        return data
    except Exception as e:
        print("DB Error (get_history):", e)
        return []
    finally:
        conn.close()


# ================= DELETE ONE =================
def delete_history_item(row_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM history WHERE id = ?", (row_id,))
        conn.commit()
    except Exception as e:
        print("DB Error (delete):", e)
    finally:
        conn.close()


# ================= CLEAR ALL =================
def clear_history():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM history")
        conn.commit()
    except Exception as e:
        print("DB Error (clear):", e)
    finally:
        conn.close()


# ================= FEEDBACK =================
def save_feedback(query, answer, rating):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO feedback (query, answer, rating) VALUES (?, ?, ?)",
            (query, answer, rating)
        )

        conn.commit()
    except Exception as e:
        print("DB Error (feedback):", e)
    finally:
        conn.close()


# ================= STATS =================
def get_feedback_stats():
    try:
        conn = get_connection()
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

        return {
            "total_queries": total_queries,
            "total_feedback": total_feedback,
            "positive_rate": round(positive_rate, 1),
            "top_terms": top_terms
        }

    except Exception as e:
        print("DB Error (stats):", e)
        return {
            "total_queries": 0,
            "total_feedback": 0,
            "positive_rate": 0,
            "top_terms": []
        }

    finally:
        conn.close()