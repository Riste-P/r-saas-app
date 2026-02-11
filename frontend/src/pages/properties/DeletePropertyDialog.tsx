import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useDeleteProperty } from "@/hooks/useProperties";
import type { Property } from "@/types";

interface DeletePropertyDialogProps {
  property: Property | null;
  onClose: () => void;
}

export function DeletePropertyDialog({ property, onClose }: DeletePropertyDialogProps) {
  const deleteMutation = useDeleteProperty({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={property !== null}
      onOpenChange={(open) => { if (!open) onClose(); }}
      title="Delete Property"
      description={
        <>
          Are you sure you want to delete <strong>{property?.name}</strong>?
          {(property?.child_properties?.length ?? 0) > 0 &&
            " All child properties (apartments) will also be deleted."}
          {" "}This action cannot be undone.
        </>
      }
      isPending={deleteMutation.isPending}
      onConfirm={() => { if (property) deleteMutation.mutate(property.id); }}
    />
  );
}
