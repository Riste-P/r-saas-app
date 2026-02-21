import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { usePropertiesQuery } from "@/hooks/useProperties";
import { useGenerateInvoices } from "@/hooks/useInvoices";
import { generateInvoicesSchema, type GenerateInvoicesFormValues } from "@/lib/schemas";

interface GenerateInvoicesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GenerateInvoicesDialog({ open, onOpenChange }: GenerateInvoicesDialogProps) {
  const { data: properties = [] } = usePropertiesQuery({ parents_only: true });

  const form = useForm<GenerateInvoicesFormValues>({
    resolver: zodResolver(generateInvoicesSchema) as Resolver<GenerateInvoicesFormValues>,
    defaultValues: {
      property_id: "",
      issue_date: new Date().toISOString().slice(0, 10),
      due_date: "",
      period_start: "",
      period_end: "",
      discount: 0,
      tax: 0,
      notes: "",
    },
  });

  const generateMutation = useGenerateInvoices({
    onSuccess: () => {
      onOpenChange(false);
      form.reset();
    },
  });

  function onSubmit(values: GenerateInvoicesFormValues) {
    generateMutation.mutate({
      property_id: values.property_id,
      issue_date: values.issue_date,
      due_date: values.due_date,
      period_start: values.period_start || undefined,
      period_end: values.period_end || undefined,
      discount: values.discount,
      tax: values.tax,
      notes: values.notes || undefined,
    });
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate Invoices</DialogTitle>
          <DialogDescription>
            Generate invoices from assigned services. For properties with children,
            one invoice per child will be created. For standalone properties, a single invoice is created.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="space-y-4">
            <FormField
              control={form.control}
              name="property_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Property</FormLabel>
                  <FormControl>
                    <SearchableSelect
                      options={properties.map((p) => {
                        const childCount = p.child_properties?.length ?? 0;
                        const suffix = childCount > 0 ? ` (${childCount} units)` : "";
                        return {
                          value: p.id,
                          label: `${p.name}${suffix}`,
                        };
                      })}
                      value={field.value}
                      onValueChange={field.onChange}
                      placeholder="Select property"
                      searchPlaceholder="Search properties..."
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="issue_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Issue Date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} value={field.value ?? ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="due_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Due Date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} value={field.value ?? ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="period_start"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Period Start (optional)</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} value={field.value ?? ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="period_end"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Period End (optional)</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} value={field.value ?? ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="discount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Discount ($)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.01" min="0" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tax"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tax ($)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.01" min="0" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea rows={2} {...field} value={field.value ?? ""} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={generateMutation.isPending}>
                {generateMutation.isPending ? "Generating..." : "Generate Invoices"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
