const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new ApiError(res.status, `API error: ${res.statusText}`);
  }

  return res.json();
}

export async function searchProducts(
  query: string,
  options?: { category?: string; page?: number; limit?: number },
) {
  const params = new URLSearchParams({ q: query });
  if (options?.category) params.set("category", options.category);
  if (options?.page) params.set("page", String(options.page));
  if (options?.limit) params.set("limit", String(options.limit));

  return fetchApi(`/api/v1/search?${params}`);
}

export async function getProduct(id: string) {
  return fetchApi(`/api/v1/products/${id}`);
}

export async function getProductScore(id: string) {
  return fetchApi(`/api/v1/products/${id}/score`);
}

export async function getChemical(id: string) {
  return fetchApi(`/api/v1/chemicals/${id}`);
}

export async function getAIExplanation(
  entityType: "product" | "chemical",
  entityId: string,
) {
  return fetchApi(`/api/v1/explain/${entityType}/${entityId}`, {
    method: "POST",
  });
}

export async function compareProducts(productIds: string[]) {
  return fetchApi("/api/v1/compare", {
    method: "POST",
    body: JSON.stringify({ product_ids: productIds }),
  });
}
