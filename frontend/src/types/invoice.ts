export type InvoiceStatus = "draft" | "sent" | "paid" | "overdue" | "cancelled";

export interface InvoiceItem {
  id: string;
  service_type_id: string | null;
  description: string;
  quantity: string;
  unit_price: string;
  total: string;
  sort_order: number;
}

export interface PaymentSummary {
  id: string;
  amount: string;
  payment_date: string;
  payment_method: string;
}

export interface Invoice {
  id: string;
  property_id: string;
  property_name: string;
  client_name: string | null;
  invoice_number: string;
  status: InvoiceStatus;
  period_start: string | null;
  period_end: string | null;
  subtotal: string;
  discount: string;
  tax: string;
  total: string;
  issue_date: string;
  due_date: string;
  paid_date: string | null;
  notes: string | null;
  items: InvoiceItem[];
  payments: PaymentSummary[];
  created_at: string;
  updated_at: string | null;
}

export interface InvoiceListItem {
  id: string;
  property_id: string;
  property_name: string;
  parent_property_name: string | null;
  client_name: string | null;
  invoice_number: string;
  status: InvoiceStatus;
  total: string;
  issue_date: string;
  due_date: string;
  paid_date: string | null;
  created_at: string;
}

export interface InvoiceItemPayload {
  service_type_id?: string | null;
  description: string;
  quantity: number;
  unit_price: number;
  sort_order: number;
}

export interface CreateInvoicePayload {
  property_id: string;
  issue_date: string;
  due_date: string;
  period_start?: string | null;
  period_end?: string | null;
  discount?: number;
  tax?: number;
  notes?: string | null;
  items: InvoiceItemPayload[];
}

export interface UpdateInvoicePayload {
  status?: string;
  issue_date?: string;
  due_date?: string;
  discount?: number;
  tax?: number;
  notes?: string | null;
  paid_date?: string | null;
}

export interface GenerateInvoicesPayload {
  property_id: string;
  issue_date: string;
  due_date: string;
  period_start?: string | null;
  period_end?: string | null;
  discount?: number;
  tax?: number;
  notes?: string | null;
}
