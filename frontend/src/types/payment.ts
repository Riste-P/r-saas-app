export interface Payment {
  id: string;
  invoice_id: string;
  invoice_number: string;
  amount: string;
  payment_date: string;
  payment_method: string;
  reference: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface CreatePaymentPayload {
  invoice_id: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference?: string | null;
  notes?: string | null;
}
