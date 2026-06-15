from flask import Flask, render_template, request, redirect, url_for, session, abort
from database.db import get_db, init_db, seed_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
# Secret key for session handling – replace with a secure random value for production
app.secret_key = "super-secret-key-CHANGE-ME"

# Initialise the database and seed demo data on startup
with app.app_context():
    init_db()
    seed_db()

# ------------------------------------------------------------------ #
# Helper constants and functions
# ------------------------------------------------------------------ #
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

def login_required(view_func):
    """Simple decorator to enforce authentication for protected routes."""
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for('login'))
        return view_func(**kwargs)
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

# ------------------------------------------------------------------ #
# Public routes
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        password_hash = generate_password_hash(password)
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
            user_id = cur.lastrowid
            session["user_id"] = user_id
            session["user_name"] = name
            return redirect(url_for('profile'))
        except sqlite3.IntegrityError:
            error = "Email already registered."
            return render_template("register.html", error=error)
    # GET request
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for('profile'))
        else:
            error = "Invalid email or password."
            return render_template("login.html", error=error)
    # GET request
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('landing'))

# ------------------------------------------------------------------ #
# Protected routes – require login
# ------------------------------------------------------------------ #

@app.route("/profile")
@login_required
def profile():
    user_id = session["user_id"]
    conn = get_db()
    user = conn.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    expenses = conn.execute(
        "SELECT id, amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    ).fetchall()
    return render_template("profile.html", user=user, expenses=expenses)


@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
        except ValueError:
            error = "Invalid amount format."
            return render_template("add_expense.html", categories=CATEGORIES, error=error)
        category = request.form["category"]
        date_str = request.form["date"]
        description = request.form.get("description", "").strip() or None
        conn = get_db()
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], amount, category, date_str, description),
        )
        conn.commit()
        return redirect(url_for('profile'))
    # GET request – render form
    return render_template("add_expense.html", categories=CATEGORIES)


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    conn = get_db()
    expense = conn.execute(
        "SELECT id, amount, category, date, description FROM expenses WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    ).fetchone()
    if not expense:
        abort(404)
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
        except ValueError:
            error = "Invalid amount format."
            return render_template("edit_expense.html", expense=expense, categories=CATEGORIES, error=error)
        category = request.form["category"]
        date_str = request.form["date"]
        description = request.form.get("description", "").strip() or None
        conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ?",
            (amount, category, date_str, description, id),
        )
        conn.commit()
        return redirect(url_for('profile'))
    # GET request – render edit form
    return render_template("edit_expense.html", expense=expense, categories=CATEGORIES)


@app.route("/expenses/<int:id>/delete", methods=["POST"])
@login_required
def delete_expense(id):
    conn = get_db()
    conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    )
    conn.commit()
    return redirect(url_for('profile'))

# ------------------------------------------------------------------ #
# Placeholder routes – retained for reference (now functional)
# ------------------------------------------------------------------ #

# Note: The original stub routes have been replaced with functional implementations above.

if __name__ == "__main__":
    app.run(debug=True, port=5001)
