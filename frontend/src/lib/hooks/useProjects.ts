"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createProject,
  getProject,
  getProjectStatus,
  getTimeline,
  startRender,
} from "../api/projects";
import { useAdaptivePolling } from "./useAdaptivePolling";
import type { ProjectCreate, ProjectStatusResponse } from "../types";

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ProjectCreate) => createProject(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useProject(projectId: string | undefined) {
  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => getProject(projectId!),
    enabled: !!projectId,
  });
}

export function useProjectStatus(projectId: string | undefined, poll = false) {
  return useAdaptivePolling<ProjectStatusResponse>({
    queryKey: ["projects", projectId, "status"],
    queryFn: () => getProjectStatus(projectId!),
    enabled: !!projectId && poll,
    getStatus: (data) => data?.project_status,
  });
}

export function useTimeline(projectId: string | undefined) {
  return useQuery({
    queryKey: ["projects", projectId, "timeline"],
    queryFn: () => getTimeline(projectId!),
    enabled: !!projectId,
  });
}

export function useStartRender(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => startRender(projectId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}
