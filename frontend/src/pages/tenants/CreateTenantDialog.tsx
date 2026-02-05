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
import { useCreateTenant } from "@/hooks/useTenants";
import { deriveSlug } from "@/lib/utils";
import {
  createTenantSchema,
  type CreateTenantFormValues,
} from "@/lib/schemas";

interface CreateTenantDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateTenantDialog({
  open,
  onOpenChange,
}: CreateTenantDialogProps) {
  const form = useForm<CreateTenantFormValues>({
    resolver: zodResolver(createTenantSchema),
    defaultValues: { name: "", slug: "" },
  });

  const createMutation = useCreateTenant({
    onSuccess: () => {
      onOpenChange(false);
      form.reset();
    },
  });

  function onSubmit(values: CreateTenantFormValues) {
    createMutation.mutate({ name: values.name, slug: values.slug });
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
          <DialogTitle>Create Tenant</DialogTitle>
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
                    <Input
                      {...field}
                      onChange={(e) => {
                        field.onChange(e);
                        form.setValue("slug", deriveSlug(e.target.value), {
                          shouldValidate: form.formState.isSubmitted,
                        });
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="slug"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Slug</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
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
