export interface UserListItem {
  id: string;
  email: string;
  is_active: boolean;
  role: string;
  tenant_id: string;
  tenant_name: string;
  created_at: string;
}

export interface UserCreatePayload {
  email: string;
  password: string;
  role_id: number;
  tenant_id?: string;
}

export interface UserUpdatePayload {
  role_id: number;
  is_active: boolean;
}
