import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import create_token, verify_token, hash_password, verify_password

# ─── Database Manager ─────────────────────────────────────────────

class DatabaseManager:
    def __init__(self, db_name="expense_tracker.db"):
        self.db_name = db_name
        self.setup()

    def setup(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            conn.commit()

    # ── Users ──────────────────────────────────────────────────────
    def add_user(self, username, hashed_password):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()

    def get_user(self, username):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            )
            return cursor.fetchone()

    # ── Categories ─────────────────────────────────────────────────
    def add_category(self, name, user_id):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "INSERT INTO categories (name, user_id) VALUES (?, ?)",
                (name, user_id)
            )
            conn.commit()

    def get_categories(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM categories WHERE user_id = ?", (user_id,)
            )
            rows = cursor.fetchall()
            return [{"id": r[0], "name": r[1]} for r in rows]

    def delete_category(self, name, user_id):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "DELETE FROM categories WHERE name = ? AND user_id = ?",
                (name, user_id)
            )
            conn.commit()

    def update_category(self, old_name, new_name, user_id):   # ✅ added missing method
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "UPDATE categories SET name = ? WHERE name = ? AND user_id = ?",
                (new_name, old_name, user_id)
            )
            conn.commit()

    # ── Expenses ───────────────────────────────────────────────────
    def add_expense(self, title, amount, category, date, user_id):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "INSERT INTO expenses (title, amount, category, date, user_id) VALUES (?,?,?,?,?)",
                (title, amount, category, date, user_id)
            )
            conn.commit()

    def get_expenses(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM expenses WHERE user_id = ?", (user_id,)
            )
            rows = cursor.fetchall()
            return [
                {"id": r[0], "title": r[1], "amount": r[2],
                 "category": r[3], "date": r[4]}
                for r in rows
            ]

    def get_expense(self, expense_id, user_id):               # ✅ added direct lookup
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
                (expense_id, user_id)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "title": row[1], "amount": row[2],
                        "category": row[3], "date": row[4]}
            return None

    def get_expenses_by_category(self, category, user_id):    # ✅ direct DB query
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM expenses WHERE category = ? AND user_id = ?",
                (category, user_id)
            )
            rows = cursor.fetchall()
            return [
                {"id": r[0], "title": r[1], "amount": r[2],
                 "category": r[3], "date": r[4]}
                for r in rows
            ]

    def update_expense(self, expense_id, title, amount, category, date, user_id):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "UPDATE expenses SET title=?, amount=?, category=?, date=? WHERE id=? AND user_id=?",
                (title, amount, category, date, expense_id, user_id)
            )
            conn.commit()

    def delete_expense(self, expense_id, user_id):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "DELETE FROM expenses WHERE id = ? AND user_id = ?",
                (expense_id, user_id)
            )
            conn.commit()

    def get_summary(self, user_id):                           # ✅ summary method
        with sqlite3.connect(self.db_name) as conn:
            total = conn.execute(
                "SELECT SUM(amount) FROM expenses WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0] or 0

            rows = conn.execute(
                "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category",
                (user_id,)
            ).fetchall()

            return {
                "total_spent": round(total, 2),
                "by_category": {row[0]: round(row[1], 2) for row in rows}
            }

# ─── Auth Setup ───────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # ✅ correct URL

app = FastAPI()
db = DatabaseManager()

def get_current_user(token: str = Depends(oauth2_scheme)):   # ✅ simplified
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ─── Input Models ─────────────────────────────────────────────────

class UserInput(BaseModel):
    username: str
    password: str

class CategoryInput(BaseModel):
    name: str

class ExpenseInput(BaseModel):
    title: str
    amount: float
    category: str
    date: str

class ExpenseUpdate(BaseModel):
    title: str = None
    amount: float = None
    category: str = None
    date: str = None

# ─── Auth Endpoints ───────────────────────────────────────────────

@app.post("/auth/register")
def register(user: UserInput):
    if db.get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    db.add_user(user.username, hash_password(user.password))
    return {"message": f"User '{user.username}' registered successfully!"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_token(user[1]), "token_type": "bearer"}

# ─── Category Endpoints ───────────────────────────────────────────

@app.get("/categories")
def get_categories(current_user: tuple = Depends(get_current_user)):
    return db.get_categories(current_user[0])

@app.post("/categories")
def create_category(category: CategoryInput, current_user: tuple = Depends(get_current_user)):
    db.add_category(category.name, current_user[0])
    return {"message": f"Category '{category.name}' created successfully!"}

@app.put("/categories/{name}")
def update_category(name: str, category: CategoryInput, current_user: tuple = Depends(get_current_user)):
    db.update_category(name, category.name, current_user[0])
    return {"message": f"Category updated successfully!"}

@app.delete("/categories/{name}")
def delete_category(name: str, current_user: tuple = Depends(get_current_user)):
    db.delete_category(name, current_user[0])
    return {"message": f"Category '{name}' deleted successfully!"}

# ─── Expense Endpoints ────────────────────────────────────────────

@app.get("/expenses")
def get_expenses(current_user: tuple = Depends(get_current_user)):
    return db.get_expenses(current_user[0])

@app.get("/expenses/category/{category_name}")
def get_expenses_by_category(category_name: str, current_user: tuple = Depends(get_current_user)):
    return db.get_expenses_by_category(category_name, current_user[0])

@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int, current_user: tuple = Depends(get_current_user)):
    expense = db.get_expense(expense_id, current_user[0])
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.post("/expenses")
def create_expense(expense: ExpenseInput, current_user: tuple = Depends(get_current_user)):
    db.add_expense(expense.title, expense.amount, expense.category, expense.date, current_user[0])
    return {"message": f"Expense '{expense.title}' created successfully!"}

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseUpdate, current_user: tuple = Depends(get_current_user)):
    existing = db.get_expense(expense_id, current_user[0])
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.update_expense(
        expense_id,
        expense.title or existing["title"],
        expense.amount or existing["amount"],
        expense.category or existing["category"],
        expense.date or existing["date"],
        current_user[0]
    )
    return {"message": f"Expense updated successfully!"}

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, current_user: tuple = Depends(get_current_user)):
    existing = db.get_expense(expense_id, current_user[0])
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete_expense(expense_id, current_user[0])
    return {"message": f"Expense deleted successfully!"}

# ─── Summary Endpoint ─────────────────────────────────────────────

@app.get("/summary")
def get_summary(current_user: tuple = Depends(get_current_user)):
    return db.get_summary(current_user[0])