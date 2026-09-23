from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import User, Loan, FinancialProfile, Negotiation
from .schemas import RegisterRequest, LoginRequest, TokenResponse, LoanCreate, ProfileUpdate, NegotiationRequest, SettlementRequest
from .security import hash_password, verify_password, create_token, get_current_user
from .services import calculate_settlement, fallback_letter, gemini_letter

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinRelief AI Backend",
    version="1.0.0",
    description="AI-powered debt relief and financial recovery platform."
)

origins = [x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FinRelief AI Backend", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/auth/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(409, "Email already registered")
    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(FinancialProfile(user_id=user.id))
    db.commit()
    return TokenResponse(access_token=create_token(user.id))

@app.post("/api/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return TokenResponse(access_token=create_token(user.id))

@app.get("/api/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}

@app.get("/api/loans")
def list_loans(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loans = db.query(Loan).filter(Loan.user_id == user.id).order_by(Loan.id.desc()).all()
    return [
        {
            "id": l.id, "lender": l.lender, "loan_type": l.loan_type,
            "principal": l.principal, "outstanding": l.outstanding,
            "monthly_emi": l.monthly_emi, "interest_rate": l.interest_rate,
            "days_overdue": l.days_overdue, "status": l.status
        } for l in loans
    ]

@app.post("/api/loans")
def create_loan(data: LoanCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = Loan(user_id=user.id, **data.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return {"id": loan.id, "message": "Loan added successfully"}

@app.delete("/api/loans/{loan_id}")
def delete_loan(loan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == user.id).first()
    if not loan:
        raise HTTPException(404, "Loan not found")
    db.delete(loan)
    db.commit()
    return {"message": "Loan deleted"}

@app.get("/api/profile")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).first()
    return {
        "monthly_income": profile.monthly_income,
        "monthly_expenses": profile.monthly_expenses,
        "dependents": profile.dependents,
        "emergency_savings": profile.emergency_savings,
        "credit_score": profile.credit_score
    }

@app.put("/api/profile")
def update_profile(data: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).first()
    if not profile:
        profile = FinancialProfile(user_id=user.id)
        db.add(profile)
    for key, value in data.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    return {"message": "Financial profile updated"}

@app.get("/api/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loans = db.query(Loan).filter(Loan.user_id == user.id).all()
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).first()
    total_outstanding = sum(x.outstanding for x in loans)
    total_emi = sum(x.monthly_emi for x in loans)
    surplus = (profile.monthly_income if profile else 0) - (profile.monthly_expenses if profile else 0)
    health = "STABLE" if surplus >= total_emi else ("STRESSED" if surplus > 0 else "CRITICAL")
    return {
        "loan_count": len(loans),
        "total_outstanding": round(total_outstanding, 2),
        "total_emi": round(total_emi, 2),
        "monthly_surplus": round(surplus, 2),
        "financial_health": health
    }

@app.post("/api/settlement/predict")
def predict(data: SettlementRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == data.loan_id, Loan.user_id == user.id).first()
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).first()
    if not loan or not profile:
        raise HTTPException(404, "Loan or financial profile not found")
    return calculate_settlement(loan, profile)

@app.post("/api/negotiation/generate")
def generate_negotiation(data: NegotiationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == data.loan_id, Loan.user_id == user.id).first()
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).first()
    if not loan or not profile:
        raise HTTPException(404, "Loan or financial profile not found")

    prediction = calculate_settlement(loan, profile)
    result = gemini_letter(user, loan, profile, data.tone, data.extra_context)
    if not result:
        result = fallback_letter(user, loan, profile, data.tone, data.extra_context)

    record = Negotiation(
        user_id=user.id,
        loan_id=loan.id,
        prompt=f"tone={data.tone}; context={data.extra_context}",
        result=result,
        settlement_percent=prediction["settlement_percent"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "loan_id": loan.id,
        "settlement": prediction,
        "letter": result,
        "created_at": record.created_at
    }

@app.get("/api/negotiations")
def negotiations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Negotiation).filter(Negotiation.user_id == user.id).order_by(Negotiation.id.desc()).all()
    return [
        {
            "id": x.id, "loan_id": x.loan_id,
            "settlement_percent": x.settlement_percent,
            "result": x.result, "created_at": x.created_at
        } for x in rows
    ]
