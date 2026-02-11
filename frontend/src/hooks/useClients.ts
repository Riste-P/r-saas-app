import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as clientService from "@/services/client.service";
import type { ClientCreatePayload, ClientUpdatePayload } from "@/types";

const CLIENTS_KEY = ["clients"] as const;

export function useClientsQuery() {
  return useQuery({
    queryKey: CLIENTS_KEY,
    queryFn: clientService.getClients,
    select: (data) => data.items,
  });
}

export function useClientQuery(id: string | null) {
  return useQuery({
    queryKey: [...CLIENTS_KEY, id],
    queryFn: () => clientService.getClient(id!),
    enabled: !!id,
  });
}

export function useCreateClient(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ClientCreatePayload) => clientService.createClient(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CLIENTS_KEY });
      toast.success("Client created successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to create client")),
  });
}

export function useUpdateClient(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & ClientUpdatePayload) =>
      clientService.updateClient(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CLIENTS_KEY });
      toast.success("Client updated successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update client")),
  });
}

export function useDeleteClient(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => clientService.deleteClient(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CLIENTS_KEY });
      toast.success("Client deleted successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to delete client")),
  });
}
