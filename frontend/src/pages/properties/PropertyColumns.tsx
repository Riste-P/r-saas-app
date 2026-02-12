import { createColumnHelper } from "@tanstack/react-table";
import { ChevronRight, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Property } from "@/types";

const columnHelper = createColumnHelper<Property>();

const typeLabels: Record<string, string> = {
  house: "House",
  apartment: "Apartment",
  building: "Building",
  commercial: "Commercial",
};

interface PropertyColumnCallbacks {
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function getPropertyColumns({ onEdit, onDelete }: PropertyColumnCallbacks) {
  return [
    columnHelper.display({
      id: "expand",
      header: "",
      size: 32,
      cell: ({ row }) => {
        if (!row.original.child_properties?.length) return null;
        return (
          <Button
            variant="ghost"
            size="icon-xs"
            onClick={() => row.toggleExpanded()}
          >
            <ChevronRight
              className={`size-4 transition-transform ${row.getIsExpanded() ? "rotate-90" : ""}`}
            />
          </Button>
        );
      },
    }),
    columnHelper.accessor("name", {
      header: "Name",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("property_type", {
      header: "Type",
      cell: (info) => (
        <Badge variant="outline">{typeLabels[info.getValue()]}</Badge>
      ),
    }),
    columnHelper.accessor("client_name", {
      header: "Client",
      cell: (info) => (
        <span className="text-muted-foreground">{info.getValue() ?? "—"}</span>
      ),
    }),
    columnHelper.accessor("address", {
      header: "Address",
      cell: (info) => (
        <span className="max-w-[200px] truncate text-muted-foreground">
          {info.getValue() ?? "—"}
        </span>
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
    columnHelper.display({
      id: "actions",
      header: "",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon-xs">
              <MoreHorizontal />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(row.original.id)}>
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => onDelete(row.original.id)}
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    }),
  ];
}
