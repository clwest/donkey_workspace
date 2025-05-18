const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export default async function apiFetch(url, options = {}) {
  const defaultHeaders = options.body
    ? { "Content-Type": "application/json" }
    : {};

  const res = await fetch(API_URL + url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...(options.headers || {}),
    },
    body:
      options.body && typeof options.body !== "string"
        ? JSON.stringify(options.body)
        : options.body,
    credentials: "include",
  });

  if (!res.ok) {
    console.error(`API Error ${res.status}: ${res.statusText}`);
    throw new Error("API Error");
  }

  return res.json();
}
