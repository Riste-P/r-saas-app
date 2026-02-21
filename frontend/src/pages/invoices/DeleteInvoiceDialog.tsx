import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useInvoiceQuery, useDeleteInvoice } from "@/hooks/useInvoices";

interface DeleteInvoiceDialogProps {
  invoiceId: string | null;
  onClose: () => void;
}

export function DeleteInvoiceDialog({ invoiceId, onClose }: DeleteInvoiceDialogProps) {
  const { data: invoice } = useInvoiceQuery(invoiceId);
  const deleteMutation = useDeleteInvoice({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={invoiceId !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
      title="Delete Invoice"
      description={
        <>
          Are you sure you want to delete invoice{" "}
          <strong>{invoice?.invoice_number}</strong>? This action cannot be undone.
        </>
      }
      isPending={deleteMutation.isPending}
      onConfirm={() => {
        if (invoiceId) deleteMutation.mutate(invoiceId);
      }}
    />
  );
}
