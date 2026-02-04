import api from "@/lib/api";
import type { Tenant, TenantCreatePayload, TenantUpdatePayload, PaginatedResponse } from "@/types";

export async function getTenants(): Promise<PaginatedResponse<Tenant>> {
  const res = await api.get<PaginatedResponse<Tenant>>("/admin/tenants");
  return res.data;
}

export async function createTenant(payload: TenantCreatePayload): Promise<Tenant> {
  const res = await api.post<Tenant>("/admin/tenants", payload);
  return res.data;
}

export async function updateTenant(id: string, payload: TenantUpdatePayload): Promise<Tenant> {
  const res = await api.patch<Tenant>(`/admin/tenants/${id}`, payload);
  return res.data;
}
