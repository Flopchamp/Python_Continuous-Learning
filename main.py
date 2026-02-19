import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ─── Database Manager ─────────────────────────────────────────────

class DatabaseManager:

    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.setup()

    def setup(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    is_available INTEGER DEFAULT 1
                )
            """)
            conn.commit()

    def add_book(self, title, author):              # ✅ takes strings not Book object
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "INSERT INTO books (title, author) VALUES (?, ?)",
                (title, author)
            )
            conn.commit()

    def get_all_books(self):                        # ✅ correct method name
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute("SELECT * FROM books")
            rows = cursor.fetchall()
            return [
                {"id": r[0], "title": r[1], "author": r[2], "is_available": bool(r[3])}
                for r in rows
            ]

    def get_book(self, title):                      # ✅ helper to find one book
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM books WHERE title = ?", (title,)
            )
            return cursor.fetchone()

    def update_availability(self, title, is_available):  # ✅ correct method name
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "UPDATE books SET is_available = ? WHERE title = ?",
                (1 if is_available else 0, title)
            )
            conn.commit()

    def delete_book(self, title):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "DELETE FROM books WHERE title = ?", (title,)
            )
            conn.commit()

# ─── FastAPI Setup ────────────────────────────────────────────────

app = FastAPI()
db = DatabaseManager()

# Add starter books only if database is empty
if not db.get_all_books():
    db.add_book("Python Crash Course", "Eric Matthes")      # ✅ strings not objects
    db.add_book("Clean Code", "Robert Martin")
    db.add_book("The Pragmatic Programmer", "David Thomas")

# ─── Input Model ──────────────────────────────────────────────────

class BookInput(BaseModel):
    title: str
    author: str

# ─── Endpoints ────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Welcome to the Library API! Go to /docs to explore."}

@app.get("/books")
def get_books():
    return db.get_all_books()                   # ✅ correct method name

@app.post("/books")
def add_book(book_input: BookInput):
    db.add_book(book_input.title, book_input.author)  # ✅ passing strings
    return {"message": f"Book '{book_input.title}' added successfully!"}

@app.put("/books/{title}/borrow")
def borrow_book(title: str):
    book = db.get_book(title)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book[3]:                             # book[3] is is_available
        raise HTTPException(status_code=400, detail="Book already borrowed")
    db.update_availability(title, False)        # ✅ correct method name
    return {"message": f"You borrowed '{title}'"}

@app.put("/books/{title}/return")
def return_book(title: str):
    book = db.get_book(title)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book[3]:                                 # book[3] is is_available
        raise HTTPException(status_code=400, detail="Book was not borrowed")
    db.update_availability(title, True)         # ✅ correct method name
    return {"message": f"You returned '{title}'"}

@app.delete("/books/{title}")
def delete_book(title: str):
    book = db.get_book(title)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book[3]:
        raise HTTPException(status_code=400, detail="Cannot delete a borrowed book")
    db.delete_book(title)
    return {"message": f"Book '{title}' deleted successfully!"}