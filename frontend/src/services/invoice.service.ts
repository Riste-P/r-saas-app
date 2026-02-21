import api from "@/lib/api";
import type {
  Invoice,
  InvoiceListItem,
  CreateInvoicePayload,
  UpdateInvoicePayload,
  GenerateInvoicesPayload,
  PaginatedResponse,
} from "@/types";

export async function getInvoices(params?: {
  status?: string;
  property_id?: string;
  client_id?: string;
  search?: string;
}): Promise<PaginatedResponse<InvoiceListItem>> {
  const res = await api.get<PaginatedResponse<InvoiceListItem>>("/invoices", { params });
  return res.data;
}

export async function getInvoice(id: string): Promise<Invoice> {
  const res = await api.get<Invoice>(`/invoices/${id}`);
  return res.data;
}

export async function createInvoice(payload: CreateInvoicePayload): Promise<Invoice> {
  const res = await api.post<Invoice>("/invoices", payload);
  return res.data;
}

export async function generateInvoices(payload: GenerateInvoicesPayload): Promise<Invoice[]> {
  const res = await api.post<Invoice[]>("/invoices/generate", payload);
  return res.data;
}

export async function updateInvoice(id: string, payload: UpdateInvoicePayload): Promise<Invoice> {
  const res = await api.patch<Invoice>(`/invoices/${id}`, payload);
  return res.data;
}

export async function deleteInvoice(id: string): Promise<void> {
  await api.delete(`/invoices/${id}`);
}

export async function markOverdue(): Promise<{ marked_overdue: number }> {
  const res = await api.post<{ marked_overdue: number }>("/invoices/mark-overdue");
  return res.data;
}

export async function bulkUpdateStatus(ids: string[], status: string) {
  const results = await Promise.allSettled(
    ids.map((id) => updateInvoice(id, { status }))
  );
  const failed = results.filter((r) => r.status === "rejected").length;
  return { total: ids.length, failed };
}

export async function bulkDelete(ids: string[]) {
  const results = await Promise.allSettled(
    ids.map((id) => deleteInvoice(id))
  );
  const failed = results.filter((r) => r.status === "rejected").length;
  return { total: ids.length, failed };
}
