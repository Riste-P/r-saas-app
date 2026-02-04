import api from "@/lib/api";
import type { TokenResponse, User } from "@/types";

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>("/auth/login", { email, password });
  return res.data;
}

export async function getMe(): Promise<User> {
  const res = await api.get<User>("/auth/me");
  return res.data;
}
