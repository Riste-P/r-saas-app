import { useState, useMemo } from "react";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DataTable } from "@/components/DataTable";
import { usePropertiesQuery } from "@/hooks/useProperties";
import { useClientsQuery } from "@/hooks/useClients";
import { getPropertyColumns } from "./PropertyColumns";
import { CreatePropertyDialog } from "./CreatePropertyDialog";
import { EditPropertyDialog } from "./EditPropertyDialog";
import { DeletePropertyDialog } from "./DeletePropertyDialog";
import type { Property } from "@/types";

export default function PropertiesPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Property | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Property | null>(null);
  const [filterClient, setFilterClient] = useState<string>("");
  const [filterType, setFilterType] = useState<string>("");

  const { data: clients = [] } = useClientsQuery();
  const { data: properties = [], isLoading } = usePropertiesQuery({
    client_id: filterClient && filterClient !== "all" ? filterClient : undefined,
    property_type: filterType && filterType !== "all" ? filterType : undefined,
  });

  const columns = useMemo(
    () => getPropertyColumns({ onEdit: setEditTarget, onDelete: setDeleteTarget }),
    []
  );

  const table = useReactTable({
    data: properties,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) {
    return <p className="text-muted-foreground">Loading properties...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Properties</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage client properties and locations
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>Create Property</Button>
      </div>

      <div className="mt-4 flex gap-3">
        <Select value={filterClient} onValueChange={setFilterClient}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="All Clients" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Clients</SelectItem>
            {clients.map((c) => (
              <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="house">House</SelectItem>
            <SelectItem value="apartment">Apartment</SelectItem>
            <SelectItem value="building">Building</SelectItem>
            <SelectItem value="commercial">Commercial</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <DataTable
        table={table}
        columnCount={columns.length}
        emptyMessage="No properties found."
      />

      <CreatePropertyDialog open={createOpen} onOpenChange={setCreateOpen} />
      <EditPropertyDialog property={editTarget} onClose={() => setEditTarget(null)} />
      <DeletePropertyDialog property={deleteTarget} onClose={() => setDeleteTarget(null)} />
    </div>
  );
}
