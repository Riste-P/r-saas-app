import { useState, useMemo, useEffect } from "react";
import { getCoreRowModel, useReactTable, type RowSelectionState } from "@tanstack/react-table";
import { ChevronDown, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { DataTable } from "@/components/DataTable";
import {
  useInvoicesQuery,
  useBulkUpdateStatus,
  useBulkDeleteInvoices,
} from "@/hooks/useInvoices";
import { useClientsQuery } from "@/hooks/useClients";
import { usePropertiesQuery } from "@/hooks/useProperties";
import { getInvoiceColumns } from "./InvoiceColumns";
import { CreateInvoiceDialog } from "./CreateInvoiceDialog";
import { GenerateInvoicesDialog } from "./GenerateInvoicesDialog";
import { EditInvoiceDialog } from "./EditInvoiceDialog";
import { DeleteInvoiceDialog } from "./DeleteInvoiceDialog";
import { InvoiceDetailDialog } from "./InvoiceDetailDialog";
import { CreatePaymentDialog } from "../payments/CreatePaymentDialog";
import type { InvoiceStatus } from "@/types";

const STATUS_OPTIONS: { value: InvoiceStatus; label: string }[] = [
  { value: "draft", label: "Draft" },
  { value: "sent", label: "Sent" },
  { value: "paid", label: "Paid" },
  { value: "overdue", label: "Overdue" },
  { value: "cancelled", label: "Cancelled" },
];

interface BulkAction {
  type: "status" | "delete";
  status?: InvoiceStatus;
}

export default function InvoicesPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [generateOpen, setGenerateOpen] = useState(false);
  const [editTargetId, setEditTargetId] = useState<string | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [detailTargetId, setDetailTargetId] = useState<string | null>(null);
  const [paymentInvoiceId, setPaymentInvoiceId] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterProperty, setFilterProperty] = useState<string>("");
  const [filterClient, setFilterClient] = useState<string>("");
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [bulkAction, setBulkAction] = useState<BulkAction | null>(null);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(searchInput), 300);
    return () => clearTimeout(t);
  }, [searchInput]);

  const { data: clients = [] } = useClientsQuery();
  const { data: properties = [] } = usePropertiesQuery({ parents_only: true });

  const propertyOptions = useMemo(() => [
    { value: "all", label: "All Properties" },
    ...properties.map((p) => ({ value: p.id, label: p.name })),
  ], [properties]);

  const { data: invoices = [], isLoading } = useInvoicesQuery({
    status: filterStatus && filterStatus !== "all" ? filterStatus : undefined,
    property_id: filterProperty && filterProperty !== "all" ? filterProperty : undefined,
    client_id: filterClient && filterClient !== "all" ? filterClient : undefined,
    search: debouncedSearch || undefined,
  });

  const clearSelection = () => setRowSelection({});

  const bulkUpdateStatus = useBulkUpdateStatus({ onSuccess: clearSelection });
  const bulkDelete = useBulkDeleteInvoices({ onSuccess: clearSelection });

  const columns = useMemo(
    () => getInvoiceColumns({
      onView: setDetailTargetId,
      onEdit: setEditTargetId,
      onDelete: setDeleteTargetId,
    }),
    []
  );

  const table = useReactTable({
    data: invoices,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    state: { rowSelection },
    getRowId: (row) => row.id,
  });

  const selectedCount = Object.keys(rowSelection).length;
  const selectedIds = Object.keys(rowSelection);

  const handleBulkConfirm = () => {
    if (!bulkAction) return;
    if (bulkAction.type === "status" && bulkAction.status) {
      bulkUpdateStatus.mutate({ ids: selectedIds, status: bulkAction.status });
    } else if (bulkAction.type === "delete") {
      bulkDelete.mutate(selectedIds);
    }
    setBulkAction(null);
  };

  const isBulkPending = bulkUpdateStatus.isPending || bulkDelete.isPending;

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Invoices</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage invoices and billing
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setGenerateOpen(true)}>
            Generate Invoices
          </Button>
          <Button onClick={() => setCreateOpen(true)}>Create Invoice</Button>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-3">
        <Input
          placeholder="Search invoice #"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="w-[180px]"
        />
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="sent">Sent</SelectItem>
            <SelectItem value="paid">Paid</SelectItem>
            <SelectItem value="overdue">Overdue</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <SearchableSelect
          options={propertyOptions}
          value={filterProperty || "all"}
          onValueChange={setFilterProperty}
          placeholder="All Properties"
          searchPlaceholder="Search properties..."
          className="w-[200px]"
        />
        <SearchableSelect
          options={[
            { value: "all", label: "All Clients" },
            ...clients.map((c) => ({ value: c.id, label: c.name })),
          ]}
          value={filterClient || "all"}
          onValueChange={setFilterClient}
          placeholder="All Clients"
          searchPlaceholder="Search clients..."
          className="w-[200px]"
        />
        {selectedCount > 0 && (
          <div className="ml-auto flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {selectedCount} selected
            </span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" disabled={isBulkPending}>
                  Actions
                  <ChevronDown className="ml-1.5 size-3.5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuSub>
                  <DropdownMenuSubTrigger>Change Status</DropdownMenuSubTrigger>
                  <DropdownMenuSubContent>
                    {STATUS_OPTIONS.map((s) => (
                      <DropdownMenuItem
                        key={s.value}
                        onClick={() => setBulkAction({ type: "status", status: s.value })}
                      >
                        {s.label}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuSubContent>
                </DropdownMenuSub>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  variant="destructive"
                  onClick={() => setBulkAction({ type: "delete" })}
                >
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={clearSelection}
            >
              <X className="size-3.5" />
            </Button>
          </div>
        )}
      </div>

      {isLoading ? (
        <p className="mt-6 text-center text-muted-foreground">Loading invoices...</p>
      ) : (
        <DataTable
          table={table}
          columnCount={columns.length}
          emptyMessage="No invoices found."
        />
      )}

      {/* Bulk action confirmation */}
      <AlertDialog open={bulkAction !== null} onOpenChange={(open) => { if (!open) setBulkAction(null); }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {bulkAction?.type === "delete"
                ? "Delete Invoices"
                : "Change Invoice Status"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {bulkAction?.type === "delete"
                ? `Are you sure you want to delete ${selectedCount} invoice${selectedCount !== 1 ? "s" : ""}? Only draft and cancelled invoices can be deleted.`
                : `Change ${selectedCount} invoice${selectedCount !== 1 ? "s" : ""} to "${STATUS_OPTIONS.find((s) => s.value === bulkAction?.status)?.label}"?`}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className={bulkAction?.type === "delete" ? "bg-destructive text-white hover:bg-destructive/90" : ""}
              onClick={handleBulkConfirm}
            >
              {bulkAction?.type === "delete" ? "Delete" : "Change Status"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <CreateInvoiceDialog open={createOpen} onOpenChange={setCreateOpen} />
      <GenerateInvoicesDialog open={generateOpen} onOpenChange={setGenerateOpen} />
      <EditInvoiceDialog invoiceId={editTargetId} onClose={() => setEditTargetId(null)} />
      <DeleteInvoiceDialog invoiceId={deleteTargetId} onClose={() => setDeleteTargetId(null)} />
      <InvoiceDetailDialog
        invoiceId={detailTargetId}
        onClose={() => setDetailTargetId(null)}
        onRecordPayment={(id) => {
          setDetailTargetId(null);
          setPaymentInvoiceId(id);
        }}
      />
      <CreatePaymentDialog
        invoiceId={paymentInvoiceId}
        onClose={() => setPaymentInvoiceId(null)}
      />
    </div>
  );
}
