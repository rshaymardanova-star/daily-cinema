"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createProject,
  getProject,
  getProjectStatus,
  getTimeline,
  startRender,
} from "../api/projects";
import type { ProjectCreate } from "../types";

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
  return useQuery({
    queryKey: ["projects", projectId, "status"],
    queryFn: () => getProjectStatus(projectId!),
    enabled: !!projectId,
    refetchInterval: poll ? 2000 : false,
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
