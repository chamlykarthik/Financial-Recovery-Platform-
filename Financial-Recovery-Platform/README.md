# FinRelief AI — Financial Recovery Platform

A runnable MVP based on the supplied AI Powered Debt Relief & Financial Recovery Platform architecture.

## Stack
- Frontend: React + Vite
- Backend: FastAPI + Python
- Database: SQLite + SQLAlchemy
- Authentication: JWT
- AI: Google Gemini API (optional) with deterministic fallback
- API: REST/JSON

## Modules
1. User registration/login
2. Financial dashboard
3. Loan management
4. Financial health profile
5. Settlement prediction
6. AI negotiation letter generation
7. AI negotiation history
8. JWT-protected APIs

## Run backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
# Linux/macOS: cp .env.example .env

uvicorn app.main:app --reload --port 8000
```

Backend: http://localhost:8000
Swagger: http://localhost:8000/docs

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

Optional Gemini:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Without a Gemini key, the app uses a deterministic fallback for the negotiation letter.

> Educational MVP only. Settlement estimates are illustrative and are not financial or legal advice.
