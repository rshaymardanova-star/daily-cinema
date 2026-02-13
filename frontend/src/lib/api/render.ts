import type { RenderRequest, RenderStatus, FilterCheckResult } from "../types";

const UNITY_BASE = process.env.NEXT_PUBLIC_UNITY_URL ?? "http://localhost:8002";

function unityGet<T>(path: string) {
  return fetch(`${UNITY_BASE}${path}`).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json() as Promise<T>;
  });
}

function unityPost<T>(path: string, body: unknown) {
  return fetch(`${UNITY_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json() as Promise<T>;
  });
}

export function render(data: RenderRequest): Promise<RenderStatus> {
  return unityPost<RenderStatus>("/render", data);
}

export function renderPreview(data: RenderRequest): Promise<RenderStatus> {
  return unityPost<RenderStatus>("/render/preview", data);
}

export function getRenderStatus(jobId: string): Promise<RenderStatus> {
  return unityGet<RenderStatus>(`/status/${jobId}`);
}

export function checkFilters(filters: string[]): Promise<FilterCheckResult> {
  return unityPost<FilterCheckResult>("/filters/check", { filters });
}
