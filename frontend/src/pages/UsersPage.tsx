import { useState } from "react";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useAuthStore } from "@/stores/auth";
import { useUsersQuery, useCreateUser, useUpdateUser, useDeleteUser } from "@/hooks/useUsers";
import { useTenantsQuery } from "@/hooks/useTenants";
import type { UserListItem } from "@/types";
import {
  createUserSchema,
  createUserSuperadminSchema,
  editUserSchema,
  type CreateUserFormValues,
  type EditUserFormValues,
} from "@/lib/schemas";

const columnHelper = createColumnHelper<UserListItem>();

export default function UsersPage() {
  const currentUser = useAuthStore((s) => s.user);
  const isSuperadmin = currentUser?.role === "superadmin";

  const [createOpen, setCreateOpen] = useState(false);
  const [editUser, setEditUser] = useState<UserListItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<UserListItem | null>(null);

  const { data: users = [], isLoading } = useUsersQuery();
  const { data: tenants = [] } = useTenantsQuery(isSuperadmin);

  const createForm = useForm<CreateUserFormValues>({
    resolver: zodResolver(isSuperadmin ? createUserSuperadminSchema : createUserSchema),
    defaultValues: { email: "", password: "", role_id: "3", tenant_id: "" },
  });

  const editForm = useForm<EditUserFormValues>({
    resolver: zodResolver(editUserSchema),
    defaultValues: { role_id: "3", is_active: true },
  });

  const createMutation = useCreateUser({
    onSuccess: () => {
      setCreateOpen(false);
      createForm.reset();
    },
  });

  const updateMutation = useUpdateUser({
    onSuccess: () => setEditUser(null),
  });

  const deleteMutation = useDeleteUser({
    onSuccess: () => setDeleteTarget(null),
  });

  function openEdit(user: UserListItem) {
    setEditUser(user);
    editForm.reset({
      role_id: roleNameToId(user.role),
      is_active: user.is_active,
    });
  }

  function onCreateSubmit(values: CreateUserFormValues) {
    createMutation.mutate({
      email: values.email,
      password: values.password,
      role_id: Number(values.role_id),
      ...(isSuperadmin && values.tenant_id ? { tenant_id: values.tenant_id } : {}),
    });
  }

  function onEditSubmit(values: EditUserFormValues) {
    if (!editUser) return;
    updateMutation.mutate({
      id: editUser.id,
      role_id: Number(values.role_id),
      is_active: values.is_active,
    });
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
              <DropdownMenuItem
                className="text-destructive focus:text-destructive"
                onClick={() => setDeleteTarget(row.original)}
              >
                Delete
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
          if (!open) createForm.reset();
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create User</DialogTitle>
          </DialogHeader>
          <Form {...createForm}>
            <form
              onSubmit={createForm.handleSubmit(onCreateSubmit)}
              noValidate
              className="space-y-4"
            >
              {isSuperadmin && (
                <FormField
                  control={createForm.control}
                  name="tenant_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tenant</FormLabel>
                      <Select
                        value={field.value}
                        onValueChange={field.onChange}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a tenant" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {tenants.map((t) => (
                            <SelectItem key={t.id} value={t.id}>
                              {t.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
              <FormField
                control={createForm.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={createForm.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={createForm.control}
                name="role_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Role</FormLabel>
                    <Select
                      value={field.value}
                      onValueChange={field.onChange}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="2">admin</SelectItem>
                        <SelectItem value="3">user</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Creating..." : "Create"}
                </Button>
              </DialogFooter>
            </form>
          </Form>
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
          <Form {...editForm}>
            <form
              onSubmit={editForm.handleSubmit(onEditSubmit)}
              noValidate
              className="space-y-4"
            >
              {isSuperadmin && editUser && (
                <div className="space-y-2">
                  <FormLabel>Tenant</FormLabel>
                  <Input value={editUser.tenant_name} disabled />
                </div>
              )}
              <FormField
                control={editForm.control}
                name="role_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Role</FormLabel>
                    <Select
                      value={field.value}
                      onValueChange={field.onChange}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="2">admin</SelectItem>
                        <SelectItem value="3">user</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={editForm.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between">
                    <FormLabel>Active</FormLabel>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
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
          </Form>
        </DialogContent>
      </Dialog>

      {/* Delete User Confirmation */}
      <AlertDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete User</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{deleteTarget?.email}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white hover:bg-destructive/90"
              disabled={deleteMutation.isPending}
              onClick={() => {
                if (deleteTarget) {
                  deleteMutation.mutate(deleteTarget.id);
                }
              }}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
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
