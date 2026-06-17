import sqlite3
from pathlib import Path
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

# Path to the SQLite database file (project root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "spendly.db"


def get_db():
    """Return a SQLite connection with row_factory set and foreign keys enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they do not already exist."""
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()


def _demo_user_exists(conn):
    """Return True if at least one user already exists in the DB."""
    return conn.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None


def seed_db():
    """Insert a demo user and a set of sample expenses (idempotent)."""
    with get_db() as conn:
        if _demo_user_exists(conn):
            # Demo data already present – nothing to do
            return

        # Insert demo user
        password_hash = generate_password_hash("demo123")
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        demo_user_id = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
        ).fetchone()["id"]

        # Sample expenses – one per category, dates spread across the current month
        categories = [
            "Food",
            "Transport",
            "Bills",
            "Health",
            "Entertainment",
            "Shopping",
            "Other",
        ]
        today = date.today()
        expense_rows = []
        for i in range(8):
            expense_date = (today.replace(day=1) + timedelta(days=i)).isoformat()
            expense_rows.append(
                (
                    demo_user_id,
                    round(5 + i * 2.5, 2),
                    categories[i % len(categories)],
                    expense_date,
                    f"Sample expense {i+1}",
                )
            )
        # Insert expenses
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expense_rows,
        )
        conn.commit()
