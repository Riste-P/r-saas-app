import { z } from "zod";

// === Shared field validators ===
const email = z.email({ message: "Invalid email address" });
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

// === Service Types ===
export const checklistItemSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().max(500).optional(),
  sort_order: z.coerce.number().int().min(0).default(0),
});

export const createServiceTypeSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().max(1000).optional(),
  base_price: z.coerce.number().positive("Price must be positive"),
  estimated_duration_minutes: z.coerce.number().int().positive("Duration must be positive"),
  checklist_items: z.array(checklistItemSchema).default([]),
});
export type CreateServiceTypeFormValues = z.infer<typeof createServiceTypeSchema>;

export const editServiceTypeSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().max(1000).optional(),
  base_price: z.coerce.number().positive("Price must be positive"),
  estimated_duration_minutes: z.coerce.number().int().positive("Duration must be positive"),
  is_active: z.boolean(),
});
export type EditServiceTypeFormValues = z.infer<typeof editServiceTypeSchema>;

export const checklistEditorSchema = z.object({
  items: z.array(checklistItemSchema),
});
export type ChecklistEditorFormValues = z.infer<typeof checklistEditorSchema>;

// === Clients ===
export const createClientSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  email: z.string().email("Invalid email").optional().or(z.literal("")),
  phone: z.string().max(50).optional().or(z.literal("")),
  address: z.string().max(500).optional().or(z.literal("")),
  billing_address: z.string().max(500).optional().or(z.literal("")),
  notes: z.string().optional().or(z.literal("")),
});
export type CreateClientFormValues = z.infer<typeof createClientSchema>;

export const editClientSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  email: z.string().email("Invalid email").optional().or(z.literal("")),
  phone: z.string().max(50).optional().or(z.literal("")),
  address: z.string().max(500).optional().or(z.literal("")),
  billing_address: z.string().max(500).optional().or(z.literal("")),
  notes: z.string().optional().or(z.literal("")),
  is_active: z.boolean(),
});
export type EditClientFormValues = z.infer<typeof editClientSchema>;

// === Properties ===
export const createPropertySchema = z.object({
  client_id: z.string().min(1, "Please select a client"),
  parent_property_id: z.string().optional().or(z.literal("")),
  property_type: z.enum(["house", "apartment", "building", "commercial"]),
  name: z.string().min(1, "Name is required").max(255),
  address: z.string().min(1, "Address is required").max(500),
  city: z.string().max(100).optional().or(z.literal("")),
  postal_code: z.string().max(20).optional().or(z.literal("")),
  size_sqm: z.string().optional().or(z.literal("")),
  num_rooms: z.string().optional().or(z.literal("")),
  floor: z.string().max(20).optional().or(z.literal("")),
  access_instructions: z.string().optional().or(z.literal("")),
  key_code: z.string().max(100).optional().or(z.literal("")),
  contact_name: z.string().max(255).optional().or(z.literal("")),
  contact_phone: z.string().max(50).optional().or(z.literal("")),
  contact_email: z.string().email("Invalid email").optional().or(z.literal("")),
});
export type CreatePropertyFormValues = z.infer<typeof createPropertySchema>;

export const editPropertySchema = z.object({
  client_id: z.string().min(1, "Please select a client"),
  property_type: z.enum(["house", "apartment", "building", "commercial"]),
  name: z.string().min(1, "Name is required").max(255),
  address: z.string().min(1, "Address is required").max(500),
  city: z.string().max(100).optional().or(z.literal("")),
  postal_code: z.string().max(20).optional().or(z.literal("")),
  size_sqm: z.string().optional().or(z.literal("")),
  num_rooms: z.string().optional().or(z.literal("")),
  floor: z.string().max(20).optional().or(z.literal("")),
  access_instructions: z.string().optional().or(z.literal("")),
  key_code: z.string().max(100).optional().or(z.literal("")),
  contact_name: z.string().max(255).optional().or(z.literal("")),
  contact_phone: z.string().max(50).optional().or(z.literal("")),
  contact_email: z.string().email("Invalid email").optional().or(z.literal("")),
  is_active: z.boolean(),
});
export type EditPropertyFormValues = z.infer<typeof editPropertySchema>;
