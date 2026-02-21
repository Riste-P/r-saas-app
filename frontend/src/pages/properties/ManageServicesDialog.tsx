import { useState } from "react";
import { Pencil, Plus, Trash2, ArrowDownLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  usePropertyServiceTypesQuery,
  useEffectiveServicesQuery,
  useAssignService,
  useUpdateAssignment,
  useRemoveAssignment,
} from "@/hooks/usePropertyServiceTypes";
import { useServiceTypesQuery } from "@/hooks/useServiceTypes";
import { usePropertyQuery } from "@/hooks/useProperties";
import type { PropertyServiceType, EffectiveService } from "@/types";

interface ManageServicesDialogProps {
  propertyId: string | null;
  onClose: () => void;
}

export function ManageServicesDialog({ propertyId, onClose }: ManageServicesDialogProps) {
  const { data: property } = usePropertyQuery(propertyId);
  const { data: assignments = [] } = usePropertyServiceTypesQuery(propertyId);
  const { data: effectiveServices = [], isLoading } = useEffectiveServicesQuery(propertyId);
  const { data: allServiceTypes = [] } = useServiceTypesQuery();

  const hasParent = !!property?.parent_property_id;

  // Build a map from service_type_id to direct assignment for mutation operations
  const assignmentByServiceType = new Map(
    assignments.map((a) => [a.service_type_id, a]),
  );

  // For parent properties: use direct assignments (no inheritance to show)
  // For child properties: use effective services (shows inherited + overrides)
  const effectiveIds = new Set(effectiveServices.map((e) => e.service_type_id));
  const assignedIds = hasParent ? effectiveIds : new Set(assignments.map((a) => a.service_type_id));

  const availableServiceTypes = allServiceTypes.filter(
    (st) => st.is_active && !assignedIds.has(st.id),
  );

  return (
    <Dialog open={propertyId !== null} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Manage Services</DialogTitle>
          <DialogDescription>
            {property?.name ?? "Property"} — assign service types and set custom prices.
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <p className="py-4 text-center text-sm text-muted-foreground">Loading...</p>
        ) : (
          <div className="space-y-3">
            {hasParent ? (
              // Child property: show effective services (inherited + direct)
              <>
                {effectiveServices.length === 0 && (
                  <p className="py-2 text-center text-sm text-muted-foreground">
                    No services assigned yet.
                  </p>
                )}
                {effectiveServices.map((es) => (
                  <EffectiveServiceRow
                    key={es.service_type_id}
                    service={es}
                    assignment={assignmentByServiceType.get(es.service_type_id) ?? null}
                    propertyId={propertyId!}
                  />
                ))}
              </>
            ) : (
              // Parent/standalone: show direct assignments
              <>
                {assignments.length === 0 && (
                  <p className="py-2 text-center text-sm text-muted-foreground">
                    No services assigned yet.
                  </p>
                )}
                {assignments.map((assignment) => (
                  <DirectServiceRow key={assignment.id} assignment={assignment} />
                ))}
              </>
            )}

            <Separator />

            <AddServiceRow
              propertyId={propertyId!}
              availableServiceTypes={availableServiceTypes}
            />
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

/** Row for direct assignments (parent/standalone properties) */
function DirectServiceRow({ assignment }: { assignment: PropertyServiceType }) {
  const [editing, setEditing] = useState(false);
  const [customPrice, setCustomPrice] = useState(assignment.custom_price ?? "");
  const updateMutation = useUpdateAssignment({ onSuccess: () => setEditing(false) });
  const removeMutation = useRemoveAssignment();

  function handleSavePrice() {
    const value = customPrice === "" ? null : Number(customPrice);
    updateMutation.mutate({ id: assignment.id, custom_price: value });
  }

  function handleToggleActive() {
    updateMutation.mutate({ id: assignment.id, is_active: !assignment.is_active });
  }

  return (
    <div className="flex items-center gap-3 rounded-md border px-3 py-2">
      <div className="min-w-0 flex-1">
        <span className="truncate text-sm font-medium">{assignment.service_type_name}</span>
        {editing ? (
          <div className="mt-1.5 flex items-center gap-2">
            <Input
              type="number"
              step="0.01"
              min="0"
              placeholder="Base price"
              value={customPrice}
              onChange={(e) => setCustomPrice(e.target.value)}
              className="h-7 w-28 text-sm"
            />
            <Button
              size="sm"
              variant="outline"
              className="h-7"
              onClick={handleSavePrice}
              disabled={updateMutation.isPending}
            >
              Save
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-7"
              onClick={() => {
                setEditing(false);
                setCustomPrice(assignment.custom_price ?? "");
              }}
            >
              Cancel
            </Button>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">
            ${Number(assignment.effective_price).toFixed(2)}
            {assignment.custom_price !== null && " (custom)"}
          </p>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-1">
        <Switch
          checked={assignment.is_active}
          onCheckedChange={handleToggleActive}
          disabled={updateMutation.isPending}
          aria-label="Toggle active"
        />
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={() => setEditing(!editing)}
          aria-label="Edit price"
        >
          <Pencil className="size-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={() => removeMutation.mutate(assignment.id)}
          disabled={removeMutation.isPending}
          aria-label="Remove service"
        >
          <Trash2 className="size-3.5 text-destructive" />
        </Button>
      </div>
    </div>
  );
}

/** Row for effective services on child properties (shows inheritance) */
function EffectiveServiceRow({
  service,
  assignment,
  propertyId,
}: {
  service: EffectiveService;
  assignment: PropertyServiceType | null;
  propertyId: string;
}) {
  const [editing, setEditing] = useState(false);
  const [customPrice, setCustomPrice] = useState(assignment?.custom_price ?? "");
  const updateMutation = useUpdateAssignment({ onSuccess: () => setEditing(false) });
  const removeMutation = useRemoveAssignment();
  const assignMutation = useAssignService({ onSuccess: () => setEditing(false) });

  const hasOverride = assignment !== null;

  function handleSavePrice() {
    const value = customPrice === "" ? null : Number(customPrice);
    if (hasOverride) {
      updateMutation.mutate({ id: assignment.id, custom_price: value });
    } else {
      // Create an override on the child
      assignMutation.mutate({
        property_id: propertyId,
        service_type_id: service.service_type_id,
        custom_price: value,
      });
    }
  }

  function handleToggleActive() {
    if (hasOverride) {
      updateMutation.mutate({ id: assignment.id, is_active: !service.is_active });
    } else {
      // Create an opt-out override on the child with is_active=false
      assignMutation.mutate({
        property_id: propertyId,
        service_type_id: service.service_type_id,
        is_active: false,
      });
    }
  }

  function handleRemoveOverride() {
    if (hasOverride) {
      removeMutation.mutate(assignment.id);
    }
  }

  const isPending = updateMutation.isPending || assignMutation.isPending;

  return (
    <div className="flex items-center gap-3 rounded-md border px-3 py-2">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-medium">{service.service_type_name}</span>
          {service.is_inherited && (
            <Badge variant="outline" className="gap-1 text-xs">
              <ArrowDownLeft className="size-3" />
              Inherited
            </Badge>
          )}
          {hasOverride && service.is_inherited && (
            <Badge variant="secondary" className="text-xs">
              Override
            </Badge>
          )}
        </div>

        {editing ? (
          <div className="mt-1.5 flex items-center gap-2">
            <Input
              type="number"
              step="0.01"
              min="0"
              placeholder="Base price"
              value={customPrice}
              onChange={(e) => setCustomPrice(e.target.value)}
              className="h-7 w-28 text-sm"
            />
            <Button
              size="sm"
              variant="outline"
              className="h-7"
              onClick={handleSavePrice}
              disabled={isPending}
            >
              Save
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-7"
              onClick={() => {
                setEditing(false);
                setCustomPrice(assignment?.custom_price ?? "");
              }}
            >
              Cancel
            </Button>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">
            ${Number(service.effective_price).toFixed(2)}
            {hasOverride && assignment.custom_price !== null && " (custom)"}
          </p>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-1">
        <Switch
          checked={service.is_active}
          onCheckedChange={handleToggleActive}
          disabled={isPending}
          aria-label="Toggle active"
        />
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={() => setEditing(!editing)}
          aria-label="Edit price"
        >
          <Pencil className="size-3.5" />
        </Button>
        {hasOverride && service.is_inherited && (
          <Button
            variant="ghost"
            size="icon-xs"
            onClick={handleRemoveOverride}
            disabled={removeMutation.isPending}
            aria-label="Remove override"
            title="Remove override (revert to parent)"
          >
            <Trash2 className="size-3.5 text-destructive" />
          </Button>
        )}
        {!service.is_inherited && hasOverride && (
          <Button
            variant="ghost"
            size="icon-xs"
            onClick={handleRemoveOverride}
            disabled={removeMutation.isPending}
            aria-label="Remove service"
          >
            <Trash2 className="size-3.5 text-destructive" />
          </Button>
        )}
      </div>
    </div>
  );
}

interface AddServiceRowProps {
  propertyId: string;
  availableServiceTypes: { id: string; name: string; base_price: string }[];
}

function AddServiceRow({ propertyId, availableServiceTypes }: AddServiceRowProps) {
  const [selectedId, setSelectedId] = useState("");
  const assignMutation = useAssignService({
    onSuccess: () => setSelectedId(""),
  });

  if (availableServiceTypes.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      <SearchableSelect
        options={availableServiceTypes.map((st) => ({
          value: st.id,
          label: `${st.name} ($${Number(st.base_price).toFixed(2)})`,
        }))}
        value={selectedId}
        onValueChange={setSelectedId}
        placeholder="Add a service..."
        searchPlaceholder="Search service types..."
        className="flex-1"
      />
      <Button
        size="sm"
        onClick={() => {
          if (selectedId) {
            assignMutation.mutate({ property_id: propertyId, service_type_id: selectedId });
          }
        }}
        disabled={!selectedId || assignMutation.isPending}
      >
        <Plus className="mr-1 size-4" />
        Add
      </Button>
    </div>
  );
}
