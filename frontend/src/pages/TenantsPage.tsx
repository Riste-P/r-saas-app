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
import {
  useTenantsQuery,
  useCreateTenant,
  useUpdateTenant,
  useDeleteTenant,
  useCreateTenantAdmin,
} from "@/hooks/useTenants";
import type { Tenant } from "@/types";
import {
  createTenantSchema,
  editTenantSchema,
  createTenantAdminSchema,
  type CreateTenantFormValues,
  type EditTenantFormValues,
  type CreateTenantAdminFormValues,
} from "@/lib/schemas";

function deriveSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

const columnHelper = createColumnHelper<Tenant>();

export default function TenantsPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [editTenant, setEditTenant] = useState<Tenant | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Tenant | null>(null);
  const [adminOpen, setAdminOpen] = useState<string | null>(null);

  const { data: tenants = [], isLoading } = useTenantsQuery();

  const createForm = useForm<CreateTenantFormValues>({
    resolver: zodResolver(createTenantSchema),
    defaultValues: { name: "", slug: "" },
  });

  const editForm = useForm<EditTenantFormValues>({
    resolver: zodResolver(editTenantSchema),
    defaultValues: { name: "", is_active: true },
  });

  const adminForm = useForm<CreateTenantAdminFormValues>({
    resolver: zodResolver(createTenantAdminSchema),
    defaultValues: { email: "", password: "" },
  });

  const createMutation = useCreateTenant({
    onSuccess: () => {
      setCreateOpen(false);
      createForm.reset();
    },
  });

  const updateMutation = useUpdateTenant({
    onSuccess: () => setEditTenant(null),
  });

  const deleteMutation = useDeleteTenant({
    onSuccess: () => setDeleteTarget(null),
  });

  const createAdminMutation = useCreateTenantAdmin({
    onSuccess: () => {
      setAdminOpen(null);
      adminForm.reset();
    },
  });

  function openEdit(tenant: Tenant) {
    setEditTenant(tenant);
    editForm.reset({
      name: tenant.name,
      is_active: tenant.is_active,
    });
  }

  function onCreateSubmit(values: CreateTenantFormValues) {
    createMutation.mutate({ name: values.name, slug: values.slug });
  }

  function onEditSubmit(values: EditTenantFormValues) {
    if (!editTenant) return;
    updateMutation.mutate({
      id: editTenant.id,
      name: values.name,
      is_active: values.is_active,
    });
  }

  function onAdminSubmit(values: CreateTenantAdminFormValues) {
    if (!adminOpen) return;
    createAdminMutation.mutate({
      email: values.email,
      password: values.password,
      role_id: 2,
      tenant_id: adminOpen,
    });
  }

  const columns = [
    columnHelper.accessor("name", {
      header: "Name",
      cell: (info) => <span className="font-medium">{info.getValue()}</span>,
    }),
    columnHelper.accessor("slug", {
      header: "Slug",
      cell: (info) => (
        <code className="text-sm text-muted-foreground">{info.getValue()}</code>
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
        row.original.slug === "system" ? null : (
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
            <DropdownMenuItem onClick={() => setAdminOpen(row.original.id)}>
              Add Admin
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
    data: tenants,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) {
    return <p className="text-muted-foreground">Loading tenants...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Tenants</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage all tenants in the system
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>Create Tenant</Button>
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
                  No tenants found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Create Tenant Dialog */}
      <Dialog
        open={createOpen}
        onOpenChange={(open) => {
          setCreateOpen(open);
          if (!open) createForm.reset();
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Tenant</DialogTitle>
          </DialogHeader>
          <Form {...createForm}>
            <form
              onSubmit={createForm.handleSubmit(onCreateSubmit)}
              noValidate
              className="space-y-4"
            >
              <FormField
                control={createForm.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        onChange={(e) => {
                          field.onChange(e);
                          createForm.setValue("slug", deriveSlug(e.target.value), {
                            shouldValidate: createForm.formState.isSubmitted,
                          });
                        }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={createForm.control}
                name="slug"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Slug</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
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

      {/* Edit Tenant Dialog */}
      <Dialog
        open={editTenant !== null}
        onOpenChange={(open) => {
          if (!open) setEditTenant(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Tenant</DialogTitle>
            <DialogDescription>{editTenant?.slug}</DialogDescription>
          </DialogHeader>
          <Form {...editForm}>
            <form
              onSubmit={editForm.handleSubmit(onEditSubmit)}
              noValidate
              className="space-y-4"
            >
              <FormField
                control={editForm.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
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
                  onClick={() => setEditTenant(null)}
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

      {/* Delete Tenant Confirmation */}
      <AlertDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Tenant</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete tenant <strong>{deleteTarget?.name}</strong>?
              This action cannot be undone. All users in this tenant will lose access.
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

      {/* Create Admin User for Tenant Dialog */}
      <Dialog
        open={adminOpen !== null}
        onOpenChange={(open) => {
          if (!open) {
            setAdminOpen(null);
            adminForm.reset();
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Admin User</DialogTitle>
          </DialogHeader>
          <Form {...adminForm}>
            <form
              onSubmit={adminForm.handleSubmit(onAdminSubmit)}
              noValidate
              className="space-y-4"
            >
              <FormField
                control={adminForm.control}
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
                control={adminForm.control}
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
              <DialogFooter>
                <Button type="submit" disabled={createAdminMutation.isPending}>
                  {createAdminMutation.isPending ? "Creating..." : "Create Admin"}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
