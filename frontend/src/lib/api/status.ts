import type { HealthResponse } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const ML_BASE = process.env.NEXT_PUBLIC_ML_URL ?? "http://localhost:8001";
const UNITY_BASE = process.env.NEXT_PUBLIC_UNITY_URL ?? "http://localhost:8002";

function healthCheck(baseUrl: string): Promise<HealthResponse> {
  return fetch(`${baseUrl}/health`).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json() as Promise<HealthResponse>;
  });
}

export function getBackendHealth(): Promise<HealthResponse> {
  return healthCheck(API_BASE);
}

export function getMLHealth(): Promise<HealthResponse> {
  return healthCheck(ML_BASE);
}

export function getUnityHealth(): Promise<HealthResponse> {
  return healthCheck(UNITY_BASE);
}

export async function getAllHealth(): Promise<{
  backend: HealthResponse | null;
  ml: HealthResponse | null;
  unity: HealthResponse | null;
}> {
  const [backend, ml, unity] = await Promise.allSettled([
    getBackendHealth(),
    getMLHealth(),
    getUnityHealth(),
  ]);

  return {
    backend: backend.status === "fulfilled" ? backend.value : null,
    ml: ml.status === "fulfilled" ? ml.value : null,
    unity: unity.status === "fulfilled" ? unity.value : null,
  };
}
