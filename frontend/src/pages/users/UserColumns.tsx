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
import type { UserListItem } from "@/types";

const columnHelper = createColumnHelper<UserListItem>();

interface UserColumnCallbacks {
  isSuperadmin: boolean;
  onEdit: (user: UserListItem) => void;
  onDelete: (user: UserListItem) => void;
}

export function getUserColumns({
  isSuperadmin,
  onEdit,
  onDelete,
}: UserColumnCallbacks) {
  return [
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
              <DropdownMenuItem onClick={() => onEdit(row.original)}>
                Edit
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
