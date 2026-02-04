import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getApiError } from "@/lib/errors";
import * as userService from "@/services/user.service";
import type { UserCreatePayload, UserUpdatePayload } from "@/types";

const USERS_KEY = ["users"] as const;

export function useUsersQuery() {
  return useQuery({
    queryKey: USERS_KEY,
    queryFn: userService.getUsers,
    select: (data) => data.items,
  });
}

export function useCreateUser(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: UserCreatePayload) => userService.createUser(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: USERS_KEY });
      toast.success("User created successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to create user")),
  });
}

export function useUpdateUser(opts?: { onSuccess?: () => void }) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & UserUpdatePayload) =>
      userService.updateUser(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: USERS_KEY });
      toast.success("User updated successfully");
      opts?.onSuccess?.();
    },
    onError: (err) => toast.error(getApiError(err, "Failed to update user")),
  });
}
