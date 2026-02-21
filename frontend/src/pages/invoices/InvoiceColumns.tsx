import { createColumnHelper } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { InvoiceListItem } from "@/types";

const columnHelper = createColumnHelper<InvoiceListItem>();

const statusConfig: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; label: string; className?: string }> = {
  draft: { variant: "outline", label: "Draft" },
  sent: { variant: "default", label: "Sent" },
  paid: { variant: "default", label: "Paid", className: "bg-emerald-600 hover:bg-emerald-600" },
  overdue: { variant: "destructive", label: "Overdue" },
  cancelled: { variant: "secondary", label: "Cancelled" },
};

interface InvoiceColumnCallbacks {
  onView: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function getInvoiceColumns({ onView, onEdit, onDelete }: InvoiceColumnCallbacks) {
  return [
    columnHelper.display({
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && "indeterminate")
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    }),
    columnHelper.accessor("invoice_number", {
      header: "Invoice #",
      cell: (info) => (
        <button
          className="font-medium text-primary hover:underline"
          onClick={() => onView(info.row.original.id)}
        >
          {info.getValue()}
        </button>
      ),
    }),
    columnHelper.accessor("client_name", {
      header: "Client",
      cell: (info) => (
        <span className="text-muted-foreground">{info.getValue() ?? "—"}</span>
      ),
    }),
    columnHelper.accessor("property_name", {
      header: "Property",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("parent_property_name", {
      header: "Parent",
      cell: (info) => (
        <span className="text-muted-foreground">{info.getValue() ?? "—"}</span>
      ),
    }),
    columnHelper.accessor("status", {
      header: "Status",
      cell: (info) => {
        const s = statusConfig[info.getValue()] ?? { variant: "outline" as const, label: info.getValue() };
        return <Badge variant={s.variant} className={s.className}>{s.label}</Badge>;
      },
    }),
    columnHelper.accessor("total", {
      header: "Total",
      cell: (info) => `$${Number(info.getValue()).toFixed(2)}`,
    }),
    columnHelper.accessor("issue_date", {
      header: "Issue Date",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("due_date", {
      header: "Due Date",
      cell: (info) => info.getValue(),
    }),
    columnHelper.display({
      id: "actions",
      header: "",
      cell: ({ row }) => {
        const inv = row.original;
        const canDelete = inv.status === "draft" || inv.status === "cancelled";
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon-xs">
                <MoreHorizontal />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onView(inv.id)}>
                View
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onEdit(inv.id)}>
                Edit
              </DropdownMenuItem>
              {canDelete && (
                <DropdownMenuItem
                  className="text-destructive focus:text-destructive"
                  onClick={() => onDelete(inv.id)}
                >
                  Delete
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    }),
  ];
}
