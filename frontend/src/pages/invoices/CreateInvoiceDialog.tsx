import { useForm, useFieldArray, useWatch, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Trash2 } from "lucide-react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { usePropertiesQuery } from "@/hooks/useProperties";
import { useCreateInvoice } from "@/hooks/useInvoices";
import { useServiceTypesQuery } from "@/hooks/useServiceTypes";
import { createInvoiceSchema, type CreateInvoiceFormValues } from "@/lib/schemas";

interface CreateInvoiceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateInvoiceDialog({ open, onOpenChange }: CreateInvoiceDialogProps) {
  const { data: properties = [] } = usePropertiesQuery();
  const { data: serviceTypes = [] } = useServiceTypesQuery();

  const form = useForm<CreateInvoiceFormValues>({
    resolver: zodResolver(createInvoiceSchema) as Resolver<CreateInvoiceFormValues>,
    defaultValues: {
      property_id: "",
      issue_date: new Date().toISOString().slice(0, 10),
      due_date: "",
      period_start: "",
      period_end: "",
      discount: 0,
      tax: 0,
      notes: "",
      items: [{ service_type_id: "", description: "", quantity: 1, unit_price: 0, sort_order: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "items",
  });

  const createMutation = useCreateInvoice({
    onSuccess: () => {
      onOpenChange(false);
      form.reset();
    },
  });

  const watchedItems = useWatch({ control: form.control, name: "items" });
  const watchedDiscount = useWatch({ control: form.control, name: "discount" });
  const watchedTax = useWatch({ control: form.control, name: "tax" });

  const subtotal = (watchedItems ?? []).reduce(
    (sum, item) => sum + (Number(item?.quantity) || 0) * (Number(item?.unit_price) || 0),
    0
  );
  const total = subtotal - (Number(watchedDiscount) || 0) + (Number(watchedTax) || 0);

  function handleServiceTypeChange(index: number, serviceTypeId: string) {
    if (serviceTypeId && serviceTypeId !== "custom") {
      const st = serviceTypes.find((s) => s.id === serviceTypeId);
      if (st) {
        form.setValue(`items.${index}.description`, st.name);
        form.setValue(`items.${index}.unit_price`, Number(st.base_price));
      }
    }
    form.setValue(`items.${index}.service_type_id`, serviceTypeId === "custom" ? "" : serviceTypeId);
  }

  function onSubmit(values: CreateInvoiceFormValues) {
    createMutation.mutate({
      property_id: values.property_id,
      issue_date: values.issue_date,
      due_date: values.due_date,
      period_start: values.period_start || undefined,
      period_end: values.period_end || undefined,
      discount: values.discount,
      tax: values.tax,
      notes: values.notes || undefined,
      items: values.items.map((item, i) => ({
        service_type_id: item.service_type_id || undefined,
        description: item.description,
        quantity: item.quantity,
        unit_price: item.unit_price,
        sort_order: i,
      })),
    });
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Invoice</DialogTitle>
          <DialogDescription>Create a new invoice with line items</DialogDescription>
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
                      options={properties.map((p) => ({
                        value: p.id,
                        label: `${p.name}${p.client_name ? ` (${p.client_name})` : ""}`,
                      }))}
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

            <div>
              <div className="mb-2 flex items-center justify-between">
                <FormLabel>Line Items</FormLabel>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => append({ service_type_id: "", description: "", quantity: 1, unit_price: 0, sort_order: fields.length })}
                >
                  <Plus className="mr-1 size-3.5" />
                  Add Item
                </Button>
              </div>
              {form.formState.errors.items?.root && (
                <p className="mb-2 text-sm text-destructive">{form.formState.errors.items.root.message}</p>
              )}
              <div className="space-y-3">
                {fields.map((field, index) => (
                  <div key={field.id} className="rounded-md border p-3 space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="flex-1">
                        <Select
                          value={form.getValues(`items.${index}.service_type_id`) || "custom"}
                          onValueChange={(val) => handleServiceTypeChange(index, val)}
                        >
                          <SelectTrigger className="h-8 text-xs">
                            <SelectValue placeholder="Service type (optional)" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="custom">Custom item</SelectItem>
                            {serviceTypes.filter((s) => s.is_active).map((st) => (
                              <SelectItem key={st.id} value={st.id}>
                                {st.name} — ${Number(st.base_price).toFixed(2)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      {fields.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon-xs"
                          onClick={() => remove(index)}
                        >
                          <Trash2 className="size-3.5 text-destructive" />
                        </Button>
                      )}
                    </div>
                    <FormField
                      control={form.control}
                      name={`items.${index}.description`}
                      render={({ field: f }) => (
                        <FormItem>
                          <FormControl>
                            <Input placeholder="Description" {...f} value={f.value ?? ""} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <div className="grid grid-cols-2 gap-2">
                      <FormField
                        control={form.control}
                        name={`items.${index}.quantity`}
                        render={({ field: f }) => (
                          <FormItem>
                            <FormControl>
                              <Input type="number" step="0.01" min="0" placeholder="Qty" {...f} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name={`items.${index}.unit_price`}
                        render={({ field: f }) => (
                          <FormItem>
                            <FormControl>
                              <Input type="number" step="0.01" min="0" placeholder="Unit Price ($)" {...f} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                ))}
              </div>
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

            <div className="flex flex-col items-end gap-1 text-sm">
              <div className="flex w-48 justify-between">
                <span className="text-muted-foreground">Subtotal:</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex w-48 justify-between border-t pt-1 font-medium">
                <span>Total:</span>
                <span>${total.toFixed(2)}</span>
              </div>
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
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create Invoice"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
