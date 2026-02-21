import { useQuery, useMutation, useQueryClient, skipToken } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as pstService from "@/services/propertyServiceType.service";
import type {
  AssignServicePayload,
  BulkAssignServicesPayload,
  UpdatePropertyServicePayload,
} from "@/types";

const PST_KEY = ["property-service-types"] as const;
const EFFECTIVE_KEY = ["effective-services"] as const;
const PROPERTIES_KEY = ["properties"] as const;

export function usePropertyServiceTypesQuery(propertyId: string | null) {
  return useQuery({
    queryKey: [...PST_KEY, propertyId],
    queryFn: propertyId ? () => pstService.getAssignments(propertyId) : skipToken,
  });
}

export function useEffectiveServicesQuery(propertyId: string | null) {
  return useQuery({
    queryKey: [...EFFECTIVE_KEY, propertyId],
    queryFn: propertyId ? () => pstService.getEffectiveServices(propertyId) : skipToken,
  });
}

export function useAssignService(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: AssignServicePayload) => pstService.assignService(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PST_KEY });
      qc.invalidateQueries({ queryKey: EFFECTIVE_KEY });
      qc.invalidateQueries({ queryKey: PROPERTIES_KEY });
      toast.success("Service assigned successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to assign service")),
  });
}

export function useBulkAssignServices(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: BulkAssignServicesPayload) => pstService.bulkAssignServices(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PST_KEY });
      qc.invalidateQueries({ queryKey: EFFECTIVE_KEY });
      qc.invalidateQueries({ queryKey: PROPERTIES_KEY });
      toast.success("Services assigned successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to assign services")),
  });
}

export function useUpdateAssignment(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & UpdatePropertyServicePayload) =>
      pstService.updateAssignment(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PST_KEY });
      qc.invalidateQueries({ queryKey: EFFECTIVE_KEY });
      qc.invalidateQueries({ queryKey: PROPERTIES_KEY });
      toast.success("Service assignment updated");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update assignment")),
  });
}

export function useRemoveAssignment(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => pstService.removeAssignment(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PST_KEY });
      qc.invalidateQueries({ queryKey: EFFECTIVE_KEY });
      qc.invalidateQueries({ queryKey: PROPERTIES_KEY });
      toast.success("Service removed");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to remove service")),
  });
}
