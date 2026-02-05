import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function deriveSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

export function roleNameToId(name: string): string {
  switch (name) {
    case "superadmin":
      return "1";
    case "admin":
      return "2";
    default:
      return "3";
  }
}
