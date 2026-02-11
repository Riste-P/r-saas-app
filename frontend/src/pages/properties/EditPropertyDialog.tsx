import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { useUpdateProperty } from "@/hooks/useProperties";
import { useClientsQuery } from "@/hooks/useClients";
import type { Property } from "@/types";
import { editPropertySchema, type EditPropertyFormValues } from "@/lib/schemas";

interface EditPropertyDialogProps {
  property: Property | null;
  onClose: () => void;
}

export function EditPropertyDialog({ property, onClose }: EditPropertyDialogProps) {
  const { data: clients = [] } = useClientsQuery();

  const form = useForm<EditPropertyFormValues>({
    resolver: zodResolver(editPropertySchema),
    defaultValues: {
      client_id: "",
      property_type: "house",
      name: "",
      address: "",
      city: "",
      postal_code: "",
      floor: "",
      access_instructions: "",
      key_code: "",
      contact_name: "",
      contact_phone: "",
      contact_email: "",
      is_active: true,
    },
  });

  const updateMutation = useUpdateProperty({ onSuccess: onClose });

  useEffect(() => {
    if (property) {
      form.reset({
        client_id: property.client_id,
        property_type: property.property_type,
        name: property.name,
        address: property.address,
        city: property.city ?? "",
        postal_code: property.postal_code ?? "",
        size_sqm: property.size_sqm ? String(property.size_sqm) : "",
        num_rooms: property.num_rooms != null ? String(property.num_rooms) : "",
        floor: property.floor ?? "",
        access_instructions: property.access_instructions ?? "",
        key_code: property.key_code ?? "",
        contact_name: property.contact_name ?? "",
        contact_phone: property.contact_phone ?? "",
        contact_email: property.contact_email ?? "",
        is_active: property.is_active,
      });
    }
  }, [property, form]);

  function onSubmit(values: EditPropertyFormValues) {
    if (!property) return;
    updateMutation.mutate({
      id: property.id,
      client_id: values.client_id,
      property_type: values.property_type,
      name: values.name,
      address: values.address,
      city: values.city || undefined,
      postal_code: values.postal_code || undefined,
      size_sqm: values.size_sqm ? Number(values.size_sqm) : undefined,
      num_rooms: values.num_rooms ? Number(values.num_rooms) : undefined,
      floor: values.floor || undefined,
      access_instructions: values.access_instructions || undefined,
      key_code: values.key_code || undefined,
      contact_name: values.contact_name || undefined,
      contact_phone: values.contact_phone || undefined,
      contact_email: values.contact_email || undefined,
      is_active: values.is_active,
    });
  }

  return (
    <Dialog open={property !== null} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit Property</DialogTitle>
          <DialogDescription>{property?.name}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="space-y-4">
            <FormField
              control={form.control}
              name="client_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Client</FormLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <FormControl>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {clients.map((c) => (
                        <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="property_type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Type</FormLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <FormControl>
                      <SelectTrigger><SelectValue /></SelectTrigger>
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
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
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
            <div className="grid grid-cols-2 gap-4">
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
              <FormField
                control={form.control}
                name="postal_code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Postal Code</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="size_sqm"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Size (sqm)</FormLabel>
                    <FormControl><Input type="number" step="0.01" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="num_rooms"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rooms</FormLabel>
                    <FormControl><Input type="number" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="access_instructions"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Access Instructions</FormLabel>
                  <FormControl><Textarea rows={2} {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="key_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Key Code</FormLabel>
                  <FormControl><Input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="is_active"
              render={({ field }) => (
                <FormItem className="flex items-center justify-between">
                  <FormLabel>Active</FormLabel>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />
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
