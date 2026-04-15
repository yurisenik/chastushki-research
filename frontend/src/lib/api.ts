import type { GeneratePackRequest, HistoryResponse, Pack } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function generatePack(payload: GeneratePackRequest): Promise<Pack> {
  return fetchJson<Pack>("/v1/generate-pack", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function refinePack(packId: string, action: string): Promise<Pack> {
  return fetchJson<Pack>("/v1/refine", {
    method: "POST",
    body: JSON.stringify({ pack_id: packId, action }),
  });
}

export function getHistory(): Promise<HistoryResponse> {
  return fetchJson<HistoryResponse>("/v1/history");
}

export function addFavorite(packId: string): Promise<Pack> {
  return fetchJson<Pack>("/v1/favorites", {
    method: "POST",
    body: JSON.stringify({ pack_id: packId }),
  });
}

export function getFavorites(): Promise<HistoryResponse> {
  return fetchJson<HistoryResponse>("/v1/favorites");
}
