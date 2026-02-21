import api from "@/lib/api";
import type { Payment, CreatePaymentPayload, PaginatedResponse } from "@/types";

export async function getPayments(params?: {
  invoice_id?: string;
}): Promise<PaginatedResponse<Payment>> {
  const res = await api.get<PaginatedResponse<Payment>>("/payments", { params });
  return res.data;
}

export async function createPayment(payload: CreatePaymentPayload): Promise<Payment> {
  const res = await api.post<Payment>("/payments", payload);
  return res.data;
}

export async function deletePayment(id: string): Promise<void> {
  await api.delete(`/payments/${id}`);
}
