import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

let accessToken: string | null = localStorage.getItem("access_token");
let refreshToken: string | null = localStorage.getItem("refresh_token");

export function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function getAccessToken() {
  return accessToken;
}

// Attach access token to every request
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// On 401, attempt silent refresh then retry original request
let refreshPromise: Promise<string> | null = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      refreshToken
    ) {
      originalRequest._retry = true;

      // Deduplicate concurrent refresh attempts
      if (!refreshPromise) {
        refreshPromise = axios
          .post("/api/auth/refresh", { refresh_token: refreshToken })
          .then((res) => {
            const newAccessToken = res.data.access_token;
            accessToken = newAccessToken;
            localStorage.setItem("access_token", newAccessToken);
            return newAccessToken;
          })
          .catch((refreshError) => {
            clearTokens();
            window.location.href = "/login";
            return Promise.reject(refreshError);
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const newToken = await refreshPromise;
      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return api(originalRequest);
    }

    return Promise.reject(error);
  }
);

export default api;
