export type PropertyType = "house" | "apartment" | "building" | "commercial";

export interface ServiceBadge {
  service_type_name: string;
  effective_price: string;
  is_active: boolean;
}

export interface PropertySummary {
  id: string;
  name: string;
  property_type: PropertyType;
  address: string | null;
  client_name: string | null;
  is_active: boolean;
  services: ServiceBadge[];
}

export interface Property {
  id: string;
  client_id: string | null;
  client_name: string | null;
  parent_property_id: string | null;
  parent_property_name: string | null;
  property_type: PropertyType;
  name: string;
  address: string | null;
  city: string | null;
  notes: string | null;
  is_active: boolean;
  child_properties: PropertySummary[];
  services: ServiceBadge[];
  created_at: string;
  updated_at: string | null;
}

export interface PropertyCreatePayload {
  client_id?: string;
  parent_property_id?: string;
  property_type: PropertyType;
  name: string;
  address?: string;
  city?: string;
  notes?: string;
  number_of_apartments?: number;
}

export interface PropertyUpdatePayload {
  client_id?: string | null;
  parent_property_id?: string | null;
  property_type?: PropertyType;
  name?: string;
  address?: string;
  city?: string;
  notes?: string;
  is_active?: boolean;
}
