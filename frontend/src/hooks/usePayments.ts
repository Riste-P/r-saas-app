import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as paymentService from "@/services/payment.service";
import type { CreatePaymentPayload } from "@/types";

const PAYMENTS_KEY = ["payments"] as const;
const INVOICES_KEY = ["invoices"] as const;
const INVOICE_DETAIL_KEY = ["invoice"] as const;

export function usePaymentsQuery(params?: { invoice_id?: string }) {
  return useQuery({
    queryKey: [...PAYMENTS_KEY, params],
    queryFn: () => paymentService.getPayments(params),
    select: (data) => data.items,
  });
}

export function useCreatePayment(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreatePaymentPayload) => paymentService.createPayment(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PAYMENTS_KEY });
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      qc.invalidateQueries({ queryKey: INVOICE_DETAIL_KEY });
      toast.success("Payment recorded successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to record payment")),
  });
}

export function useDeletePayment(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => paymentService.deletePayment(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PAYMENTS_KEY });
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      qc.invalidateQueries({ queryKey: INVOICE_DETAIL_KEY });
      toast.success("Payment deleted successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to delete payment")),
  });
}
