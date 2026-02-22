import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { SearchableSelect } from "@/components/ui/searchable-select";
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
import { useCreateProperty, usePropertyQuery } from "@/hooks/useProperties";
import { useClientsQuery } from "@/hooks/useClients";
import {
  createPropertySchema,
  type CreatePropertyFormValues,
} from "@/lib/schemas";

interface AddUnitDialogProps {
  parentPropertyId: string | null;
  onClose: () => void;
}

export function AddUnitDialog({ parentPropertyId, onClose }: AddUnitDialogProps) {
  const { data: parent } = usePropertyQuery(parentPropertyId);
  const { data: clients = [] } = useClientsQuery();

  const form = useForm<CreatePropertyFormValues>({
    resolver: zodResolver(createPropertySchema),
    defaultValues: {
      client_id: "none",
      parent_property_id: "none",
      property_type: "unit",
      name: "",
      address: "",
      city: "",
      notes: "",
    },
  });

  useEffect(() => {
    if (parent) {
      form.reset({
        client_id: parent.client_id ?? "none",
        parent_property_id: parent.id,
        property_type: "unit",
        name: "",
        address: parent.address ?? "",
        city: parent.city ?? "",
        notes: "",
      });
    }
  }, [parent, form]);

  const createMutation = useCreateProperty({
    onSuccess: () => {
      onClose();
      form.reset();
    },
  });

  function onSubmit(values: CreatePropertyFormValues) {
    createMutation.mutate({
      client_id: values.client_id && values.client_id !== "none" ? values.client_id : undefined,
      parent_property_id: parentPropertyId ?? undefined,
      property_type: "unit",
      name: values.name,
      address: values.address || undefined,
      city: values.city || undefined,
      notes: values.notes || undefined,
    });
  }

  return (
    <Dialog open={parentPropertyId !== null} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Add Unit</DialogTitle>
          <DialogDescription>{parent?.name}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Address</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>City</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
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
                  <FormControl><Textarea rows={2} {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <FormItem>
                <FormLabel>Type</FormLabel>
                <Input value="Unit" disabled />
              </FormItem>
              <FormField
                control={form.control}
                name="client_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Client</FormLabel>
                    <SearchableSelect
                      options={[
                        { value: "none", label: "No client" },
                        ...clients
                          .filter((c) => c.is_active)
                          .map((c) => ({ value: c.id, label: c.name })),
                      ]}
                      value={field.value ?? "none"}
                      onValueChange={field.onChange}
                      placeholder="No client"
                      searchPlaceholder="Search clients..."
                    />
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormItem>
              <FormLabel>Part of</FormLabel>
              <Input value={parent?.name ?? ""} disabled />
            </FormItem>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create Unit"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
