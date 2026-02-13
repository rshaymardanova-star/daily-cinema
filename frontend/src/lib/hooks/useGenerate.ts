"use client";

import { useMutation } from "@tanstack/react-query";
import { generate, generateBatch, getGenerateStatus } from "../api/generate";
import { useAdaptivePolling } from "./useAdaptivePolling";
import type { GenerateRequest, JobStatus } from "../types";

export function useGenerate() {
  return useMutation({
    mutationFn: (data: GenerateRequest) => generate(data),
  });
}

export function useGenerateBatch() {
  return useMutation({
    mutationFn: (requests: GenerateRequest[]) => generateBatch(requests),
  });
}

export function useGenerateStatus(jobId: string | undefined) {
  return useAdaptivePolling<JobStatus>({
    queryKey: ["generate", jobId],
    queryFn: () => getGenerateStatus(jobId!),
    enabled: !!jobId,
    getStatus: (data) => data?.status,
  });
}
