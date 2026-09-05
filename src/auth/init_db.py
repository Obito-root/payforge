#!/usr/bin/env python3
"""
Database initialization helper for PayForge.

Usage examples:
  # Initialize DB and create default tables (uses /opt/payforge/database/payforge.db by default)
  python3 src/auth/init_db.py

  # Initialize DB and seed an admin user
  python3 src/auth/init_db.py --seed-admin admin --seed-pass admin123

If you run this from the repository root, the script will ensure the src/ directory
is on sys.path so imports work correctly.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import logging
from typing import Optional

# Ensure the src/ directory (one level up from this file) is on sys.path so `import auth` works.
_this_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.abspath(os.path.join(_this_dir, ".."))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from auth.electron_auth import ElectronAuth  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payforge.init_db")


DEFAULT_DB = "/opt/payforge/database/payforge.db"


def create_additional_tables(conn: sqlite3.Connection) -> None:
    """
    Create other tables the application may expect.
    Keep these idempotent (CREATE TABLE IF NOT EXISTS).
    """
    cur = conn.cursor()
    # sessions table (basic)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    # modules metadata table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            version TEXT,
            author TEXT,
            description TEXT,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # results / findings table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            module_id INTEGER,
            target TEXT,
            result_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            FOREIGN KEY(module_id) REFERENCES modules(id)
        )
        """
    )
    conn.commit()


def ensure_db_path(db_path: str) -> None:
    d = os.path.dirname(db_path)
    if d and not os.path.exists(d):
        logger.info("Creating parent directories for DB: %s", d)
        os.makedirs(d, exist_ok=True)


def initialize_database(db_path: str, seed_admin: Optional[str] = None, seed_pass: Optional[str] = None) -> None:
    ensure_db_path(db_path)

    # Use sqlite3 directly to create tables so we don't rely solely on ElectronAuth side-effects.
    logger.info("Initializing database at: %s", db_path)
    conn = sqlite3.connect(db_path)
    try:
        # users table: keep schema compatible with auth.electron_auth
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

        # create other helpful tables
        create_additional_tables(conn)

        logger.info("Database initialized successfully.")
    except Exception:
        logger.exception("Error while creating database schema.")
        raise
    finally:
        conn.close()

    if seed_admin:
        logger.info("Seeding admin user '%s' (will not overwrite existing user).", seed_admin)
        auth = ElectronAuth(db_path=db_path)
        created = auth.create_user(seed_admin, seed_pass or "admin")
        if created:
            logger.info("Admin user '%s' created successfully.", seed_admin)
        else:
            logger.info("Admin user '%s' already exists or failed to be created.", seed_admin)
        auth.close()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Initialize PayForge sqlite database and tables.")
    p.add_argument(
        "--db",
        "-d",
        default=os.environ.get("PAYFORGE_DB", DEFAULT_DB),
        help=f"path to sqlite DB (default: {DEFAULT_DB})",
    )
    p.add_argument("--seed-admin", help="Username for initial admin user to create (optional).")
    p.add_argument("--seed-pass", help="Password for initial admin user (optional). Defaults to 'admin' if omitted.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        initialize_database(args.db, args.seed_admin, args.seed_pass)
    except Exception as exc:
        logger.exception("Initialization failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
