import { useState, useMemo } from "react";
import { getCoreRowModel, getExpandedRowModel, useReactTable } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TableRow, TableCell } from "@/components/ui/table";
import { DataTable } from "@/components/DataTable";
import { usePropertiesQuery } from "@/hooks/useProperties";
import { useClientsQuery } from "@/hooks/useClients";
import { getPropertyColumns } from "./PropertyColumns";
import { CreatePropertyDialog } from "./CreatePropertyDialog";
import { EditPropertyDialog } from "./EditPropertyDialog";
import { DeletePropertyDialog } from "./DeletePropertyDialog";

const typeLabels: Record<string, string> = {
  house: "House",
  apartment: "Apartment",
  building: "Building",
  commercial: "Commercial",
};

export default function PropertiesPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [editTargetId, setEditTargetId] = useState<string | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>("");
  const [filterClient, setFilterClient] = useState<string>("");

  const { data: clients = [] } = useClientsQuery();
  const { data: properties = [], isLoading } = usePropertiesQuery({
    property_type: filterType && filterType !== "all" ? filterType : undefined,
    client_id: filterClient && filterClient !== "all" ? filterClient : undefined,
    parents_only: true,
  });

  const columns = useMemo(
    () => getPropertyColumns({ onEdit: setEditTargetId, onDelete: setDeleteTargetId }),
    []
  );

  const table = useReactTable({
    data: properties,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getRowCanExpand: (row) => (row.original.child_properties?.length ?? 0) > 0,
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

      <div className="mt-4 flex items-center gap-3">
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
      </div>

      <DataTable
        table={table}
        columnCount={columns.length}
        emptyMessage="No properties found."
        renderExpandedRows={(row) => {
          const children = row.original.child_properties;
          if (!children?.length) return null;
          return children.map((child) => (
            <TableRow key={child.id} className="bg-muted/50">
              <TableCell />
              <TableCell className="pl-8">{child.name}</TableCell>
              <TableCell>
                <Badge variant="outline">{typeLabels[child.property_type]}</Badge>
              </TableCell>
              <TableCell className="text-muted-foreground">{child.client_name ?? "—"}</TableCell>
              <TableCell className="text-muted-foreground">{child.address ?? "—"}</TableCell>
              <TableCell>
                <Badge variant={child.is_active ? "default" : "secondary"}>
                  {child.is_active ? "Active" : "Inactive"}
                </Badge>
              </TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon-xs">
                      <MoreHorizontal />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setEditTargetId(child.id)}>
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-destructive focus:text-destructive"
                      onClick={() => setDeleteTargetId(child.id)}
                    >
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ));
        }}
      />

      <CreatePropertyDialog open={createOpen} onOpenChange={setCreateOpen} />
      <EditPropertyDialog propertyId={editTargetId} onClose={() => setEditTargetId(null)} />
      <DeletePropertyDialog propertyId={deleteTargetId} onClose={() => setDeleteTargetId(null)} />
    </div>
  );
}
