export interface ChecklistItem {
  id: string;
  name: string;
  description: string | null;
  sort_order: number;
}

export interface ServiceType {
  id: string;
  name: string;
  description: string | null;
  base_price: string;
  estimated_duration_minutes: number;
  is_active: boolean;
  checklist_items: ChecklistItem[];
  created_at: string;
  updated_at: string | null;
}

export interface ServiceTypeCreatePayload {
  name: string;
  description?: string;
  base_price: number;
  estimated_duration_minutes: number;
  checklist_items?: { name: string; description?: string; sort_order: number }[];
}

export interface ServiceTypeUpdatePayload {
  name?: string;
  description?: string;
  base_price?: number;
  estimated_duration_minutes?: number;
  is_active?: boolean;
}

export interface ChecklistUpdatePayload {
  items: { name: string; description?: string; sort_order: number }[];
}
