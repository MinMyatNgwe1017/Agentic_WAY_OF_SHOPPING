import json
import sqlite3
from datetime import datetime
from hashlib import pbkdf2_hmac
from pathlib import Path
import secrets
import re

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


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _require_non_empty(value: str, field: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} must not be empty")
    return cleaned


def _validate_email(email: str) -> str:
    cleaned = _require_non_empty(email, "email").lower()
    if not _EMAIL_RE.match(cleaned):
        raise ValueError("email must be a valid address")
    return cleaned


def _validate_password(password: str) -> str:
    if not password:
        raise ValueError("password must not be empty")
    if len(password) < 8:
        raise ValueError("password must be at least 8 characters long")
    return password


def _validate_session_id(session_id: int) -> int:
    if not isinstance(session_id, int) or session_id <= 0:
        raise ValueError("session_id must be a positive integer")
    return session_id


def _validate_user_id(user_id: int | None) -> int | None:
    if user_id is None:
        return None
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id must be a positive integer")
    return user_id


def _validate_role(role: str) -> str:
    cleaned = _require_non_empty(role, "role")
    if cleaned not in {"user", "assistant", "system"}:
        raise ValueError("role must be one of: user, assistant, system")
    return cleaned


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
    full_name_clean = _require_non_empty(full_name, "full_name")
    email_clean = _validate_email(email)
    password_clean = _validate_password(password)
    salt_hex = secrets.token_hex(16)
    password_hash = _hash_password(password_clean, salt_hex)
    with _get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, password_salt, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name_clean, email_clean, password_hash, salt_hex, _utc_now()),
        )
        return int(cursor.lastrowid)


def get_user_by_email(email: str):
    email_clean = _validate_email(email)
    with _get_conn() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email_clean,),
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
    session_id_clean = _validate_session_id(session_id)
    user_id_clean = _validate_user_id(user_id)
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO chat_sessions (session_id, user_id, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                user_id = COALESCE(excluded.user_id, chat_sessions.user_id)
            """,
            (session_id_clean, user_id_clean, _utc_now()),
        )


def record_message(session_id: int, role: str, content: str) -> None:
    session_id_clean = _validate_session_id(session_id)
    role_clean = _validate_role(role)
    content_clean = _require_non_empty(content, "content")
    get_or_create_session(session_id_clean)
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id_clean, role_clean, content_clean, _utc_now()),
        )


def record_recommendation(session_id: int, data: dict) -> None:
    session_id_clean = _validate_session_id(session_id)
    if not isinstance(data, dict):
        raise ValueError("data must be a dict")
    get_or_create_session(session_id_clean)
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO recommendations (session_id, data_json, created_at)
            VALUES (?, ?, ?)
            """,
            (session_id_clean, json.dumps(data, ensure_ascii=True), _utc_now()),
        )
