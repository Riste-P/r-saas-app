import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useDeleteServiceType } from "@/hooks/useServiceTypes";
import type { ServiceType } from "@/types";

interface DeleteServiceTypeDialogProps {
  serviceType: ServiceType | null;
  onClose: () => void;
}

export function DeleteServiceTypeDialog({
  serviceType,
  onClose,
}: DeleteServiceTypeDialogProps) {
  const deleteMutation = useDeleteServiceType({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={serviceType !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
      title="Delete Service Type"
      description={
        <>
          Are you sure you want to delete{" "}
          <strong>{serviceType?.name}</strong>? This action cannot be undone.
        </>
      }
      isPending={deleteMutation.isPending}
      onConfirm={() => {
        if (serviceType) deleteMutation.mutate(serviceType.id);
      }}
    />
  );
}
