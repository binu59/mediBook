const BASE = "/api/appointments";

async function request(url, options = {}) {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    // FastAPI returns a string for HTTP errors and a list for validation errors
    throw new Error(Array.isArray(detail) ? detail.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join("; ") : detail || "Request failed");
  }
  return data;
}

export const api = {
  list: (filters) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => v && params.set(k, v));
    return request(`${BASE}?${params}`);
  },
  create: (body) => request(BASE, { method: "POST", body: JSON.stringify(body) }),
  update: (id, body) => request(`${BASE}/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  cancel: (id) => request(`${BASE}/${id}/cancel`, { method: "POST" }),
};