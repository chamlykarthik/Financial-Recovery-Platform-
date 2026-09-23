const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const token = localStorage.getItem("finrelief_token");
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

export const api = {
  register: (body) => request("/api/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body) => request("/api/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: () => request("/api/me"),
  dashboard: () => request("/api/dashboard"),
  loans: () => request("/api/loans"),
  addLoan: (body) => request("/api/loans", { method: "POST", body: JSON.stringify(body) }),
  deleteLoan: (id) => request(`/api/loans/${id}`, { method: "DELETE" }),
  profile: () => request("/api/profile"),
  updateProfile: (body) => request("/api/profile", { method: "PUT", body: JSON.stringify(body) }),
  predict: (loan_id) => request("/api/settlement/predict", { method: "POST", body: JSON.stringify({ loan_id }) }),
  negotiate: (body) => request("/api/negotiation/generate", { method: "POST", body: JSON.stringify(body) }),
  negotiations: () => request("/api/negotiations")
};
