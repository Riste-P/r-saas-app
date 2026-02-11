import { useState, useMemo } from "react";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/DataTable";
import { useClientsQuery } from "@/hooks/useClients";
import { getClientColumns } from "./ClientColumns";
import { CreateClientDialog } from "./CreateClientDialog";
import { EditClientDialog } from "./EditClientDialog";
import { DeleteClientDialog } from "./DeleteClientDialog";
import type { Client } from "@/types";

export default function ClientsPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Client | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Client | null>(null);

  const { data: clients = [], isLoading } = useClientsQuery();

  const columns = useMemo(
    () => getClientColumns({ onEdit: setEditTarget, onDelete: setDeleteTarget }),
    []
  );

  const table = useReactTable({
    data: clients,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) {
    return <p className="text-muted-foreground">Loading clients...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Clients</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage your cleaning clients
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>Create Client</Button>
      </div>

      <DataTable
        table={table}
        columnCount={columns.length}
        emptyMessage="No clients found."
      />

      <CreateClientDialog open={createOpen} onOpenChange={setCreateOpen} />
      <EditClientDialog client={editTarget} onClose={() => setEditTarget(null)} />
      <DeleteClientDialog client={deleteTarget} onClose={() => setDeleteTarget(null)} />
    </div>
  );
}
