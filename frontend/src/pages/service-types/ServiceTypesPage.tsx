import { useState, useMemo } from "react";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/DataTable";
import { useServiceTypesQuery } from "@/hooks/useServiceTypes";
import { getServiceTypeColumns } from "./ServiceTypeColumns";
import { CreateServiceTypeDialog } from "./CreateServiceTypeDialog";
import { EditServiceTypeDialog } from "./EditServiceTypeDialog";
import { DeleteServiceTypeDialog } from "./DeleteServiceTypeDialog";
import { ChecklistEditor } from "./ChecklistEditor";
import type { ServiceType } from "@/types";

export default function ServiceTypesPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<ServiceType | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<ServiceType | null>(null);
  const [checklistTarget, setChecklistTarget] = useState<ServiceType | null>(null);

  const { data: serviceTypes = [], isLoading } = useServiceTypesQuery();

  const columns = useMemo(
    () =>
      getServiceTypeColumns({
        onEdit: setEditTarget,
        onChecklist: setChecklistTarget,
        onDelete: setDeleteTarget,
      }),
    []
  );

  const table = useReactTable({
    data: serviceTypes,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) {
    return <p className="text-muted-foreground">Loading service types...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Service Types</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage cleaning service types and their checklists
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>Create Service Type</Button>
      </div>

      <DataTable
        table={table}
        columnCount={columns.length}
        emptyMessage="No service types found."
      />

      <CreateServiceTypeDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
      />
      <EditServiceTypeDialog
        serviceType={editTarget}
        onClose={() => setEditTarget(null)}
      />
      <DeleteServiceTypeDialog
        serviceType={deleteTarget}
        onClose={() => setDeleteTarget(null)}
      />
      <ChecklistEditor
        serviceType={checklistTarget}
        onClose={() => setChecklistTarget(null)}
      />
    </div>
  );
}
