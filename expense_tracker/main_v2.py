from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal, init_db, User, Category, Expense
from auth import create_token, verify_token, hash_password, verify_password

# ─── Init Database ────────────────────────────────────────────────
init_db()

# ─── FastAPI Setup ────────────────────────────────────────────────
app = FastAPI()

# ─── Database Session Dependency ─────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db        # give the session to the route
    finally:
        db.close()      # always close after request finishes

# ─── Auth Setup ───────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
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

@app.get("/")
def home():
    return {"message": "Expense Tracker API v2 — SQLAlchemy + PostgreSQL!"}

@app.post("/auth/register")
def register(user: UserInput, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=user.username, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    return {"message": f"User '{user.username}' registered successfully!"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_token(user.username), "token_type": "bearer"}

# ─── Category Endpoints ───────────────────────────────────────────

@app.get("/categories")
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return [{"id": c.id, "name": c.name} for c in categories]

@app.post("/categories")
def create_category(
    category: CategoryInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_cat = Category(name=category.name, user_id=current_user.id)
    db.add(new_cat)
    db.commit()
    return {"message": f"Category '{category.name}' created successfully!"}

@app.put("/categories/{name}")
def update_category(
    name: str,
    category: CategoryInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cat = db.query(Category).filter(
        Category.name == name,
        Category.user_id == current_user.id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = category.name
    db.commit()
    return {"message": "Category updated successfully!"}

@app.delete("/categories/{name}")
def delete_category(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cat = db.query(Category).filter(
        Category.name == name,
        Category.user_id == current_user.id
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"message": f"Category '{name}' deleted successfully!"}

# ─── Expense Endpoints ────────────────────────────────────────────

@app.get("/expenses")
def get_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    return [
        {"id": e.id, "title": e.title, "amount": e.amount,
         "category": e.category, "date": e.date}
        for e in expenses
    ]

@app.get("/expenses/category/{category_name}")
def get_expenses_by_category(
    category_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.category == category_name
    ).all()
    return [
        {"id": e.id, "title": e.title, "amount": e.amount,
         "category": e.category, "date": e.date}
        for e in expenses
    ]

@app.get("/expenses/{expense_id}")
def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"id": expense.id, "title": expense.title, "amount": expense.amount,
            "category": expense.category, "date": expense.date}

@app.post("/expenses")
def create_expense(
    expense: ExpenseInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        user_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    return {"message": f"Expense '{expense.title}' created successfully!"}

@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.title:    existing.title    = expense.title
    if expense.amount:   existing.amount   = expense.amount
    if expense.category: existing.category = expense.category
    if expense.date:     existing.date     = expense.date

    db.commit()
    return {"message": "Expense updated successfully!"}

@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(existing)
    db.commit()
    return {"message": "Expense deleted successfully!"}

# ─── Summary Endpoint ─────────────────────────────────────────────

@app.get("/summary")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id
    ).scalar() or 0

    breakdown = db.query(Expense.category, func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id
    ).group_by(Expense.category).all()

    return {
        "total_spent": round(total, 2),
        "by_category": {row[0]: round(row[1], 2) for row in breakdown}
    }