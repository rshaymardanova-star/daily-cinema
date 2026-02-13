"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { generate, generateBatch, getGenerateStatus } from "../api/generate";
import type { GenerateRequest } from "../types";

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

export function useGenerateStatus(jobId: string | undefined, poll = false) {
  return useQuery({
    queryKey: ["generate", jobId],
    queryFn: () => getGenerateStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: poll ? 1000 : false,
  });
}
