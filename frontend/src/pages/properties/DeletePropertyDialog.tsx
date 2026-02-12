import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useDeleteProperty, usePropertyQuery } from "@/hooks/useProperties";

interface DeletePropertyDialogProps {
  propertyId: string | null;
  onClose: () => void;
}

export function DeletePropertyDialog({ propertyId, onClose }: DeletePropertyDialogProps) {
  const { data: property } = usePropertyQuery(propertyId);
  const deleteMutation = useDeleteProperty({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={propertyId !== null}
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
      onConfirm={() => { if (propertyId) deleteMutation.mutate(propertyId); }}
    />
  );
}
