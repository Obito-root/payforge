"""
Electron-based authentication helper for PayForge.

This module provides a small, dependency-light ElectronAuth class that:
- Ensures a minimal users table exists in the sqlite DB path
- Can create users (for initial setup)
- Verifies credentials using salted SHA-256 hashing
- Exposes a simple login/verify API suitable for CLI/Electron usage

The implementation is defensive and logs errors rather than crashing on import.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
import logging
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _ensure_dir_for(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            logger.exception("Failed to create directory for path: %s", path)


class ElectronAuth:
    DEFAULT_DB = "/opt/payforge/database/payforge.db"
    # static salt length and hashing params; for production use a robust KDF (PBKDF2/argon2)
    SALT_SIZE = 16

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize auth backend. If db_path is None, use DEFAULT_DB.
        """
        self.db_path = db_path or self.DEFAULT_DB
        _ensure_dir_for(self.db_path)
        try:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.execute(
                """CREATE TABLE IF NOT EXISTS users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT UNIQUE NOT NULL,
                       password_hash TEXT NOT NULL,
                       salt TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )"""
            )
            self._conn.commit()
        except Exception:
            logger.exception("Failed to initialize auth database at %s", self.db_path)
            # allow object creation even if DB init failed; operations will raise

    def _hash_password(self, password: str, salt: bytes) -> str:
        """
        Compute a salted SHA-256 hex digest.
        Note: For production use a KDF like PBKDF2, bcrypt, or argon2.
        """
        if isinstance(salt, str):
            salt = salt.encode("utf-8")
        pw = password.encode("utf-8")
        digest = hashlib.sha256(salt + pw).hexdigest()
        return digest

    def _generate_salt(self) -> bytes:
        return os.urandom(self.SALT_SIZE)

    def create_user(self, username: str, password: str) -> bool:
        """
        Create a user with username and password.
        Returns True if created, False if user exists or error.
        """
        try:
            salt = self._generate_salt()
            pwd_hash = self._hash_password(password, salt)
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, pwd_hash, salt.hex()),
            )
            self._conn.commit()
            logger.info("Created user '%s' in auth DB", username)
            return True
        except sqlite3.IntegrityError:
            logger.warning("User '%s' already exists", username)
            return False
        except Exception:
            logger.exception("Error creating user '%s'", username)
            return False

    def verify_user(self, username: str, password: str) -> bool:
        """
        Verify username/password. Returns True on successful verification.
        """
        try:
            cur = self._conn.cursor()
            cur.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            if not row:
                logger.debug("User '%s' not found", username)
                return False
            stored_hash, salt_hex = row
            salt = bytes.fromhex(salt_hex)
            computed = self._hash_password(password, salt)
            return hmac.compare_digest(computed, stored_hash)
        except Exception:
            logger.exception("Error verifying user '%s'", username)
            return False

    def login(self, username: str, password: str) -> bool:
        """
        High-level login API returning True/False.
        """
        return self.verify_user(username, password)

    def set_password(self, username: str, new_password: str) -> bool:
        """
        Set or update a user's password. Returns True on success.
        """
        try:
            salt = self._generate_salt()
            pwd_hash = self._hash_password(new_password, salt)
            cur = self._conn.cursor()
            cur.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE username = ?",
                (pwd_hash, salt.hex(), username),
            )
            if cur.rowcount == 0:
                # user does not exist; create it
                return self.create_user(username, new_password)
            self._conn.commit()
            logger.info("Password updated for user '%s'", username)
            return True
        except Exception:
            logger.exception("Failed to set password for '%s'", username)
            return False

    def close(self) -> None:
        try:
            if hasattr(self, "_conn") and self._conn:
                self._conn.close()
        except Exception:
            logger.exception("Error closing DB connection")
