import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { useUpdateTenant } from "@/hooks/useTenants";
import type { Tenant } from "@/types";
import {
  editTenantSchema,
  type EditTenantFormValues,
} from "@/lib/schemas";

interface EditTenantDialogProps {
  tenant: Tenant | null;
  onClose: () => void;
}

export function EditTenantDialog({ tenant, onClose }: EditTenantDialogProps) {
  const form = useForm<EditTenantFormValues>({
    resolver: zodResolver(editTenantSchema),
    defaultValues: { name: "", is_active: true },
  });

  const updateMutation = useUpdateTenant({
    onSuccess: onClose,
  });

  useEffect(() => {
    if (tenant) {
      form.reset({ name: tenant.name, is_active: tenant.is_active });
    }
  }, [tenant, form]);

  function onSubmit(values: EditTenantFormValues) {
    if (!tenant) return;
    updateMutation.mutate({
      id: tenant.id,
      name: values.name,
      is_active: values.is_active,
    });
  }

  return (
    <Dialog
      open={tenant !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Tenant</DialogTitle>
          <DialogDescription>{tenant?.slug}</DialogDescription>
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
