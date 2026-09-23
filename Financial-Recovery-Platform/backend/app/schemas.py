from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoanCreate(BaseModel):
    lender: str
    loan_type: str
    principal: float = Field(gt=0)
    outstanding: float = Field(gt=0)
    monthly_emi: float = Field(ge=0)
    interest_rate: float = Field(ge=0, default=0)
    days_overdue: int = Field(ge=0, default=0)

class ProfileUpdate(BaseModel):
    monthly_income: float = Field(ge=0)
    monthly_expenses: float = Field(ge=0)
    dependents: int = Field(ge=0, default=0)
    emergency_savings: float = Field(ge=0, default=0)
    credit_score: Optional[int] = Field(default=None, ge=300, le=900)

class NegotiationRequest(BaseModel):
    loan_id: int
    tone: str = "professional"
    extra_context: str = ""

class SettlementRequest(BaseModel):
    loan_id: int
