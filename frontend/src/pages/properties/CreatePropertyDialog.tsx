import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
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
import { useCreateProperty } from "@/hooks/useProperties";
import { useClientsQuery } from "@/hooks/useClients";
import { usePropertiesQuery } from "@/hooks/useProperties";
import {
  createPropertySchema,
  type CreatePropertyFormValues,
} from "@/lib/schemas";

interface CreatePropertyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreatePropertyDialog({ open, onOpenChange }: CreatePropertyDialogProps) {
  const { data: clients = [] } = useClientsQuery();
  const { data: allProperties = [] } = usePropertiesQuery();

  const form = useForm<CreatePropertyFormValues>({
    resolver: zodResolver(createPropertySchema),
    defaultValues: {
      client_id: "none",
      parent_property_id: "none",
      property_type: "building",
      name: "",
      address: "",
      city: "",
      notes: "",
    },
  });

  const propertyType = useWatch({ control: form.control, name: "property_type" });

  const createMutation = useCreateProperty({
    onSuccess: () => {
      onOpenChange(false);
      form.reset();
    },
  });

  function onSubmit(values: CreatePropertyFormValues) {
    createMutation.mutate({
      client_id: values.client_id && values.client_id !== "none" ? values.client_id : undefined,
      parent_property_id: values.parent_property_id && values.parent_property_id !== "none" ? values.parent_property_id : undefined,
      property_type: values.property_type,
      name: values.name,
      address: values.address || undefined,
      city: values.city || undefined,
      notes: values.notes || undefined,
      number_of_apartments:
        values.property_type === "building" && values.number_of_apartments
          ? values.number_of_apartments
          : undefined,
    });
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        onOpenChange(o);
        if (!o) form.reset();
      }}
    >
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Create Property</DialogTitle>
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
              <FormField
                control={form.control}
                name="property_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Type</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
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
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger className="w-full"><SelectValue placeholder="No client" /></SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="none">No client</SelectItem>
                        {clients.filter((c) => c.is_active).map((c) => (
                          <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            {propertyType === "building" && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="number_of_apartments"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Number of Apartments</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            min={1}
                            max={100}
                            placeholder="e.g. 10"
                            value={field.value ?? ""}
                            onChange={(e) => {
                              const val = e.target.valueAsNumber;
                              field.onChange(isNaN(val) ? undefined : val);
                            }}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <p className="text-muted-foreground flex items-start gap-1.5 text-sm">
                  <Info className="mt-0.5 size-4 shrink-0" />
                  Apartments will be auto-created and linked to this building with the same address and client.
                </p>
              </>
            )}
            {propertyType === "apartment" && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="parent_property_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Part of</FormLabel>
                        <Select value={field.value} onValueChange={field.onChange}>
                          <FormControl>
                            <SelectTrigger className="w-full"><SelectValue placeholder="None" /></SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="none">None</SelectItem>
                            {allProperties.filter((p) => p.is_active && p.property_type !== "apartment").map((p) => (
                              <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
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

            <DialogFooter>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
