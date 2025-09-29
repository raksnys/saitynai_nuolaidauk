import { apiClient } from "../../../context/apiClient";

const BASE_URL = "/debts";

export type Debt = {
  id: number;
  type: string;
  amount: number;
  description: string;
  is_paid: boolean;
  is_confirmed?: boolean;
  owner?: number;
  debtee?: number;
  created_at?: string;
  updated_at?: string;
  paid_at?: string | null;
};

export async function listMyDebts(paid?: boolean): Promise<Debt[]> {
  let url = `${BASE_URL}/list-my-debts/`;
  if (typeof paid === "boolean") {
    url += `?paid=${paid}`;
  }
  const res = await apiClient(url);
  if (!res.ok) throw new Error("Failed to fetch debts");
  return await res.json();
}

export async function listCreatedDebts(confirmed?: boolean): Promise<Debt[]> {
  let url = `${BASE_URL}/list-created-debts/`;
  if (typeof confirmed === "boolean") {
    url += `?confirmed=${confirmed}`;
  }
  const res = await apiClient(url);
  if (!res.ok) throw new Error("Failed to fetch created debts");
  return await res.json();
}

export async function payDebt(id: number): Promise<void> {
  const res = await apiClient(`${BASE_URL}/${id}/pay/`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to pay debt");
}

export async function confirmDebt(id: number): Promise<void> {
  const res = await apiClient(`${BASE_URL}/${id}/confirm/`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to confirm debt");
}

export async function getDebt(id: number): Promise<Debt> {
  const res = await apiClient(`${BASE_URL}/${id}/`);
  if (!res.ok) throw new Error("Failed to fetch debt");
  return await res.json();
}

export async function listDebts(): Promise<Debt[]> {
  const res = await apiClient(`${BASE_URL}/`);
  if (!res.ok) throw new Error("Failed to fetch debts");
  return await res.json();
}

export async function createDebt(data: Partial<Debt>): Promise<Debt> {
  const res = await apiClient(`${BASE_URL}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create debt");
  return await res.json();
}

export async function updateDebt(id: number, data: Partial<Debt>): Promise<Debt> {
  const res = await apiClient(`${BASE_URL}/${id}/`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update debt");
  return await res.json();
}

export async function deleteDebt(id: number): Promise<void> {
  const res = await apiClient(`${BASE_URL}/${id}/`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete debt");
}

export async function markDebtUnpaid(debtId: number): Promise<void> {
  const res = await apiClient(`${BASE_URL}/mark_unpaid/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ debt_id: debtId }),
  });
  if (!res.ok) throw new Error("Failed to mark debt as unpaid");
}

export async function listUsers(): Promise<{ id: number; name: string }[]> {
  const res = await apiClient(`/list`, { method: "GET" });
  if (!res.ok) throw new Error("Failed to fetch users");
  return await res.json();
}

export async function getCurrentUser(): Promise<{ id: number; name: string }> {
  const res = await apiClient(`/user`, { method: "GET" });
  if (!res.ok) throw new Error("Failed to fetch current user");
  return await res.json();
}