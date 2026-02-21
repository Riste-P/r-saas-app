import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useDeletePayment } from "@/hooks/usePayments";

interface DeletePaymentDialogProps {
  paymentId: string | null;
  onClose: () => void;
}

export function DeletePaymentDialog({ paymentId, onClose }: DeletePaymentDialogProps) {
  const deleteMutation = useDeletePayment({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={paymentId !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
      title="Delete Payment"
      description="Are you sure you want to delete this payment? The invoice status may revert."
      isPending={deleteMutation.isPending}
      onConfirm={() => {
        if (paymentId) deleteMutation.mutate(paymentId);
      }}
    />
  );
}
