import api from "@/lib/api";
import type {
  Property,
  PropertyCreatePayload,
  PropertyUpdatePayload,
  PaginatedResponse,
} from "@/types";

export async function getProperties(params?: {
  client_id?: string;
  property_type?: string;
  parent_property_id?: string;
}): Promise<PaginatedResponse<Property>> {
  const res = await api.get<PaginatedResponse<Property>>("/properties", { params });
  return res.data;
}

export async function getProperty(id: string): Promise<Property> {
  const res = await api.get<Property>(`/properties/${id}`);
  return res.data;
}

export async function createProperty(payload: PropertyCreatePayload): Promise<Property> {
  const res = await api.post<Property>("/properties", payload);
  return res.data;
}

export async function updateProperty(id: string, payload: PropertyUpdatePayload): Promise<Property> {
  const res = await api.patch<Property>(`/properties/${id}`, payload);
  return res.data;
}

export async function deleteProperty(id: string): Promise<void> {
  await api.delete(`/properties/${id}`);
}
