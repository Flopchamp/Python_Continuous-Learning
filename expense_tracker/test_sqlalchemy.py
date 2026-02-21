from database import init_db, SessionLocal, User, Category, Expense
from auth import hash_password

init_db()
print("Tables created! ✅")

session = SessionLocal()

# create test user
user = User(username="testuser", password=hash_password("test123"))
session.add(user)
session.commit()
session.refresh(user)
print(f"User created: {user.username} (id={user.id}) ✅")

# create category
cat = Category(name="Food", user_id=user.id)
session.add(cat)
session.commit()
print(f"Category created: {cat.name} ✅")

# create expense
expense = Expense(
    title="Lunch",
    amount=12.50,
    category="Food",
    date="2026-02-21",
    user_id=user.id
)
session.add(expense)
session.commit()
print(f"Expense created: {expense.title} — ${expense.amount} ✅")

# query back
expenses = session.query(Expense).filter(Expense.user_id == user.id).all()
print(f"Found {len(expenses)} expense(s) ✅")

session.close()
print("\nAll tests passed! 🎉")