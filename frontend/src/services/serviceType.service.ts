import api from "@/lib/api";
import type {
  ServiceType,
  ServiceTypeCreatePayload,
  ServiceTypeUpdatePayload,
  ChecklistUpdatePayload,
  PaginatedResponse,
} from "@/types";

export async function getServiceTypes(): Promise<PaginatedResponse<ServiceType>> {
  const res = await api.get<PaginatedResponse<ServiceType>>("/service-types");
  return res.data;
}

export async function getServiceType(id: string): Promise<ServiceType> {
  const res = await api.get<ServiceType>(`/service-types/${id}`);
  return res.data;
}

export async function createServiceType(payload: ServiceTypeCreatePayload): Promise<ServiceType> {
  const res = await api.post<ServiceType>("/service-types", payload);
  return res.data;
}

export async function updateServiceType(id: string, payload: ServiceTypeUpdatePayload): Promise<ServiceType> {
  const res = await api.patch<ServiceType>(`/service-types/${id}`, payload);
  return res.data;
}

export async function updateChecklist(id: string, payload: ChecklistUpdatePayload): Promise<ServiceType> {
  const res = await api.put<ServiceType>(`/service-types/${id}/checklist`, payload);
  return res.data;
}

export async function deleteServiceType(id: string): Promise<void> {
  await api.delete(`/service-types/${id}`);
}
