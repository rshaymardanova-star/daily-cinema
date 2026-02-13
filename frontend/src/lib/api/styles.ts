import { api } from "./client";
import type { StyleInfo, StyleValidationResult } from "../types";

const ML_BASE = process.env.NEXT_PUBLIC_ML_URL ?? "http://localhost:8001";
const UNITY_BASE = process.env.NEXT_PUBLIC_UNITY_URL ?? "http://localhost:8002";

export function getBackendStyles(): Promise<Record<string, StyleInfo>> {
  return api.get<Record<string, StyleInfo>>("/styles");
}

export function validateStyle(visual_style: string): Promise<StyleValidationResult> {
  return api.post<StyleValidationResult>("/styles/validate", { visual_style });
}

export function getMLStyles(): Promise<Record<string, unknown>> {
  return fetch(`${ML_BASE}/styles`).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json() as Promise<Record<string, unknown>>;
  });
}

export function getUnityStyles(): Promise<Record<string, unknown>> {
  return fetch(`${UNITY_BASE}/styles`).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json() as Promise<Record<string, unknown>>;
  });
}
