import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth";
import { getAccessToken } from "@/lib/api";
import {
  PublicRoute,
  PrivateRoute,
  AdminRoute,
  SuperAdminRoute,
} from "@/components/guards";
import Layout from "@/components/Layout";
import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";
import UsersPage from "@/pages/UsersPage";
import TenantsPage from "@/pages/TenantsPage";
import { Toaster } from "@/components/ui/sonner";
import ErrorBoundary from "@/components/ErrorBoundary";

const queryClient = new QueryClient();

function AuthInitializer({ children }: { children: React.ReactNode }) {
  const fetchUser = useAuthStore((s) => s.fetchUser);
  const isLoading = useAuthStore((s) => s.isLoading);

  useEffect(() => {
    // Only attempt to fetch user if we have a token in memory
    if (getAccessToken()) {
      fetchUser();
    } else {
      // No token, mark loading as done
      useAuthStore.setState({ isLoading: false });
    }
  }, [fetchUser]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthInitializer>
          <Routes>
            {/* Public routes */}
            <Route element={<PublicRoute />}>
              <Route path="/login" element={<LoginPage />} />
            </Route>

            {/* Authenticated routes */}
            <Route element={<PrivateRoute />}>
              <Route element={<Layout />}>
                <Route path="/dashboard" element={<DashboardPage />} />

                {/* Admin routes */}
                <Route element={<AdminRoute />}>
                  <Route path="/admin/users" element={<UsersPage />} />
                </Route>

                {/* SuperAdmin routes */}
                <Route element={<SuperAdminRoute />}>
                  <Route path="/admin/tenants" element={<TenantsPage />} />
                </Route>
              </Route>
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthInitializer>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </QueryClientProvider>
    </ErrorBoundary>
  );
}
