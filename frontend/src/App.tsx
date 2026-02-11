import ErrorBoundary from "@/components/ErrorBoundary";
import { AdminRoute, PrivateRoute, PublicRoute, SuperAdminRoute } from "@/components/guards";
import Layout from "@/components/Layout";
import { Toaster } from "@/components/ui/sonner";
import { getAccessToken } from "@/lib/api";
import DashboardPage from "@/pages/DashboardPage";
import LoginPage from "@/pages/LoginPage";
import TenantsPage from "@/pages/tenants/TenantsPage";
import ClientsPage from "@/pages/clients/ClientsPage";
import PropertiesPage from "@/pages/properties/PropertiesPage";
import ServiceTypesPage from "@/pages/service-types/ServiceTypesPage";
import UsersPage from "@/pages/users/UsersPage";
import { useAuthStore } from "@/stores/auth";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

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
                  <Route path="/service-types" element={<ServiceTypesPage />} />
                  <Route path="/clients" element={<ClientsPage />} />
                  <Route path="/properties" element={<PropertiesPage />} />

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
