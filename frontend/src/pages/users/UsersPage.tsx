import { useState, useMemo } from "react";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/DataTable";
import { useAuthStore } from "@/stores/auth";
import { useUsersQuery } from "@/hooks/useUsers";
import { getUserColumns } from "./UserColumns";
import { CreateUserDialog } from "./CreateUserDialog";
import { EditUserDialog } from "./EditUserDialog";
import { DeleteUserDialog } from "./DeleteUserDialog";
import type { UserListItem } from "@/types";

export default function UsersPage() {
  const currentUser = useAuthStore((s) => s.user);
  const isSuperadmin = currentUser?.role === "superadmin";

  const [createOpen, setCreateOpen] = useState(false);
  const [editUser, setEditUser] = useState<UserListItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<UserListItem | null>(null);

  const { data: users = [], isLoading } = useUsersQuery();

  const columns = useMemo(
    () =>
      getUserColumns({
        isSuperadmin,
        onEdit: setEditUser,
        onDelete: setDeleteTarget,
      }),
    [isSuperadmin]
  );

  const table = useReactTable({
    data: users,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) {
    return <p className="text-muted-foreground">Loading users...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Users</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {isSuperadmin
              ? "Manage users across all tenants"
              : "Manage users in your tenant"}
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>Create User</Button>
      </div>

      <DataTable
        table={table}
        columnCount={columns.length}
        emptyMessage="No users found."
      />

      <CreateUserDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        isSuperadmin={isSuperadmin}
      />
      <EditUserDialog
        user={editUser}
        onClose={() => setEditUser(null)}
        isSuperadmin={isSuperadmin}
      />
      <DeleteUserDialog
        user={deleteTarget}
        onClose={() => setDeleteTarget(null)}
      />
    </div>
  );
}
