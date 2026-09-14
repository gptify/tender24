import sqlite3
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

DB_PATH = Path(__file__).resolve().parent / "data" / "tenderpro.db"

class DatabaseManager:
    """Manages users, subscriptions/tiers, audit history, and seen lots for TenderPro AI."""

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Initializes database tables if they do not exist."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                company_name TEXT NOT NULL,
                tier TEXT DEFAULT 'free',
                credits_left INTEGER DEFAULT 3,
                phone TEXT,
                email TEXT,
                contact_person TEXT,
                telegram_chat_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Ensure columns exist if table was already created
            cursor.execute("PRAGMA table_info(users)")
            cols = [row["name"] for row in cursor.fetchall()]
            if "phone" not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            if "email" not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            if "contact_person" not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN contact_person TEXT")

            # Audit history table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                lot_id TEXT,
                title TEXT,
                customer TEXT,
                starting_price TEXT,
                match_score INTEGER,
                verdict TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Seen lots table for real-time Telegram alerts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seen_lots (
                lot_id TEXT PRIMARY KEY,
                portal TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified INTEGER DEFAULT 0
            )
            """)

            conn.commit()

        # Seed default test users if empty
        cls._seed_default_users()

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def _seed_default_users(cls):
        """Seeds demo accounts (Free and Pro) for immediate testing."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            row = cursor.fetchone()
            if row["count"] == 0:
                demo_users = [
                    ("demo", cls._hash_password("demo123"), "GPTify.uz Labs", "pro", 999, ""),
                    ("startup", cls._hash_password("startup123"), "Fintech Solutions MCHJ", "free", 3, "")
                ]
                cursor.executemany("""
                INSERT INTO users (username, password_hash, company_name, tier, credits_left, telegram_chat_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """, demo_users)
                conn.commit()

    @classmethod
    def authenticate_user(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticates user and returns profile if valid."""
        pwd_hash = cls._hash_password(password)
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, username, company_name, tier, credits_left, telegram_chat_id, created_at 
            FROM users WHERE username = ? AND password_hash = ?
            """, (username.strip(), pwd_hash))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    @classmethod
    def get_user(cls, username: str) -> Optional[Dict[str, Any]]:
        """Retrieves user profile by username."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, username, company_name, tier, credits_left, telegram_chat_id, created_at 
            FROM users WHERE username = ?
            """, (username.strip(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    @classmethod
    def register_user(cls, username: str, password: str, company_name: str, phone: str = "", email: str = "", contact_person: str = "") -> Dict[str, Any]:
        """Registers a new user with 3 free audit credits."""
        if not username.strip() or not password.strip():
            return {"success": False, "error": "Foydalanuvchi nomi va parol kiritilishi shart."}
        
        pwd_hash = cls._hash_password(password)
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO users (username, password_hash, company_name, tier, credits_left, phone, email, contact_person)
                VALUES (?, ?, ?, 'free', 3, ?, ?, ?)
                """, (username.strip(), pwd_hash, company_name.strip() or "Mening Kompaniyam", phone.strip(), email.strip(), contact_person.strip()))
                conn.commit()
                return {"success": True}
            except sqlite3.IntegrityError:
                return {"success": False, "error": "Ushbu foydalanuvchi nomi band. Boshqa nom tanlang."}

    @classmethod
    def quick_signup(
        cls,
        phone: str = "",
        email: str = "",
        company_name: str = "",
        contact_person: str = "",
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fast 1-click B2B lead signup using Phone or Gmail/Email. Grants 3 free audit credits."""
        clean_phone = (phone or "").strip()
        clean_email = (email or "").strip().lower()
        clean_comp = (company_name or "").strip() or "Mening Kompaniyam MCHJ"
        clean_person = (contact_person or "").strip()

        if not clean_phone and not clean_email:
            return {"success": False, "error": "Iltimos, telefon raqamingiz yoki Gmail manzilingizni kiriting."}

        # Derive username from email or phone
        if clean_email:
            username = clean_email.split("@")[0].replace(".", "_")
        else:
            username = "u_" + clean_phone.replace("+", "").replace(" ", "").replace("-", "")[-9:]

        raw_pwd = password or "tender24"
        pwd_hash = cls._hash_password(raw_pwd)

        with cls.get_connection() as conn:
            cursor = conn.cursor()
            # Check if user with this phone or email already exists
            cursor.execute("""
            SELECT id, username, company_name, tier, credits_left, phone, email, contact_person, created_at 
            FROM users 
            WHERE (phone != '' AND phone = ?) OR (email != '' AND email = ?) OR username = ?
            """, (clean_phone, clean_email, username))
            existing = cursor.fetchone()
            if existing:
                # Update existing user's missing info
                cursor.execute("""
                UPDATE users SET 
                    company_name = CASE WHEN company_name = 'Mening Kompaniyam' OR company_name = '' THEN ? ELSE company_name END,
                    contact_person = CASE WHEN contact_person IS NULL OR contact_person = '' THEN ? ELSE contact_person END,
                    phone = CASE WHEN phone IS NULL OR phone = '' THEN ? ELSE phone END,
                    email = CASE WHEN email IS NULL OR email = '' THEN ? ELSE email END
                WHERE id = ?
                """, (clean_comp, clean_person, clean_phone, clean_email, existing["id"]))
                conn.commit()
                cursor.execute("SELECT * FROM users WHERE id = ?", (existing["id"],))
                updated = cursor.fetchone()
                return {"success": True, "user": dict(updated), "is_new": False}

            # If brand new lead, insert
            try:
                cursor.execute("""
                INSERT INTO users (username, password_hash, company_name, tier, credits_left, phone, email, contact_person)
                VALUES (?, ?, ?, 'free', 3, ?, ?, ?)
                """, (username, pwd_hash, clean_comp, clean_phone, clean_email, clean_person))
                conn.commit()
                new_id = cursor.lastrowid
                cursor.execute("SELECT * FROM users WHERE id = ?", (new_id,))
                new_user = cursor.fetchone()
                return {"success": True, "user": dict(new_user), "is_new": True}
            except sqlite3.IntegrityError:
                # Username collision fallback
                import random
                username_alt = f"{username}_{random.randint(100, 999)}"
                cursor.execute("""
                INSERT INTO users (username, password_hash, company_name, tier, credits_left, phone, email, contact_person)
                VALUES (?, ?, ?, 'free', 3, ?, ?, ?)
                """, (username_alt, pwd_hash, clean_comp, clean_phone, clean_email, clean_person))
                conn.commit()
                new_id = cursor.lastrowid
                cursor.execute("SELECT * FROM users WHERE id = ?", (new_id,))
                new_user = cursor.fetchone()
                return {"success": True, "user": dict(new_user), "is_new": True}

    @classmethod
    def get_all_leads(cls) -> List[Dict[str, Any]]:
        """Retrieves all registered client companies, phone numbers, and emails for B2B CRM analytics."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, username, company_name, contact_person, phone, email, tier, credits_left, created_at
            FROM users
            ORDER BY id DESC
            """)
            return [dict(r) for r in cursor.fetchall()]

    @classmethod
    def use_audit_credit(cls, username: str) -> bool:
        """Decrements user credit if tier is free and has credits; Pro tier has unlimited credits."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tier, credits_left FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                return False
            
            tier = row["tier"]
            credits = row["credits_left"]

            if tier in ["pro", "starter", "corporate"]:
                return True
            
            if credits > 0:
                cursor.execute("UPDATE users SET credits_left = credits_left - 1 WHERE username = ?", (username,))
                conn.commit()
                return True
            return False

    @classmethod
    def log_audit(cls, username: str, tender_summary: Dict[str, Any], match_evaluation: Dict[str, Any]):
        """Logs an audit run to history."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO audit_history (username, lot_id, title, customer, starting_price, match_score, verdict)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                username,
                tender_summary.get("lot_number", "Noma'lum"),
                tender_summary.get("title", ""),
                tender_summary.get("customer", ""),
                tender_summary.get("starting_price", ""),
                match_evaluation.get("match_score", 0),
                match_evaluation.get("verdict", "")
            ))
            conn.commit()

    @classmethod
    def is_lot_seen(cls, lot_id: str) -> bool:
        """Checks if a lot has already been recorded."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM seen_lots WHERE lot_id = ?", (str(lot_id),))
            return cursor.fetchone() is not None

    @classmethod
    def mark_lot_seen(cls, lot_id: str, portal: str = "etender.uzex.uz", notified: bool = False):
        """Marks a lot as seen/notified."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO seen_lots (lot_id, portal, notified)
            VALUES (?, ?, ?)
            """, (str(lot_id), portal, 1 if notified else 0))
            conn.commit()

# Initialize DB on module load
DatabaseManager.init_db()
