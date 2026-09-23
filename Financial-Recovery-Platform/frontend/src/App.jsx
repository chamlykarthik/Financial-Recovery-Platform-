import React, { useEffect, useState } from "react";
import { api } from "./api";
import { LayoutDashboard, WalletCards, BrainCircuit, History, LogOut, Plus, Trash2, Activity, ShieldCheck } from "lucide-react";

const money = (n) => `₹${Number(n || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const submit = async (e) => {
    e.preventDefault(); setError("");
    try {
      const result = mode === "login" ? await api.login({ email: form.email, password: form.password }) : await api.register(form);
      localStorage.setItem("finrelief_token", result.access_token); onLogin();
    } catch (err) { setError(err.message); }
  };
  return <div className="auth-shell"><div className="auth-card">
    <div className="brand-mark">FR</div><h1>FinRelief AI</h1><p className="muted">AI-powered debt relief & financial recovery</p>
    <div className="tabs"><button className={mode==="login"?"active":""} onClick={()=>setMode("login")}>Login</button><button className={mode==="register"?"active":""} onClick={()=>setMode("register")}>Register</button></div>
    <form onSubmit={submit}>{mode==="register" && <input placeholder="Full name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required />}
      <input type="email" placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required />
      <input type="password" placeholder="Password (6+ characters)" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required />
      {error && <div className="error">{error}</div>}<button className="primary full">{mode==="login"?"Sign in":"Create account"}</button>
    </form>
  </div></div>;
}

function App() {
  const [authed,setAuthed]=useState(!!localStorage.getItem("finrelief_token")); const [user,setUser]=useState(null); const [page,setPage]=useState("dashboard");
  useEffect(()=>{if(authed) api.me().then(setUser).catch(()=>{localStorage.removeItem("finrelief_token");setAuthed(false)})},[authed]);
  if(!authed) return <Auth onLogin={()=>setAuthed(true)}/>;
  const logout=()=>{localStorage.removeItem("finrelief_token");setAuthed(false)};
  return <div className="app"><aside className="sidebar"><div className="logo"><div className="logo-icon">FR</div><div><b>FinRelief</b><span>AI</span></div></div>
    <nav><Nav icon={<LayoutDashboard/>} label="Dashboard" active={page==="dashboard"} onClick={()=>setPage("dashboard")}/><Nav icon={<WalletCards/>} label="Loans" active={page==="loans"} onClick={()=>setPage("loans")}/><Nav icon={<Activity/>} label="Financial Health" active={page==="health"} onClick={()=>setPage("health")}/><Nav icon={<BrainCircuit/>} label="AI Negotiation" active={page==="ai"} onClick={()=>setPage("ai")}/><Nav icon={<History/>} label="History" active={page==="history"} onClick={()=>setPage("history")}/></nav>
    <button className="logout" onClick={logout}><LogOut size={17}/> Logout</button></aside>
    <main className="content"><header><div><div className="eyebrow">FINANCIAL RECOVERY PLATFORM</div><h2>{page==="dashboard"?"Financial Dashboard":page.replace("-"," ")}</h2></div><div className="user-pill"><ShieldCheck size={16}/>{user?.name||"User"}</div></header>
      {page==="dashboard"&&<Dashboard/>}{page==="loans"&&<Loans/>}{page==="health"&&<Health/>}{page==="ai"&&<Negotiation/>}{page==="history"&&<HistoryPage/>}
    </main></div>;
}
function Nav({icon,label,active,onClick}){return <button className={`nav-item ${active?"active":""}`} onClick={onClick}>{icon}<span>{label}</span></button>}
function Dashboard(){const[data,setData]=useState(null),[loans,setLoans]=useState([]);useEffect(()=>{Promise.all([api.dashboard(),api.loans()]).then(([d,l])=>{setData(d);setLoans(l)})},[]);if(!data)return <Loading/>;return <>
  <section className="hero"><div><span className="badge">AI-ASSISTED</span><h1>Take control of your debt.</h1><p>Understand affordability, model settlements, and prepare structured negotiation requests.</p></div><div className="hero-score"><small>FINANCIAL HEALTH</small><strong>{data.financial_health}</strong></div></section>
  <div className="stats"><Stat title="Total outstanding" value={money(data.total_outstanding)}/><Stat title="Monthly EMI" value={money(data.total_emi)}/><Stat title="Monthly surplus" value={money(data.monthly_surplus)}/><Stat title="Active loans" value={data.loan_count}/></div>
  <section className="panel"><h3>Loan portfolio</h3><p className="muted">Your current obligations</p>{loans.length?loans.map(l=><LoanRow key={l.id} loan={l}/>):<Empty text="No loans added yet. Open Loans to add one."/>}</section></>}
function Stat({title,value}){return <div className="stat"><span>{title}</span><strong>{value}</strong></div>}
function LoanRow({loan,onDelete}){return <div className="loan-row"><div><b>{loan.lender}</b><span>{loan.loan_type} · {loan.days_overdue} days overdue</span></div><div><b>{money(loan.outstanding)}</b><span>EMI {money(loan.monthly_emi)}</span></div>{onDelete&&<button className="icon-btn danger" onClick={()=>onDelete(loan.id)}><Trash2 size={16}/></button>}</div>}
function Loans(){const[loans,setLoans]=useState([]);const[form,setForm]=useState({lender:"",loan_type:"Personal Loan",principal:"",outstanding:"",monthly_emi:"",interest_rate:"",days_overdue:"0"});const[error,setError]=useState("");const load=()=>api.loans().then(setLoans);useEffect(load,[]);const add=async e=>{e.preventDefault();setError("");try{await api.addLoan({...form,principal:+form.principal,outstanding:+form.outstanding,monthly_emi:+form.monthly_emi,interest_rate:+(form.interest_rate||0),days_overdue:+form.days_overdue});setForm({lender:"",loan_type:"Personal Loan",principal:"",outstanding:"",monthly_emi:"",interest_rate:"",days_overdue:"0"});load()}catch(err){setError(err.message)}};const remove=async id=>{await api.deleteLoan(id);load()};return <div className="grid-2"><section className="panel"><h3>Add loan</h3><p className="muted">Enter your current loan information.</p><form onSubmit={add} className="form-grid">
  <input placeholder="Lender" value={form.lender} onChange={e=>setForm({...form,lender:e.target.value})} required/><select value={form.loan_type} onChange={e=>setForm({...form,loan_type:e.target.value})}><option>Personal Loan</option><option>Credit Card</option><option>Education Loan</option><option>Auto Loan</option><option>Home Loan</option><option>Other</option></select>
  <input type="number" placeholder="Original principal" value={form.principal} onChange={e=>setForm({...form,principal:e.target.value})} required/><input type="number" placeholder="Outstanding amount" value={form.outstanding} onChange={e=>setForm({...form,outstanding:e.target.value})} required/>
  <input type="number" placeholder="Monthly EMI" value={form.monthly_emi} onChange={e=>setForm({...form,monthly_emi:e.target.value})} required/><input type="number" placeholder="Interest rate %" value={form.interest_rate} onChange={e=>setForm({...form,interest_rate:e.target.value})}/>
  <input type="number" placeholder="Days overdue" value={form.days_overdue} onChange={e=>setForm({...form,days_overdue:e.target.value})}/>{error&&<div className="error span-2">{error}</div>}<button className="primary span-2"><Plus size={17}/> Add loan</button>
</form></section><section className="panel"><h3>Your loans</h3>{loans.length?loans.map(l=><LoanRow key={l.id} loan={l} onDelete={remove}/>):<Empty text="No loans yet."/>}</section></div>}
function Health(){const[p,setP]=useState(null),[saved,setSaved]=useState("");useEffect(()=>api.profile().then(setP),[]);if(!p)return <Loading/>;const save=async e=>{e.preventDefault();await api.updateProfile({...p,monthly_income:+p.monthly_income,monthly_expenses:+p.monthly_expenses,dependents:+p.dependents,emergency_savings:+p.emergency_savings,credit_score:p.credit_score?+p.credit_score:null});setSaved("Saved successfully")};const surplus=+p.monthly_income-(+p.monthly_expenses);return <section className="panel narrow"><h3>Financial health profile</h3><p className="muted">This information powers affordability and settlement estimates.</p><form onSubmit={save} className="form-grid">
  {Object.entries({monthly_income:"Monthly income",monthly_expenses:"Monthly expenses",dependents:"Dependents",emergency_savings:"Emergency savings",credit_score:"Credit score (optional)"}).map(([key,label])=><label key={key}>{label}<input type="number" value={p[key]??""} onChange={e=>setP({...p,[key]:e.target.value})}/></label>)}
  <div className={`health-callout span-2 ${surplus>=0?"good":"bad"}`}><b>Monthly cash-flow: {money(surplus)}</b><span>{surplus>=0?"Reported income covers reported expenses.":"Reported expenses exceed reported income."}</span></div>{saved&&<div className="success span-2">{saved}</div>}<button className="primary span-2">Save profile</button>
</form></section>}
function Negotiation(){const[loans,setLoans]=useState([]),[loanId,setLoanId]=useState(""),[tone,setTone]=useState("professional"),[context,setContext]=useState(""),[result,setResult]=useState(null),[busy,setBusy]=useState(false);useEffect(()=>api.loans().then(l=>{setLoans(l);if(l[0])setLoanId(String(l[0].id))}),[]);const run=async()=>{setBusy(true);try{setResult(await api.negotiate({loan_id:+loanId,tone,extra_context:context}))}finally{setBusy(false)}};return <div className="grid-2"><section className="panel"><span className="badge">AI NEGOTIATION</span><h3>Generate a settlement request</h3><p className="muted">The AI uses supplied financial context and the platform's illustrative affordability calculation.</p><label>Loan<select value={loanId} onChange={e=>setLoanId(e.target.value)}>{loans.map(l=><option key={l.id} value={l.id}>{l.lender} — {money(l.outstanding)}</option>)}</select></label><label>Tone<select value={tone} onChange={e=>setTone(e.target.value)}><option>professional</option><option>concise</option><option>empathetic</option></select></label><label>Additional context<textarea rows="6" placeholder="Optional context..." value={context} onChange={e=>setContext(e.target.value)}/></label><button className="primary" disabled={!loanId||busy} onClick={run}>{busy?"Generating...":"Generate letter"}</button></section>
<section className="panel"><h3>Generated result</h3>{!result?<Empty text="Your generated negotiation letter will appear here."/>:<><div className="prediction"><b>Illustrative settlement</b><strong>{result.settlement.settlement_percent}%</strong><span>{money(result.settlement.suggested_settlement)}</span></div><pre className="letter">{result.letter}</pre></>}</section></div>}
function HistoryPage(){const[rows,setRows]=useState([]);useEffect(()=>api.negotiations().then(setRows),[]);return <section className="panel"><h3>AI negotiation history</h3><p className="muted">Previously generated requests saved to your account.</p>{rows.length?rows.map(x=><details className="history-item" key={x.id}><summary>Loan #{x.loan_id} · {x.settlement_percent}% · {new Date(x.created_at).toLocaleString()}</summary><pre className="letter">{x.result}</pre></details>):<Empty text="No negotiation history yet."/>}</section>}
function Empty({text}){return <div className="empty">{text}</div>} function Loading(){return <div className="empty">Loading...</div>}
export default App;
