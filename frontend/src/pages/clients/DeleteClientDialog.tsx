import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useDeleteClient } from "@/hooks/useClients";
import type { Client } from "@/types";

interface DeleteClientDialogProps {
  client: Client | null;
  onClose: () => void;
}

export function DeleteClientDialog({ client, onClose }: DeleteClientDialogProps) {
  const deleteMutation = useDeleteClient({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={client !== null}
      onOpenChange={(open) => { if (!open) onClose(); }}
      title="Delete Client"
      description={
        <>
          Are you sure you want to delete <strong>{client?.name}</strong>?
          All associated properties will also be deleted. This action cannot be undone.
        </>
      }
      isPending={deleteMutation.isPending}
      onConfirm={() => { if (client) deleteMutation.mutate(client.id); }}
    />
  );
}
