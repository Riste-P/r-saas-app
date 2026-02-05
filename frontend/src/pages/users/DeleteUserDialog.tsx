import { ConfirmDeleteDialog } from "@/components/ConfirmDeleteDialog";
import { useDeleteUser } from "@/hooks/useUsers";
import type { UserListItem } from "@/types";

interface DeleteUserDialogProps {
  user: UserListItem | null;
  onClose: () => void;
}

export function DeleteUserDialog({ user, onClose }: DeleteUserDialogProps) {
  const deleteMutation = useDeleteUser({ onSuccess: onClose });

  return (
    <ConfirmDeleteDialog
      open={user !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
      title="Delete User"
      description={
        <>
          Are you sure you want to delete{" "}
          <strong>{user?.email}</strong>? This action cannot be undone.
        </>
      }
      isPending={deleteMutation.isPending}
      onConfirm={() => {
        if (user) deleteMutation.mutate(user.id);
      }}
    />
  );
}
