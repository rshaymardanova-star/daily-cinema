"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { render, renderPreview, getRenderStatus, checkFilters } from "../api/render";
import type { RenderRequest } from "../types";

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

export function useRenderStatus(jobId: string | undefined, poll = false) {
  return useQuery({
    queryKey: ["render", jobId],
    queryFn: () => getRenderStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: poll ? 1000 : false,
  });
}

export function useCheckFilters() {
  return useMutation({
    mutationFn: (filters: string[]) => checkFilters(filters),
  });
}
