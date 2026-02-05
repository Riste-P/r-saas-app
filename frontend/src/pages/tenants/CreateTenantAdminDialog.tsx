import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { useCreateTenantAdmin } from "@/hooks/useTenants";
import {
  createTenantAdminSchema,
  type CreateTenantAdminFormValues,
} from "@/lib/schemas";

interface CreateTenantAdminDialogProps {
  tenantId: string | null;
  onClose: () => void;
}

export function CreateTenantAdminDialog({
  tenantId,
  onClose,
}: CreateTenantAdminDialogProps) {
  const form = useForm<CreateTenantAdminFormValues>({
    resolver: zodResolver(createTenantAdminSchema),
    defaultValues: { email: "", password: "" },
  });

  const createAdminMutation = useCreateTenantAdmin({
    onSuccess: () => {
      onClose();
      form.reset();
    },
  });

  function onSubmit(values: CreateTenantAdminFormValues) {
    if (!tenantId) return;
    createAdminMutation.mutate({
      email: values.email,
      password: values.password,
      role_id: 2,
      tenant_id: tenantId,
    });
  }

  return (
    <Dialog
      open={tenantId !== null}
      onOpenChange={(open) => {
        if (!open) {
          onClose();
          form.reset();
        }
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Admin User</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
            className="space-y-4"
          >
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input type="email" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input type="password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="submit" disabled={createAdminMutation.isPending}>
                {createAdminMutation.isPending
                  ? "Creating..."
                  : "Create Admin"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
