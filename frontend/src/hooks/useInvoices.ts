import { useQuery, useMutation, useQueryClient, skipToken } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as invoiceService from "@/services/invoice.service";
import type { CreateInvoicePayload, UpdateInvoicePayload, GenerateInvoicesPayload, InvoiceStatus } from "@/types";

const INVOICES_KEY = ["invoices"] as const;
const INVOICE_DETAIL_KEY = ["invoice"] as const;

export function useInvoicesQuery(params?: {
  status?: string;
  property_id?: string;
  client_id?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: [...INVOICES_KEY, params],
    queryFn: () => invoiceService.getInvoices(params),
    select: (data) => data.items,
  });
}

export function useInvoiceQuery(id: string | null) {
  return useQuery({
    queryKey: [...INVOICE_DETAIL_KEY, id],
    queryFn: id ? () => invoiceService.getInvoice(id) : skipToken,
  });
}

export function useCreateInvoice(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateInvoicePayload) => invoiceService.createInvoice(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      toast.success("Invoice created successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to create invoice")),
  });
}

export function useGenerateInvoices(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: GenerateInvoicesPayload) => invoiceService.generateInvoices(payload),
    onSuccess: (invoices) => {
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      toast.success(`Generated ${invoices.length} invoice${invoices.length !== 1 ? "s" : ""}`);
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to generate invoices")),
  });
}

export function useUpdateInvoice(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & UpdateInvoicePayload) =>
      invoiceService.updateInvoice(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      qc.invalidateQueries({ queryKey: INVOICE_DETAIL_KEY });
      toast.success("Invoice updated successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update invoice")),
  });
}

export function useDeleteInvoice(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => invoiceService.deleteInvoice(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      toast.success("Invoice deleted successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to delete invoice")),
  });
}

export function useBulkUpdateStatus(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ ids, status }: { ids: string[]; status: InvoiceStatus }) =>
      invoiceService.bulkUpdateStatus(ids, status),
    onSuccess: ({ total, failed }) => {
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      qc.invalidateQueries({ queryKey: INVOICE_DETAIL_KEY });
      const succeeded = total - failed;
      if (failed === 0) {
        toast.success(`Updated ${succeeded} invoice${succeeded !== 1 ? "s" : ""}`);
      } else {
        toast.warning(`Updated ${succeeded} of ${total} invoices (${failed} failed)`);
      }
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update invoices")),
  });
}

export function useBulkDeleteInvoices(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ids: string[]) => invoiceService.bulkDelete(ids),
    onSuccess: ({ total, failed }) => {
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      const succeeded = total - failed;
      if (failed === 0) {
        toast.success(`Deleted ${succeeded} invoice${succeeded !== 1 ? "s" : ""}`);
      } else {
        toast.warning(`Deleted ${succeeded} of ${total} invoices (${failed} failed)`);
      }
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to delete invoices")),
  });
}

export function useMarkOverdue(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => invoiceService.markOverdue(),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: INVOICES_KEY });
      if (data.marked_overdue > 0) {
        toast.success(`Marked ${data.marked_overdue} invoice${data.marked_overdue !== 1 ? "s" : ""} as overdue`);
      } else {
        toast.info("No invoices to mark as overdue");
      }
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to mark overdue")),
  });
}
