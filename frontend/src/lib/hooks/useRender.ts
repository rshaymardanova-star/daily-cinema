"use client";

import { useMutation } from "@tanstack/react-query";
import { render, renderPreview, getRenderStatus, checkFilters } from "../api/render";
import { useAdaptivePolling } from "./useAdaptivePolling";
import type { RenderRequest, RenderStatus } from "../types";

export function useRender() {
  return useMutation({
    mutationFn: (data: RenderRequest) => render(data),
  });
}

export function useRenderPreview() {
  return useMutation({
    mutationFn: (data: RenderRequest) => renderPreview(data),
  });
}

export function useRenderStatus(jobId: string | undefined) {
  return useAdaptivePolling<RenderStatus>({
    queryKey: ["render", jobId],
    queryFn: () => getRenderStatus(jobId!),
    enabled: !!jobId,
    getStatus: (data) => data?.status,
  });
}

export function useCheckFilters() {
  return useMutation({
    mutationFn: (filters: string[]) => checkFilters(filters),
  });
}
