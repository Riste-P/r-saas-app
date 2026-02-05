import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useDeleteTenant } from "@/hooks/useTenants";
import type { Tenant } from "@/types";

interface DeleteTenantDialogProps {
  tenant: Tenant | null;
  onClose: () => void;
}

export function DeleteTenantDialog({
  tenant,
  onClose,
}: DeleteTenantDialogProps) {
  const deleteMutation = useDeleteTenant({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={tenant !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
      title="Delete Tenant"
      description={
        <>
          Are you sure you want to delete tenant{" "}
          <strong>{tenant?.name}</strong>? This action cannot be undone. All
          users in this tenant will lose access.
        </>
      }
      isPending={deleteMutation.isPending}
      onConfirm={() => {
        if (tenant) deleteMutation.mutate(tenant.id);
      }}
    />
  );
}
