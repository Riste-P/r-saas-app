import api from "@/lib/api";
import type { UserListItem, UserCreatePayload, UserUpdatePayload, PaginatedResponse } from "@/types";

export async function getUsers(): Promise<PaginatedResponse<UserListItem>> {
  const res = await api.get<PaginatedResponse<UserListItem>>("/admin/users");
  return res.data;
}

export async function createUser(payload: UserCreatePayload): Promise<UserListItem> {
  const res = await api.post<UserListItem>("/admin/users", payload);
  return res.data;
}

export async function updateUser(id: string, payload: UserUpdatePayload): Promise<UserListItem> {
  const res = await api.patch<UserListItem>(`/admin/users/${id}`, payload);
  return res.data;
}
