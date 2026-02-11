import { useForm, useFieldArray, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Trash2, GripVertical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  FormMessage,
} from "@/components/ui/form";
import { useUpdateChecklist } from "@/hooks/useServiceTypes";
import type { ServiceType } from "@/types";
import {
  checklistEditorSchema,
  type ChecklistEditorFormValues,
} from "@/lib/schemas";
import { useEffect } from "react";

interface ChecklistEditorProps {
  serviceType: ServiceType | null;
  onClose: () => void;
}

export function ChecklistEditor({
  serviceType,
  onClose,
}: ChecklistEditorProps) {
  const form = useForm<ChecklistEditorFormValues>({
    resolver: zodResolver(checklistEditorSchema) as Resolver<ChecklistEditorFormValues>,
    defaultValues: { items: [] },
  });

  const { fields, append, remove, move } = useFieldArray({
    control: form.control,
    name: "items",
  });

  const updateMutation = useUpdateChecklist({
    onSuccess: onClose,
  });

  useEffect(() => {
    if (serviceType) {
      form.reset({
        items: serviceType.checklist_items.map((item) => ({
          name: item.name,
          description: item.description ?? "",
          sort_order: item.sort_order,
        })),
      });
    }
  }, [serviceType, form]);

  function onSubmit(values: ChecklistEditorFormValues) {
    if (!serviceType) return;
    updateMutation.mutate({
      id: serviceType.id,
      items: values.items.map((item, index) => ({
        name: item.name,
        description: item.description || undefined,
        sort_order: index,
      })),
    });
  }

  function moveItem(index: number, direction: "up" | "down") {
    const newIndex = direction === "up" ? index - 1 : index + 1;
    if (newIndex >= 0 && newIndex < fields.length) {
      move(index, newIndex);
    }
  }

  return (
    <Dialog
      open={serviceType !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Manage Checklist</DialogTitle>
          <DialogDescription>{serviceType?.name}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
            className="space-y-4"
          >
            <div className="space-y-2">
              {fields.length === 0 && (
                <p className="py-4 text-center text-sm text-muted-foreground">
                  No checklist items yet. Add one below.
                </p>
              )}
              {fields.map((field, index) => (
                <div key={field.id} className="flex items-center gap-2">
                  <div className="flex flex-col">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-xs"
                      disabled={index === 0}
                      onClick={() => moveItem(index, "up")}
                    >
                      <GripVertical className="size-3 rotate-90" />
                    </Button>
                  </div>
                  <div className="flex-1">
                    <FormField
                      control={form.control}
                      name={`items.${index}.name`}
                      render={({ field }) => (
                        <FormItem>
                          <FormControl>
                            <Input placeholder="Item name" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-xs"
                    onClick={() => remove(index)}
                  >
                    <Trash2 className="size-3" />
                  </Button>
                </div>
              ))}
            </div>

            <Button
              type="button"
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() =>
                append({ name: "", description: "", sort_order: fields.length })
              }
            >
              <Plus className="mr-1 size-3" />
              Add Item
            </Button>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? "Saving..." : "Save Checklist"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
