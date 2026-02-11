export type PropertyType = "house" | "apartment" | "building" | "commercial";

export interface PropertySummary {
  id: string;
  name: string;
  property_type: PropertyType;
  address: string;
}

export interface Property {
  id: string;
  client_id: string;
  client_name: string;
  parent_property_id: string | null;
  property_type: PropertyType;
  name: string;
  address: string;
  city: string | null;
  postal_code: string | null;
  size_sqm: string | null;
  num_rooms: number | null;
  floor: string | null;
  access_instructions: string | null;
  key_code: string | null;
  contact_name: string | null;
  contact_phone: string | null;
  contact_email: string | null;
  is_active: boolean;
  child_properties: PropertySummary[];
  created_at: string;
  updated_at: string | null;
}

export interface PropertyCreatePayload {
  client_id: string;
  parent_property_id?: string;
  property_type: PropertyType;
  name: string;
  address: string;
  city?: string;
  postal_code?: string;
  size_sqm?: number;
  num_rooms?: number;
  floor?: string;
  access_instructions?: string;
  key_code?: string;
  contact_name?: string;
  contact_phone?: string;
  contact_email?: string;
}

export interface PropertyUpdatePayload {
  client_id?: string;
  parent_property_id?: string;
  property_type?: PropertyType;
  name?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  size_sqm?: number;
  num_rooms?: number;
  floor?: string;
  access_instructions?: string;
  key_code?: string;
  contact_name?: string;
  contact_phone?: string;
  contact_email?: string;
  is_active?: boolean;
}
