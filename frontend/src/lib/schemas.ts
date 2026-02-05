import { z } from "zod";

// === Shared field validators ===
const email = z.string().min(1, "Email is required").email("Invalid email address");
const password = z.string().min(8, "Password must be at least 8 characters");

// === Auth ===
export const loginSchema = z.object({
  email,
  password: z.string().min(1, "Password is required"),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

// === Users ===
export const createUserSchema = z.object({
  email,
  password,
  role_id: z.string(),
  tenant_id: z.string().optional(),
});
export type CreateUserFormValues = z.infer<typeof createUserSchema>;

export const createUserSuperadminSchema = createUserSchema.extend({
  tenant_id: z.string().min(1, "Please select a tenant"),
});

export const editUserSchema = z.object({
  role_id: z.string(),
  is_active: z.boolean(),
});
export type EditUserFormValues = z.infer<typeof editUserSchema>;

// === Tenants ===
export const createTenantSchema = z.object({
  name: z.string().min(1, "Name is required").max(100, "Name is too long"),
  slug: z
    .string()
    .min(1, "Slug is required")
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Slug must be lowercase letters, numbers, and hyphens"),
});
export type CreateTenantFormValues = z.infer<typeof createTenantSchema>;

export const editTenantSchema = z.object({
  name: z.string().min(1, "Name is required").max(100, "Name is too long"),
  is_active: z.boolean(),
});
export type EditTenantFormValues = z.infer<typeof editTenantSchema>;

export const createTenantAdminSchema = z.object({
  email,
  password,
});
export type CreateTenantAdminFormValues = z.infer<typeof createTenantAdminSchema>;
