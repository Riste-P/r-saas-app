import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as tenantService from "@/services/tenant.service";
import * as userService from "@/services/user.service";
import type { TenantCreatePayload, TenantUpdatePayload, UserCreatePayload } from "@/types";

export const TENANTS_KEY = ["tenants"] as const;

export function useTenantsQuery(enabled = true) {
  return useQuery({
    queryKey: TENANTS_KEY,
    queryFn: tenantService.getTenants,
    select: (data) => data.items,
    enabled,
  });
}

export function useCreateTenant(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: TenantCreatePayload) => tenantService.createTenant(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: TENANTS_KEY });
      toast.success("Tenant created successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to create tenant")),
  });
}

export function useUpdateTenant(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & TenantUpdatePayload) =>
      tenantService.updateTenant(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: TENANTS_KEY });
      toast.success("Tenant updated successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update tenant")),
  });
}

export function useCreateTenantAdmin(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: UserCreatePayload) => userService.createUser(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] });
      toast.success("Admin user created successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to create admin")),
  });
}
