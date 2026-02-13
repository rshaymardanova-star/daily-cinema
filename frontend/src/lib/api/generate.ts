import { api } from "./client";
import type { GenerateRequest, JobStatus, BatchGenerateResult } from "../types";

const ML_BASE = process.env.NEXT_PUBLIC_ML_URL ?? "http://localhost:8001";

function mlGet<T>(path: string) {
  return fetch(`${ML_BASE}${path}`).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json() as Promise<T>;
  });
}

function mlPost<T>(path: string, body: unknown) {
  return fetch(`${ML_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json() as Promise<T>;
  });
}

export function generate(data: GenerateRequest): Promise<JobStatus> {
  return mlPost<JobStatus>("/generate", data);
}

export function generateBatch(requests: GenerateRequest[]): Promise<BatchGenerateResult> {
  return mlPost<BatchGenerateResult>("/generate/batch", requests);
}

export function getGenerateStatus(jobId: string): Promise<JobStatus> {
  return mlGet<JobStatus>(`/status/${jobId}`);
}
