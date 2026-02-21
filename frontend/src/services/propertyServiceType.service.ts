import api from "@/lib/api";
import type {
  PropertyServiceType,
  EffectiveService,
  AssignServicePayload,
  BulkAssignServicesPayload,
  UpdatePropertyServicePayload,
} from "@/types";

export async function getAssignments(propertyId: string): Promise<PropertyServiceType[]> {
  const res = await api.get<PropertyServiceType[]>("/property-service-types", {
    params: { property_id: propertyId },
  });
  return res.data;
}

export async function getEffectiveServices(propertyId: string): Promise<EffectiveService[]> {
  const res = await api.get<EffectiveService[]>("/property-service-types/effective", {
    params: { property_id: propertyId },
  });
  return res.data;
}

export async function assignService(payload: AssignServicePayload): Promise<PropertyServiceType> {
  const res = await api.post<PropertyServiceType>("/property-service-types", payload);
  return res.data;
}

export async function bulkAssignServices(payload: BulkAssignServicesPayload): Promise<PropertyServiceType[]> {
  const res = await api.post<PropertyServiceType[]>("/property-service-types/bulk", payload);
  return res.data;
}

export async function updateAssignment(
  id: string,
  payload: UpdatePropertyServicePayload,
): Promise<PropertyServiceType> {
  const res = await api.patch<PropertyServiceType>(`/property-service-types/${id}`, payload);
  return res.data;
}

export async function removeAssignment(id: string): Promise<void> {
  await api.delete(`/property-service-types/${id}`);
}
