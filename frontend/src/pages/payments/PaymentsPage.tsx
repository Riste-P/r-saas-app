import { useState, useMemo } from "react";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { DataTable } from "@/components/DataTable";
import { usePaymentsQuery } from "@/hooks/usePayments";
import { getPaymentColumns } from "./PaymentColumns";
import { DeletePaymentDialog } from "./DeletePaymentDialog";

export default function PaymentsPage() {
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);

  const { data: payments = [], isLoading } = usePaymentsQuery();

  const columns = useMemo(
    () => getPaymentColumns({ onDelete: setDeleteTargetId }),
    []
  );

  const table = useReactTable({
    data: payments,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) {
    return <p className="text-muted-foreground">Loading payments...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Payments</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Track payment records
          </p>
        </div>
      </div>

      <DataTable
        table={table}
        columnCount={columns.length}
        emptyMessage="No payments found."
      />

      <DeletePaymentDialog paymentId={deleteTargetId} onClose={() => setDeleteTargetId(null)} />
    </div>
  );
}
