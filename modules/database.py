import os
import re
import sqlite3
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is installed in normal setup
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(BASE_DIR / ".env")


def get_database_path() -> Path:
    db_path = os.getenv("DATABASE_PATH", "database.db")
    path = Path(db_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_database_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                question_text TEXT NOT NULL,
                answer TEXT,
                explanation TEXT,
                level INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS practice_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                user_answer TEXT,
                correct_answer TEXT,
                is_correct INTEGER NOT NULL,
                mistake_note TEXT,
                level INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                total_questions INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                wrong_count INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                weakness TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject, topic)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                mode TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(thread_id) REFERENCES chat_threads(id) ON DELETE CASCADE
            )
            """
        )
        _ensure_chat_thread_column(conn)
        _ensure_legacy_chat_thread(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                trigger_text TEXT NOT NULL,
                correction TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _ensure_default_admin(conn)


def insert_question(subject: str, topic: str, question_text: str, answer: str, explanation: str = "", level: int = 1) -> int:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO questions (subject, topic, question_text, answer, explanation, level)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (subject, topic, question_text, answer, explanation, level),
        )
        return int(cursor.lastrowid)


def insert_practice_result(
    subject: str,
    topic: str,
    question: str,
    user_answer: str,
    correct_answer: str,
    is_correct: bool,
    mistake_note: str,
    level: int = 1,
) -> int:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO practice_results
            (subject, topic, question, user_answer, correct_answer, is_correct, mistake_note, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (subject, topic, question, user_answer, correct_answer, int(is_correct), mistake_note, level),
        )
        return int(cursor.lastrowid)


def get_practice_history(limit: int = 50) -> list[sqlite3.Row]:
    init_db()
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM practice_results
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def get_progress_rows() -> list[sqlite3.Row]:
    init_db()
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM progress
            ORDER BY subject ASC, topic ASC
            """
        ).fetchall()


def create_chat_thread(title: str = "Chat baru") -> int:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chat_threads (title, updated_at)
            VALUES (?, CURRENT_TIMESTAMP)
            """,
            (_make_thread_title(title),),
        )
        return int(cursor.lastrowid)


def get_chat_thread(thread_id: int | None) -> sqlite3.Row | None:
    if not thread_id:
        return None
    init_db()
    with get_connection() as conn:
        return conn.execute("SELECT * FROM chat_threads WHERE id = ?", (int(thread_id),)).fetchone()


def get_chat_threads(limit: int = 30) -> list[sqlite3.Row]:
    init_db()
    safe_limit = max(1, min(int(limit or 30), 100))
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                t.*,
                COUNT(h.id) AS message_count
            FROM chat_threads t
            LEFT JOIN chat_history h ON h.thread_id = t.id
            GROUP BY t.id
            ORDER BY t.updated_at DESC, t.id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()


def delete_chat_thread(thread_id: int) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE thread_id = ?", (int(thread_id),))
        conn.execute("DELETE FROM chat_threads WHERE id = ?", (int(thread_id),))


def save_chat_message(mode: str, user_message: str, ai_response: str, thread_id: int | None = None) -> int:
    init_db()
    safe_thread_id = thread_id or create_chat_thread(user_message or "Chat baru")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chat_history (thread_id, mode, user_message, ai_response)
            VALUES (?, ?, ?, ?)
            """,
            (safe_thread_id, mode or "general", user_message or "", ai_response or ""),
        )
        conn.execute(
            """
            UPDATE chat_threads
            SET title = CASE
                    WHEN title = 'Chat baru' THEN ?
                    ELSE title
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (_make_thread_title(user_message or "Chat baru"), safe_thread_id),
        )
        return int(cursor.lastrowid)


def get_recent_chat_history(
    mode: str | None = None,
    limit: int = 6,
    thread_id: int | None = None,
) -> list[sqlite3.Row]:
    init_db()
    safe_limit = max(1, min(int(limit or 6), 50))
    with get_connection() as conn:
        if thread_id and mode:
            return conn.execute(
                """
                SELECT * FROM chat_history
                WHERE thread_id = ? AND mode = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (int(thread_id), mode, safe_limit),
            ).fetchall()[::-1]
        if thread_id:
            return conn.execute(
                """
                SELECT * FROM chat_history
                WHERE thread_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (int(thread_id), safe_limit),
            ).fetchall()[::-1]
        if mode:
            return conn.execute(
                """
                SELECT * FROM chat_history
                WHERE mode = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (mode, safe_limit),
            ).fetchall()[::-1]
        return conn.execute(
            """
            SELECT * FROM chat_history
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()[::-1]


def clear_chat_history() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_history")
        conn.execute("DELETE FROM chat_threads")


def create_user(username: str, email: str, password: str, role: str = "user") -> int:
    init_db()
    clean_username = (username or "").strip()
    clean_email = (email or "").strip().lower() or None
    if not clean_username:
        raise ValueError("Username tidak boleh kosong.")
    if not password:
        raise ValueError("Password tidak boleh kosong.")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (clean_username, clean_email, generate_password_hash(password), role or "user"),
        )
        return int(cursor.lastrowid)


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    init_db()
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()


def get_user_by_login(login: str) -> sqlite3.Row | None:
    init_db()
    clean_login = (login or "").strip()
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM users
            WHERE lower(username) = lower(?) OR lower(email) = lower(?)
            LIMIT 1
            """,
            (clean_login, clean_login),
        ).fetchone()


def verify_user(login: str, password: str) -> sqlite3.Row | None:
    user = get_user_by_login(login)
    if user and check_password_hash(user["password_hash"], password or ""):
        return user
    return None


def save_learning_note(subject: str, trigger_text: str, correction: str) -> int:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO learning_notes (subject, trigger_text, correction)
            VALUES (?, ?, ?)
            """,
            (subject or "umum", trigger_text or "", correction or ""),
        )
        return int(cursor.lastrowid)


def get_learning_notes(limit: int = 20) -> list[sqlite3.Row]:
    init_db()
    safe_limit = max(1, min(int(limit or 20), 500000))
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM learning_notes
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()


def get_relevant_learning_notes(query: str, subject: str | None = None, limit: int = 3) -> list[sqlite3.Row]:
    init_db()
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    token_list = sorted(query_tokens, key=len, reverse=True)[:10]
    like_clauses = " OR ".join(["trigger_text LIKE ? OR correction LIKE ?" for _ in token_list])
    like_params = []
    for token in token_list:
        like_params.extend([f"%{token}%", f"%{token}%"])

    with get_connection() as conn:
        if subject and subject != "umum":
            rows = conn.execute(
                f"""
                SELECT * FROM learning_notes
                WHERE subject IN (?, 'umum')
                AND ({like_clauses})
                ORDER BY created_at DESC, id DESC
                LIMIT 3000
                """,
                (subject, *like_params),
            ).fetchall()
        elif subject == "umum":
            rows = conn.execute(
                f"""
                SELECT * FROM learning_notes
                WHERE subject = 'umum'
                AND ({like_clauses})
                ORDER BY created_at DESC, id DESC
                LIMIT 3000
                """,
                tuple(like_params),
            ).fetchall()
        else:
            rows = conn.execute(
                f"""
                SELECT * FROM learning_notes
                WHERE {like_clauses}
                ORDER BY created_at DESC, id DESC
                LIMIT 3000
                """,
                tuple(like_params),
            ).fetchall()

    scored = []
    for row in rows:
        note_tokens = _tokens(f"{row['subject']} {row['trigger_text']} {row['correction']}")
        score = len(query_tokens.intersection(note_tokens))
        trigger_text = (row["trigger_text"] or "").lower()
        if trigger_text and trigger_text in (query or "").lower():
            score += 6
        if subject and row["subject"] == subject:
            score += 4
        if row["subject"] == "umum":
            score += 1
        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored[: max(1, int(limit or 3))]]


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if len(token) > 2}


def _ensure_default_admin(conn: sqlite3.Connection) -> None:
    admin = conn.execute("SELECT id FROM users WHERE lower(username) = lower('dhafir') LIMIT 1").fetchone()
    if admin:
        return
    default_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "dhafir012")
    conn.execute(
        """
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """,
        ("dhafir", "dhafir@local", generate_password_hash(default_password), "admin"),
    )


def _ensure_chat_thread_column(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(chat_history)").fetchall()}
    if "thread_id" not in columns:
        conn.execute("ALTER TABLE chat_history ADD COLUMN thread_id INTEGER")


def _ensure_legacy_chat_thread(conn: sqlite3.Connection) -> None:
    legacy_count = conn.execute("SELECT COUNT(*) AS total FROM chat_history WHERE thread_id IS NULL").fetchone()["total"]
    if not legacy_count:
        return
    cursor = conn.execute(
        """
        INSERT INTO chat_threads (title, updated_at)
        VALUES ('Riwayat lama', CURRENT_TIMESTAMP)
        """
    )
    conn.execute("UPDATE chat_history SET thread_id = ? WHERE thread_id IS NULL", (int(cursor.lastrowid),))


def _make_thread_title(text: str, max_length: int = 48) -> str:
    clean = re.sub(r"\s+", " ", (text or "Chat baru")).strip()
    if not clean:
        return "Chat baru"
    return clean[:max_length].rstrip()
