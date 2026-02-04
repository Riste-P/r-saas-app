import api from "@/lib/api";
import type { DashboardStats } from "@/types";

export async function getStats(): Promise<DashboardStats> {
  const res = await api.get<DashboardStats>("/dashboard/stats");
  return res.data;
}
