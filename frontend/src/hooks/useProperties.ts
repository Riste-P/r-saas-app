import { useQuery, useMutation, useQueryClient, skipToken } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as propertyService from "@/services/property.service";
import type { PropertyCreatePayload, PropertyUpdatePayload } from "@/types";

const PROPERTIES_KEY = ["properties"] as const;
const PROPERTY_DETAIL_KEY = ["property"] as const;

export function usePropertiesQuery(params?: {
  client_id?: string;
  property_type?: string;
  parent_property_id?: string;
  parents_only?: boolean;
}) {
  return useQuery({
    queryKey: [...PROPERTIES_KEY, params],
    queryFn: () => propertyService.getProperties(params),
    select: (data) => data.items,
  });
}

export function usePropertyQuery(id: string | null) {
  return useQuery({
    queryKey: [...PROPERTY_DETAIL_KEY, id],
    queryFn: id ? () => propertyService.getProperty(id) : skipToken,
  });
}

export function useCreateProperty(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: PropertyCreatePayload) => propertyService.createProperty(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PROPERTIES_KEY });
      qc.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Property created successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to create property")),
  });
}

export function useUpdateProperty(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & PropertyUpdatePayload) =>
      propertyService.updateProperty(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PROPERTIES_KEY });
      qc.invalidateQueries({ queryKey: PROPERTY_DETAIL_KEY });
      toast.success("Property updated successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update property")),
  });
}

export function useDeleteProperty(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => propertyService.deleteProperty(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PROPERTIES_KEY });
      qc.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Property deleted successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to delete property")),
  });
}
