from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("FinancialProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    negotiations = relationship("Negotiation", back_populates="user", cascade="all, delete-orphan")

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lender = Column(String(150), nullable=False)
    loan_type = Column(String(80), nullable=False)
    principal = Column(Float, nullable=False)
    outstanding = Column(Float, nullable=False)
    monthly_emi = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0)
    days_overdue = Column(Integer, default=0)
    status = Column(String(40), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="loans")

class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    monthly_income = Column(Float, default=0)
    monthly_expenses = Column(Float, default=0)
    dependents = Column(Integer, default=0)
    emergency_savings = Column(Float, default=0)
    credit_score = Column(Integer, nullable=True)
    user = relationship("User", back_populates="profile")

class Negotiation(Base):
    __tablename__ = "negotiations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    result = Column(Text, nullable=False)
    settlement_percent = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="negotiations")