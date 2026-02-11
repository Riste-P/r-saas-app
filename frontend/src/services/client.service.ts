import api from "@/lib/api";
import type {
  Client,
  ClientCreatePayload,
  ClientUpdatePayload,
  PaginatedResponse,
} from "@/types";

export async function getClients(): Promise<PaginatedResponse<Client>> {
  const res = await api.get<PaginatedResponse<Client>>("/clients");
  return res.data;
}

export async function getClient(id: string): Promise<Client> {
  const res = await api.get<Client>(`/clients/${id}`);
  return res.data;
}

export async function createClient(payload: ClientCreatePayload): Promise<Client> {
  const res = await api.post<Client>("/clients", payload);
  return res.data;
}

export async function updateClient(id: string, payload: ClientUpdatePayload): Promise<Client> {
  const res = await api.patch<Client>(`/clients/${id}`, payload);
  return res.data;
}

export async function deleteClient(id: string): Promise<void> {
  await api.delete(`/clients/${id}`);
}
