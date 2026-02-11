export interface Client {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  billing_address: string | null;
  notes: string | null;
  is_active: boolean;
  property_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface ClientCreatePayload {
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  billing_address?: string;
  notes?: string;
}

export interface ClientUpdatePayload {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
  billing_address?: string;
  notes?: string;
  is_active?: boolean;
}
