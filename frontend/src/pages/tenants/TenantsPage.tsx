import { useState, useMemo } from "react";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/DataTable";
import { useTenantsQuery } from "@/hooks/useTenants";
import { getTenantColumns } from "./TenantColumns";
import { CreateTenantDialog } from "./CreateTenantDialog";
import { EditTenantDialog } from "./EditTenantDialog";
import { DeleteTenantDialog } from "./DeleteTenantDialog";
import { CreateTenantAdminDialog } from "./CreateTenantAdminDialog";
import type { Tenant } from "@/types";

export default function TenantsPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [editTenant, setEditTenant] = useState<Tenant | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Tenant | null>(null);
  const [adminTenantId, setAdminTenantId] = useState<string | null>(null);

  const { data: tenants = [], isLoading } = useTenantsQuery();

  const columns = useMemo(
    () =>
      getTenantColumns({
        onEdit: setEditTenant,
        onDelete: setDeleteTarget,
        onAddAdmin: setAdminTenantId,
      }),
    []
  );

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

      <DataTable
        table={table}
        columnCount={columns.length}
        emptyMessage="No tenants found."
      />

      <CreateTenantDialog open={createOpen} onOpenChange={setCreateOpen} />
      <EditTenantDialog tenant={editTenant} onClose={() => setEditTenant(null)} />
      <DeleteTenantDialog tenant={deleteTarget} onClose={() => setDeleteTarget(null)} />
      <CreateTenantAdminDialog tenantId={adminTenantId} onClose={() => setAdminTenantId(null)} />
    </div>
  );
}
