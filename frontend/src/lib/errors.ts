/**
 * Extract a human-readable error message from an Axios error.
 * Handles both FastAPI string `detail` (e.g. 409) and
 * Pydantic validation array `detail` (422).
 */
export function getApiError(error: unknown, fallback: string): string {
  const detail = (error as { response?: { data?: { detail?: unknown } } })
    ?.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((e: { msg?: string }) => e.msg ?? "").join(", ");
  }

  return fallback;
}
