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
import type { Tenant } from "@/types";

const columnHelper = createColumnHelper<Tenant>();

interface TenantColumnCallbacks {
  onEdit: (tenant: Tenant) => void;
  onDelete: (tenant: Tenant) => void;
  onAddAdmin: (tenantId: string) => void;
}

export function getTenantColumns({
  onEdit,
  onDelete,
  onAddAdmin,
}: TenantColumnCallbacks) {
  return [
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
              <DropdownMenuItem onClick={() => onEdit(row.original)}>
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onAddAdmin(row.original.id)}>
                Add Admin
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
