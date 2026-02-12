import { useQuery, useMutation, useQueryClient, skipToken } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as serviceTypeService from "@/services/serviceType.service";
import type { ServiceTypeCreatePayload, ServiceTypeUpdatePayload, ChecklistUpdatePayload } from "@/types";

const SERVICE_TYPES_KEY = ["service-types"] as const;
const SERVICE_TYPE_DETAIL_KEY = ["service-type"] as const;

export function useServiceTypesQuery() {
  return useQuery({
    queryKey: SERVICE_TYPES_KEY,
    queryFn: serviceTypeService.getServiceTypes,
    select: (data) => data.items,
  });
}

export function useServiceTypeQuery(id: string | null) {
  return useQuery({
    queryKey: [...SERVICE_TYPE_DETAIL_KEY, id],
    queryFn: id ? () => serviceTypeService.getServiceType(id) : skipToken,
  });
}

export function useCreateServiceType(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ServiceTypeCreatePayload) => serviceTypeService.createServiceType(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: SERVICE_TYPES_KEY });
      toast.success("Service type created successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to create service type")),
  });
}

export function useUpdateServiceType(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & ServiceTypeUpdatePayload) =>
      serviceTypeService.updateServiceType(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: SERVICE_TYPES_KEY });
      qc.invalidateQueries({ queryKey: SERVICE_TYPE_DETAIL_KEY });
      toast.success("Service type updated successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update service type")),
  });
}

export function useUpdateChecklist(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & ChecklistUpdatePayload) =>
      serviceTypeService.updateChecklist(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: SERVICE_TYPES_KEY });
      qc.invalidateQueries({ queryKey: SERVICE_TYPE_DETAIL_KEY });
      toast.success("Checklist updated successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update checklist")),
  });
}

export function useDeleteServiceType(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => serviceTypeService.deleteServiceType(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: SERVICE_TYPES_KEY });
      toast.success("Service type deleted successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to delete service type")),
  });
}
