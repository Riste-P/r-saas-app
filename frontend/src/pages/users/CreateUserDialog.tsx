import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { useCreateUser } from "@/hooks/useUsers";
import { useTenantsQuery } from "@/hooks/useTenants";
import {
  createUserSchema,
  createUserSuperadminSchema,
  type CreateUserFormValues,
} from "@/lib/schemas";

interface CreateUserDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isSuperadmin: boolean;
}

export function CreateUserDialog({
  open,
  onOpenChange,
  isSuperadmin,
}: CreateUserDialogProps) {
  const { data: tenants = [] } = useTenantsQuery(isSuperadmin);

  const form = useForm<CreateUserFormValues>({
    resolver: zodResolver(
      isSuperadmin ? createUserSuperadminSchema : createUserSchema
    ),
    defaultValues: { email: "", password: "", role_id: "3", tenant_id: "" },
  });

  const createMutation = useCreateUser({
    onSuccess: () => {
      onOpenChange(false);
      form.reset();
    },
  });

  function onSubmit(values: CreateUserFormValues) {
    createMutation.mutate({
      email: values.email,
      password: values.password,
      role_id: Number(values.role_id),
      ...(isSuperadmin && values.tenant_id
        ? { tenant_id: values.tenant_id }
        : {}),
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
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create User</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
            className="space-y-4"
          >
            {isSuperadmin && (
              <FormField
                control={form.control}
                name="tenant_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tenant</FormLabel>
                    <Select
                      value={field.value}
                      onValueChange={field.onChange}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a tenant" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {tenants.map((t) => (
                          <SelectItem key={t.id} value={t.id}>
                            {t.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
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
            <FormField
              control={form.control}
              name="role_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Role</FormLabel>
                  <Select
                    value={field.value}
                    onValueChange={field.onChange}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="2">admin</SelectItem>
                      <SelectItem value="3">user</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
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
