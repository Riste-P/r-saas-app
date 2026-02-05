import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { useUpdateUser } from "@/hooks/useUsers";
import { roleNameToId } from "@/lib/utils";
import type { UserListItem } from "@/types";
import {
  editUserSchema,
  type EditUserFormValues,
} from "@/lib/schemas";

interface EditUserDialogProps {
  user: UserListItem | null;
  onClose: () => void;
  isSuperadmin: boolean;
}

export function EditUserDialog({
  user,
  onClose,
  isSuperadmin,
}: EditUserDialogProps) {
  const form = useForm<EditUserFormValues>({
    resolver: zodResolver(editUserSchema),
    defaultValues: { role_id: "3", is_active: true },
  });

  const updateMutation = useUpdateUser({
    onSuccess: onClose,
  });

  useEffect(() => {
    if (user) {
      form.reset({
        role_id: roleNameToId(user.role),
        is_active: user.is_active,
      });
    }
  }, [user, form]);

  function onSubmit(values: EditUserFormValues) {
    if (!user) return;
    updateMutation.mutate({
      id: user.id,
      role_id: Number(values.role_id),
      is_active: values.is_active,
    });
  }

  return (
    <Dialog
      open={user !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit User</DialogTitle>
          <DialogDescription>{user?.email}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
            className="space-y-4"
          >
            {isSuperadmin && user && (
              <div className="space-y-2">
                <FormLabel>Tenant</FormLabel>
                <Input value={user.tenant_name} disabled />
              </div>
            )}
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
