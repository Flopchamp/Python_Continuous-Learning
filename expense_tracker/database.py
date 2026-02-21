from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ─── Update your password here ────────────────────────────────────
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:yourpassword@localhost/expense_tracker"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ─── Models ───────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    expenses   = relationship("Expense", back_populates="owner")
    categories = relationship("Category", back_populates="owner")


class Category(Base):
    __tablename__ = "categories"
    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="categories")


class Expense(Base):
    __tablename__ = "expenses"
    id       = Column(Integer, primary_key=True, index=True)
    title    = Column(String, nullable=False)
    amount   = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date     = Column(String, nullable=False)
    user_id  = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="expenses")


def init_db():
    Base.metadata.create_all(bind=engine)