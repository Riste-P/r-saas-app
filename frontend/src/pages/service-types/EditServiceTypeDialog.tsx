import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
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
import { useUpdateServiceType } from "@/hooks/useServiceTypes";
import type { ServiceType } from "@/types";
import {
  editServiceTypeSchema,
  type EditServiceTypeFormValues,
} from "@/lib/schemas";

interface EditServiceTypeDialogProps {
  serviceType: ServiceType | null;
  onClose: () => void;
}

export function EditServiceTypeDialog({
  serviceType,
  onClose,
}: EditServiceTypeDialogProps) {
  const form = useForm<EditServiceTypeFormValues>({
    resolver: zodResolver(editServiceTypeSchema),
    defaultValues: {
      name: "",
      description: "",
      base_price: 0,
      estimated_duration_minutes: 60,
      is_active: true,
    },
  });

  const updateMutation = useUpdateServiceType({
    onSuccess: onClose,
  });

  useEffect(() => {
    if (serviceType) {
      form.reset({
        name: serviceType.name,
        description: serviceType.description ?? "",
        base_price: Number(serviceType.base_price),
        estimated_duration_minutes: serviceType.estimated_duration_minutes,
        is_active: serviceType.is_active,
      });
    }
  }, [serviceType, form]);

  function onSubmit(values: EditServiceTypeFormValues) {
    if (!serviceType) return;
    updateMutation.mutate({
      id: serviceType.id,
      name: values.name,
      description: values.description || undefined,
      base_price: values.base_price,
      estimated_duration_minutes: values.estimated_duration_minutes,
      is_active: values.is_active,
    });
  }

  return (
    <Dialog
      open={serviceType !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Service Type</DialogTitle>
          <DialogDescription>{serviceType?.name}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
            className="space-y-4"
          >
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea rows={2} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="base_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Base Price ($)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.01" min="0" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="estimated_duration_minutes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Duration (min)</FormLabel>
                    <FormControl>
                      <Input type="number" min="1" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="is_active"
              render={({ field }) => (
                <FormItem className="flex items-center justify-between">
                  <FormLabel>Active</FormLabel>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
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
