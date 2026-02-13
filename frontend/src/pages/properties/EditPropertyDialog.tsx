import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { Info } from "lucide-react";
import { useUpdateProperty, usePropertyQuery, usePropertiesQuery } from "@/hooks/useProperties";
import { useClientsQuery } from "@/hooks/useClients";
import { editPropertySchema, type EditPropertyFormValues } from "@/lib/schemas";

interface EditPropertyDialogProps {
  propertyId: string | null;
  onClose: () => void;
}

export function EditPropertyDialog({ propertyId, onClose }: EditPropertyDialogProps) {
  const { data: property } = usePropertyQuery(propertyId);
  const { data: clients = [] } = useClientsQuery();
  const { data: allProperties = [] } = usePropertiesQuery();

  const form = useForm<EditPropertyFormValues>({
    resolver: zodResolver(editPropertySchema),
    defaultValues: {
      client_id: "none",
      parent_property_id: "none",
      property_type: "house",
      name: "",
      address: "",
      city: "",
      notes: "",
      is_active: true,
    },
  });

  const updateMutation = useUpdateProperty({ onSuccess: onClose });
  const propertyType = useWatch({ control: form.control, name: "property_type" });

  useEffect(() => {
    if (property) {
      form.reset({
        client_id: property.client_id ?? "none",
        parent_property_id: property.parent_property_id ?? "none",
        property_type: property.property_type,
        name: property.name,
        address: property.address ?? "",
        city: property.city ?? "",
        notes: property.notes ?? "",
        is_active: property.is_active,
      });
    }
  }, [property, form]);

  function onSubmit(values: EditPropertyFormValues) {
    if (!propertyId) return;
    updateMutation.mutate({
      id: propertyId,
      client_id: values.client_id && values.client_id !== "none" ? values.client_id : null,
      parent_property_id: values.property_type === "apartment" && values.parent_property_id && values.parent_property_id !== "none" ? values.parent_property_id : null,
      property_type: values.property_type,
      name: values.name,
      address: values.address || undefined,
      city: values.city || undefined,
      notes: values.notes || undefined,
      is_active: values.is_active,
    });
  }

  return (
    <Dialog open={propertyId !== null} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Edit Property</DialogTitle>
          <DialogDescription>{property?.name}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl><Input {...field} value={field.value ?? ""} /></FormControl>
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
                    <FormControl><Input {...field} value={field.value ?? ""} /></FormControl>
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
                    <FormControl><Input {...field} value={field.value ?? ""} /></FormControl>
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
                  <FormControl><Textarea rows={2} {...field} value={field.value ?? ""} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="property_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Type</FormLabel>
                    <Select value={field.value ?? "house"} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="house">House</SelectItem>
                        <SelectItem value="apartment">Apartment</SelectItem>
                        <SelectItem value="building">Building</SelectItem>
                        <SelectItem value="commercial">Commercial</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="client_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Client</FormLabel>
                    <SearchableSelect
                      options={[
                        { value: "none", label: "No client" },
                        ...clients.map((c) => ({ value: c.id, label: c.name })),
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
            {propertyType === "apartment" && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="parent_property_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Part of</FormLabel>
                        <SearchableSelect
                          options={[
                            { value: "none", label: "None" },
                            ...allProperties
                              .filter((p) => p.is_active && p.id !== propertyId && p.property_type !== "apartment")
                              .map((p) => ({ value: p.id, label: p.name })),
                          ]}
                          value={field.value ?? "none"}
                          onValueChange={field.onChange}
                          placeholder="None"
                          searchPlaceholder="Search properties..."
                        />
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <p className="text-muted-foreground flex items-start gap-1.5 text-sm">
                  <Info className="mt-0.5 size-4 shrink-0" />
                  Link this apartment to a building or property it belongs to.
                </p>
              </>
            )}

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex items-center gap-3">
                    <FormLabel>Active</FormLabel>
                    <FormControl>
                      <Switch checked={field.value ?? true} onCheckedChange={field.onChange} />
                    </FormControl>
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? "Saving..." : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
