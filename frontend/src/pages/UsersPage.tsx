import { useState } from "react";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/stores/auth";
import { useUsersQuery, useCreateUser, useUpdateUser } from "@/hooks/useUsers";
import { useTenantsQuery } from "@/hooks/useTenants";
import type { UserListItem } from "@/types";

const columnHelper = createColumnHelper<UserListItem>();

export default function UsersPage() {
  const currentUser = useAuthStore((s) => s.user);
  const isSuperadmin = currentUser?.role === "superadmin";

  const [createOpen, setCreateOpen] = useState(false);
  const [editUser, setEditUser] = useState<UserListItem | null>(null);
  const [editRoleId, setEditRoleId] = useState("3");
  const [editActive, setEditActive] = useState(true);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRoleId, setNewRoleId] = useState("3");
  const [newTenantId, setNewTenantId] = useState("");
  const [tenantError, setTenantError] = useState("");

  const { data: users = [], isLoading } = useUsersQuery();
  const { data: tenants = [] } = useTenantsQuery(isSuperadmin);

  const createMutation = useCreateUser({
    onSuccess: () => {
      setCreateOpen(false);
      setNewEmail("");
      setNewPassword("");
      setNewRoleId("3");
      setNewTenantId("");
      setTenantError("");
    },
  });

  const updateMutation = useUpdateUser({
    onSuccess: () => setEditUser(null),
  });

  function openEdit(user: UserListItem) {
    setEditUser(user);
    setEditRoleId(roleNameToId(user.role));
    setEditActive(user.is_active);
  }

  const columns = [
    columnHelper.accessor("email", {
      header: "Email",
      cell: (info) => info.getValue(),
    }),
    ...(isSuperadmin
      ? [
          columnHelper.accessor("tenant_name", {
            header: "Tenant",
            cell: (info) => (
              <span className="text-muted-foreground">{info.getValue()}</span>
            ),
          }),
        ]
      : []),
    columnHelper.accessor("role", {
      header: "Role",
      cell: (info) => (
        <Badge variant="outline" className="capitalize">
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor("is_active", {
      header: "Status",
      cell: (info) => (
        <Badge variant={info.getValue() ? "default" : "secondary"}>
          {info.getValue() ? "Active" : "Inactive"}
        </Badge>
      ),
    }),
    columnHelper.accessor("created_at", {
      header: "Created",
      cell: (info) => new Date(info.getValue()).toLocaleDateString(),
    }),
    columnHelper.display({
      id: "actions",
      header: "",
      cell: ({ row }) =>
        row.original.role === "superadmin" ? null : (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon-xs">
                <MoreHorizontal />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => openEdit(row.original)}>
                Edit
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
    }),
  ];

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

      <div className="mt-6 rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No users found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Create User Dialog */}
      <Dialog
        open={createOpen}
        onOpenChange={(open) => {
          setCreateOpen(open);
          if (!open) setTenantError("");
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create User</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (isSuperadmin && !newTenantId) {
                setTenantError("Please select a tenant");
                return;
              }
              setTenantError("");
              createMutation.mutate({
                email: newEmail,
                password: newPassword,
                role_id: Number(newRoleId),
                ...(isSuperadmin && newTenantId ? { tenant_id: newTenantId } : {}),
              });
            }}
            className="space-y-4"
          >
            {isSuperadmin && (
              <div className="space-y-2">
                <Label>Tenant</Label>
                <Select
                  value={newTenantId}
                  onValueChange={(v) => {
                    setNewTenantId(v);
                    setTenantError("");
                  }}
                >
                  <SelectTrigger
                    className={tenantError ? "border-destructive" : ""}
                  >
                    <SelectValue placeholder="Select a tenant" />
                  </SelectTrigger>
                  <SelectContent>
                    {tenants.map((t) => (
                      <SelectItem key={t.id} value={t.id}>
                        {t.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {tenantError && (
                  <p className="text-sm text-destructive">{tenantError}</p>
                )}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="new-email">Email</Label>
              <Input
                id="new-email"
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-password">Password</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Role</Label>
              <Select value={newRoleId} onValueChange={setNewRoleId}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2">admin</SelectItem>
                  <SelectItem value="3">user</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog
        open={editUser !== null}
        onOpenChange={(open) => {
          if (!open) setEditUser(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
            <DialogDescription>{editUser?.email}</DialogDescription>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!editUser) return;
              updateMutation.mutate({
                id: editUser.id,
                role_id: Number(editRoleId),
                is_active: editActive,
              });
            }}
            className="space-y-4"
          >
            {isSuperadmin && editUser && (
              <div className="space-y-2">
                <Label>Tenant</Label>
                <Input value={editUser.tenant_name} disabled />
              </div>
            )}
            <div className="space-y-2">
              <Label>Role</Label>
              <Select value={editRoleId} onValueChange={setEditRoleId}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2">admin</SelectItem>
                  <SelectItem value="3">user</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="edit-active">Active</Label>
              <Switch
                id="edit-active"
                checked={editActive}
                onCheckedChange={setEditActive}
              />
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditUser(null)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? "Saving..." : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function roleNameToId(name: string): string {
  switch (name) {
    case "superadmin":
      return "1";
    case "admin":
      return "2";
    default:
      return "3";
  }
}
