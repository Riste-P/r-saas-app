export interface PropertyServiceType {
  id: string;
  property_id: string;
  service_type_id: string;
  service_type_name: string;
  custom_price: string | null;
  effective_price: string;
  is_active: boolean;
  is_inherited: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface EffectiveService {
  service_type_id: string;
  service_type_name: string;
  effective_price: string;
  is_active: boolean;
  is_inherited: boolean;
  override_id: string | null;
}

export interface AssignServicePayload {
  property_id: string;
  service_type_id: string;
  custom_price?: number | null;
  is_active?: boolean;
}

export interface BulkAssignServicesPayload {
  property_id: string;
  service_type_ids: string[];
}

export interface UpdatePropertyServicePayload {
  custom_price?: number | null;
  is_active?: boolean;
}
