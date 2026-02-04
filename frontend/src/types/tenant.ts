export interface Tenant {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
}

export interface TenantCreatePayload {
  name: string;
  slug: string;
}

export interface TenantUpdatePayload {
  name: string;
  is_active: boolean;
}
