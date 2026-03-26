import json
import sqlite3
from datetime import datetime
from hashlib import pbkdf2_hmac
from pathlib import Path
import secrets

import os
DB_PATH = os.path.expanduser("~/app.db")


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _get_conn() -> sqlite3.Connection:
    # DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id)
            )
            """
        )


def _hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    dk = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return dk.hex()


def create_user(full_name: str, email: str, password: str) -> int:
    salt_hex = secrets.token_hex(16)
    password_hash = _hash_password(password, salt_hex)
    with _get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, password_salt, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email.lower().strip(), password_hash, salt_hex, _utc_now()),
        )
        return int(cursor.lastrowid)


def get_user_by_email(email: str):
    with _get_conn() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.lower().strip(),),
        )
        return cursor.fetchone()


def verify_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    expected = _hash_password(password, user["password_salt"])
    if expected != user["password_hash"]:
        return None
    return user


def get_or_create_session(session_id: int, user_id: int | None = None) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO chat_sessions (session_id, user_id, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                user_id = COALESCE(excluded.user_id, chat_sessions.user_id)
            """,
            (session_id, user_id, _utc_now()),
        )


def record_message(session_id: int, role: str, content: str) -> None:
    get_or_create_session(session_id)
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, _utc_now()),
        )


def record_recommendation(session_id: int, data: dict) -> None:
    get_or_create_session(session_id)
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO recommendations (session_id, data_json, created_at)
            VALUES (?, ?, ?)
            """,
            (session_id, json.dumps(data, ensure_ascii=True), _utc_now()),
        )
