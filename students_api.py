import sqlite3
from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import create_token, verify_token, hash_password, verify_password

# ─── Database Manager ─────────────────────────────────────────────

class DatabaseManager:

    def __init__(self, db_name="students.db"):
        self.db_name = db_name
        self.setup()

    def setup(self):
        with sqlite3.connect(self.db_name) as conn:
         conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                grade INTEGER NOT NULL,
                course TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
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

    def add_student(self, name, age, grade, course):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "INSERT INTO students (name, age, grade, course) VALUES (?, ?, ?, ?)",
                (name, age, grade, course)
            )
            conn.commit()

    def get_all_students(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute("SELECT * FROM students")
            rows = cursor.fetchall()
            return [
                {"id": r[0], "name": r[1], "age": r[2], "grade": r[3], "course": r[4]}
                for r in rows
            ]

    def get_student(self, name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM students WHERE name = ?", (name,)
            )
            return cursor.fetchone()

    def update_student(self, name, age, grade, course):   # ✅ fixed method name
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "UPDATE students SET age = ?, grade = ?, course = ? WHERE name = ?",
                (age, grade, course, name)
            )
            conn.commit()

    def update_grade(self, name, grade):                  # ✅ dedicated grade update
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "UPDATE students SET grade = ? WHERE name = ?",
                (grade, name)
            )
            conn.commit()

    def delete_student(self, name):                       # ✅ only needs name
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "DELETE FROM students WHERE name = ?", (name,)
            )
            conn.commit()

    def get_top_students(self):                           # ✅ new method
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute(
                "SELECT * FROM students WHERE grade >= 80 ORDER BY grade DESC"
            )
            rows = cursor.fetchall()
            return [
                {"id": r[0], "name": r[1], "age": r[2], "grade": r[3], "course": r[4]}
                for r in rows
            ]


# ─── Auth Setup ───────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

# ─── FastAPI Setup ────────────────────────────────────────────────

app = FastAPI()
db = DatabaseManager()

if not db.get_all_students():
    db.add_student("Alice",   20, 85, "Computer Science")
    db.add_student("Bob",     22, 45, "Mathematics")
    db.add_student("Charlie", 21, 91, "Computer Science")
    db.add_student("Diana",   23, 78, "Physics")
    db.add_student("Eve",     20, 95, "Computer Science")

# ─── Input Models ─────────────────────────────────────────────────

class StudentInput(BaseModel):
    name: str
    age: int
    grade: int
    course: str

class GradeUpdate(BaseModel):
    grade: int

class UserInput(BaseModel):
    username: str
    password: str

#
# ─── Auth Endpoints ───────────────────────────────────────────────
@app.post("/auth/register")
def register(user: UserInput):
    existing = db.get_user(user.username)   # ✅ prevent duplicate usernames
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    db.add_user(user.username, hashed_password)
    return {"message": f"User '{user.username}' registered successfully!"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user[2]):  # user[2] is password
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}


# ─── Endpoints ────────────────────────────────────────────────────


@app.get("/")
def home():
    return {"message": "Welcome to the Student Management API!"}

@app.get("/students")
def get_all_students():
    return db.get_all_students()

@app.get("/students/top")                                 # ✅ added missing endpoint
def get_top_students():
    top = db.get_top_students()
    if not top:
        raise HTTPException(status_code=404, detail="No top students found")
    return top

@app.get("/students/{name}")                              # ✅ added missing endpoint
def get_student(name: str):
    student = db.get_student(name)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student[0], "name": student[1], "age": student[2],
            "grade": student[3], "course": student[4]}

@app.post("/students")
def create_student(student: StudentInput, current_user: str = Depends(get_current_user)):
    existing = db.get_student(student.name)
    if existing:                                          # ✅ prevent duplicates
        raise HTTPException(status_code=400, detail="Student already exists")
    db.add_student(student.name, student.age, student.grade, student.course)
    return {"message": f"Student '{student.name}' added successfully!"}


@app.put("/students/{name}")
def update_student(name: str, student: StudentInput, current_user: str = Depends(get_current_user)):
    existing = db.get_student(name)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    db.update_student(name, student.age, student.grade, student.course)
    return {"message": f"Student '{name}' updated successfully!"}

@app.put("/students/{name}/grade")
def update_grade(name: str, grade_update: GradeUpdate, current_user: str = Depends(get_current_user)):
    existing = db.get_student(name)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    if grade_update.grade < 0 or grade_update.grade > 100:  # ✅ validate grade range
        raise HTTPException(status_code=400, detail="Grade must be between 0 and 100")
    db.update_grade(name, grade_update.grade)
    return {"message": f"Grade updated to {grade_update.grade} for '{name}'"}

@app.delete("/students/{name}")
def delete_student(name: str, current_user: str = Depends(get_current_user)):                            # ✅ no body needed
    existing = db.get_student(name)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete_student(name)
    return {"message": f"Student '{name}' deleted successfully!"}