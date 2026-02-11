import { createColumnHelper } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { ServiceType } from "@/types";

const columnHelper = createColumnHelper<ServiceType>();

interface ServiceTypeColumnCallbacks {
  onEdit: (st: ServiceType) => void;
  onChecklist: (st: ServiceType) => void;
  onDelete: (st: ServiceType) => void;
}

export function getServiceTypeColumns({
  onEdit,
  onChecklist,
  onDelete,
}: ServiceTypeColumnCallbacks) {
  return [
    columnHelper.accessor("name", {
      header: "Name",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("base_price", {
      header: "Base Price",
      cell: (info) => `$${Number(info.getValue()).toFixed(2)}`,
    }),
    columnHelper.accessor("estimated_duration_minutes", {
      header: "Duration",
      cell: (info) => `${info.getValue()} min`,
    }),
    columnHelper.accessor("is_active", {
      header: "Status",
      cell: (info) => (
        <Badge variant={info.getValue() ? "default" : "secondary"}>
          {info.getValue() ? "Active" : "Inactive"}
        </Badge>
      ),
    }),
    columnHelper.accessor("checklist_items", {
      header: "Checklist",
      cell: (info) => {
        const count = info.getValue().length;
        return (
          <span className="text-muted-foreground">
            {count} {count === 1 ? "item" : "items"}
          </span>
        );
      },
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
            <DropdownMenuItem onClick={() => onEdit(row.original)}>
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onChecklist(row.original)}>
              Checklist
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => onDelete(row.original)}
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    }),
  ];
}
