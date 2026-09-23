FinRelief AI — Financial Recovery Platform
A runnable MVP based on the supplied AI Powered Debt Relief & Financial Recovery Platform architecture.

Stack
Frontend: React + Vite
Backend: FastAPI + Python
Database: SQLite + SQLAlchemy
Authentication: JWT
AI: Google Gemini API (optional) with deterministic fallback
API: REST/JSON
Modules
User registration/login
Financial dashboard
Loan management
Financial health profile
Settlement prediction
AI negotiation letter generation
AI negotiation history
JWT-protected APIs
Run backend
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
Backend: http://localhost:8000 Swagger: http://localhost:8000/docs

Run frontend
cd frontend
npm install
npm run dev
Frontend: http://localhost:5173

Optional Gemini:

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
Without a Gemini key, the app uses a deterministic fallback for the negotiation letter.

Educational MVP only. Settlement estimates are illustrative and are not financial or legal advice.
