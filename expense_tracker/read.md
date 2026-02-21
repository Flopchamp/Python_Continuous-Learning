# Expense Tracker API

This project is a FastAPI-based expense tracker application with user authentication, expense and category management, and SQLite database storage.

## Features
- User registration and login (JWT authentication)
- Add, update, delete, and view expenses
- Add, update, delete, and view categories
- Secure endpoints (require authentication)

## Setup
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn passlib[bcrypt] python-jose sqlite3
   ```
2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Auth
- `POST /auth/register` — Register a new user
- `POST /auth/login` — Login and get JWT token
- `POST /auth/logout` — Logout (dummy endpoint)

### Categories
- `GET /categories` — List categories
- `POST /categories` — Create category
- `DELETE /categories/{name}` — Delete category
- `PUT /categories/{name}` — Update category

### Expenses
- `GET /expenses` — List expenses
- `GET /expenses/{expense_id}` — Get expense by ID
- `GET /expenses/category/{category_name}` — List expenses by category
- `POST /expenses` — Create expense
- `DELETE /expenses/{expense_id}` — Delete expense
- `PUT /expenses/{expense_id}` — Update expense

## Usage Notes
- All endpoints except `/auth/register` and `/auth/login` require a valid JWT token in the `Authorization` header.
- Passwords are securely hashed using bcrypt.

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" -H "Content-Type: application/json" -d '{"username": "user1", "password": "pass123"}'
```

## License
MIT License
