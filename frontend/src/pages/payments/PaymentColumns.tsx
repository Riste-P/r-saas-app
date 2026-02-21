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
import type { Payment } from "@/types";

const columnHelper = createColumnHelper<Payment>();

const methodLabels: Record<string, string> = {
  cash: "Cash",
  bank_transfer: "Bank Transfer",
  card: "Card",
  other: "Other",
};

interface PaymentColumnCallbacks {
  onDelete: (id: string) => void;
}

export function getPaymentColumns({ onDelete }: PaymentColumnCallbacks) {
  return [
    columnHelper.accessor("invoice_number", {
      header: "Invoice #",
      cell: (info) => <span className="font-medium">{info.getValue()}</span>,
    }),
    columnHelper.accessor("amount", {
      header: "Amount",
      cell: (info) => `$${Number(info.getValue()).toFixed(2)}`,
    }),
    columnHelper.accessor("payment_date", {
      header: "Date",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("payment_method", {
      header: "Method",
      cell: (info) => (
        <Badge variant="outline">
          {methodLabels[info.getValue()] ?? info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor("reference", {
      header: "Reference",
      cell: (info) => (
        <span className="text-muted-foreground">{info.getValue() ?? "—"}</span>
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
