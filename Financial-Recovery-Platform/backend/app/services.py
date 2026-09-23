from .config import settings

def calculate_settlement(loan, profile):
    outstanding = max(loan.outstanding, 0)
    income = max(profile.monthly_income, 0)
    expenses = max(profile.monthly_expenses, 0)
    surplus = max(income - expenses, 0)

    overdue_factor = min(loan.days_overdue / 180, 0.30)
    affordability_factor = 0.20 if surplus <= 0 else min(surplus / max(outstanding, 1), 0.35)
    hardship_discount = min(0.35, overdue_factor + (0.15 if affordability_factor < 0.08 else 0))
    settlement_percent = max(45.0, min(90.0, 100.0 - hardship_discount * 100))
    suggested_amount = round(outstanding * settlement_percent / 100, 2)

    return {
        "loan_id": loan.id,
        "outstanding": round(outstanding, 2),
        "monthly_surplus": round(surplus, 2),
        "settlement_percent": round(settlement_percent, 1),
        "suggested_settlement": suggested_amount,
        "risk_band": "HIGH" if loan.days_overdue >= 90 else ("MEDIUM" if loan.days_overdue >= 30 else "LOW"),
        "explanation": "Illustrative estimate based on overdue days and reported affordability."
    }

def fallback_letter(user, loan, profile, tone="professional", extra_context=""):
    result = calculate_settlement(loan, profile)
    amount = result["suggested_settlement"]
    style = "respectfully and clearly" if tone == "professional" else "in a concise and practical manner"
    context = f"\nAdditional context: {extra_context}" if extra_context else ""
    return (
        f"Subject: Request for a Sustainable Settlement Arrangement\n\n"
        f"Dear {loan.lender} Team,\n\n"
        f"I am {user.name}, and I am writing to request a review of my outstanding loan account. "
        f"Due to my current financial circumstances, I would like to discuss a mutually acceptable "
        f"settlement or repayment arrangement.\n\n"
        f"My current outstanding amount is approximately ₹{loan.outstanding:,.2f}. "
        f"Based on my current affordability, I would like to propose an initial settlement amount "
        f"of approximately ₹{amount:,.2f}, subject to your review and approval.\n\n"
        f"I would appreciate the opportunity to discuss the available options {style}. "
        f"Please let me know the documents and terms required to evaluate this request.{context}\n\n"
        f"Thank you for your consideration.\n\n"
        f"Sincerely,\n{name}"
    )

def gemini_letter(user, loan, profile, tone, extra_context):
    if not settings.GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        prompt = f'''
Create a professional debt-settlement negotiation letter.
Do not claim legal rights or guaranteed outcomes.
Use only these supplied facts:
Borrower: {user.name}
Lender: {loan.lender}
Loan type: {loan.loan_type}
Outstanding: {loan.outstanding}
Monthly EMI: {loan.monthly_emi}
Days overdue: {loan.days_overdue}
Monthly income: {profile.monthly_income}
Monthly expenses: {profile.monthly_expenses}
Tone: {tone}
Additional context: {extra_context}
Keep it concise and factual.
'''
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None
