import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Separator } from "@/components/ui/separator";
import { useInvoiceQuery } from "@/hooks/useInvoices";

const statusConfig: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; label: string; className?: string }> = {
  draft: { variant: "outline", label: "Draft" },
  sent: { variant: "default", label: "Sent" },
  paid: { variant: "default", label: "Paid", className: "bg-emerald-600 hover:bg-emerald-600" },
  overdue: { variant: "destructive", label: "Overdue" },
  cancelled: { variant: "secondary", label: "Cancelled" },
};

const methodLabels: Record<string, string> = {
  cash: "Cash",
  bank_transfer: "Bank Transfer",
  card: "Card",
  other: "Other",
};

interface InvoiceDetailDialogProps {
  invoiceId: string | null;
  onClose: () => void;
  onRecordPayment: (invoiceId: string) => void;
}

export function InvoiceDetailDialog({ invoiceId, onClose, onRecordPayment }: InvoiceDetailDialogProps) {
  const { data: invoice } = useInvoiceQuery(invoiceId);

  if (!invoice) {
    return (
      <Dialog open={invoiceId !== null} onOpenChange={(open) => { if (!open) onClose(); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invoice</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">Loading...</p>
        </DialogContent>
      </Dialog>
    );
  }

  const s = statusConfig[invoice.status] ?? { variant: "outline" as const, label: invoice.status };
  const totalPaid = invoice.payments.reduce((sum, p) => sum + Number(p.amount), 0);
  const balance = Number(invoice.total) - totalPaid;

  return (
    <Dialog open={invoiceId !== null} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            {invoice.invoice_number}
            <Badge variant={s.variant} className={s.className}>{s.label}</Badge>
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div>
            <span className="text-muted-foreground">Property:</span>{" "}
            <span className="font-medium">{invoice.property_name}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Client:</span>{" "}
            <span className="font-medium">{invoice.client_name ?? "—"}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Issue Date:</span>{" "}
            {invoice.issue_date}
          </div>
          <div>
            <span className="text-muted-foreground">Due Date:</span>{" "}
            {invoice.due_date}
          </div>
          {invoice.period_start && (
            <div>
              <span className="text-muted-foreground">Period:</span>{" "}
              {invoice.period_start} — {invoice.period_end}
            </div>
          )}
          {invoice.paid_date && (
            <div>
              <span className="text-muted-foreground">Paid Date:</span>{" "}
              {invoice.paid_date}
            </div>
          )}
        </div>

        {invoice.notes && (
          <p className="text-sm text-muted-foreground italic">{invoice.notes}</p>
        )}

        <Separator />

        <div>
          <h4 className="mb-2 text-sm font-medium">Line Items</h4>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Description</TableHead>
                  <TableHead className="w-20 text-right">Qty</TableHead>
                  <TableHead className="w-24 text-right">Unit Price</TableHead>
                  <TableHead className="w-24 text-right">Total</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoice.items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.description}</TableCell>
                    <TableCell className="text-right">{Number(item.quantity)}</TableCell>
                    <TableCell className="text-right">${Number(item.unit_price).toFixed(2)}</TableCell>
                    <TableCell className="text-right">${Number(item.total).toFixed(2)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="mt-3 flex flex-col items-end gap-1 text-sm">
            <div className="flex w-48 justify-between">
              <span className="text-muted-foreground">Subtotal:</span>
              <span>${Number(invoice.subtotal).toFixed(2)}</span>
            </div>
            {Number(invoice.discount) > 0 && (
              <div className="flex w-48 justify-between">
                <span className="text-muted-foreground">Discount:</span>
                <span>-${Number(invoice.discount).toFixed(2)}</span>
              </div>
            )}
            {Number(invoice.tax) > 0 && (
              <div className="flex w-48 justify-between">
                <span className="text-muted-foreground">Tax:</span>
                <span>${Number(invoice.tax).toFixed(2)}</span>
              </div>
            )}
            <div className="flex w-48 justify-between border-t pt-1 font-medium">
              <span>Total:</span>
              <span>${Number(invoice.total).toFixed(2)}</span>
            </div>
          </div>
        </div>

        <Separator />

        <div>
          <div className="mb-2 flex items-center justify-between">
            <h4 className="text-sm font-medium">Payments</h4>
            {invoice.status !== "paid" && invoice.status !== "cancelled" && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onRecordPayment(invoice.id)}
              >
                Record Payment
              </Button>
            )}
          </div>
          {invoice.payments.length > 0 ? (
            <div className="space-y-2">
              {invoice.payments.map((p) => (
                <div key={p.id} className="flex items-center justify-between rounded-md border px-3 py-2 text-sm">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">${Number(p.amount).toFixed(2)}</span>
                    <Badge variant="outline">{methodLabels[p.payment_method] ?? p.payment_method}</Badge>
                  </div>
                  <span className="text-muted-foreground">{p.payment_date}</span>
                </div>
              ))}
              <div className="flex justify-between text-sm font-medium">
                <span>Balance:</span>
                <span className={balance <= 0 ? "text-emerald-600" : "text-destructive"}>
                  ${balance.toFixed(2)}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No payments recorded.</p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
