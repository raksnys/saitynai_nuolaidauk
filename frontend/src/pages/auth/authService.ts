const BASE_URL = import.meta.env.VITE_API_URL;

export async function login(email: string, password: string) {
  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    throw new Error("Login failed");
  }
  return await response.json();
}

export async function register(name: string, email: string, password: string) {
  const response = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ name, email, password }),
  });
  if (!response.ok) {
    throw new Error("Registration failed");
  }
  return await response.json();
}