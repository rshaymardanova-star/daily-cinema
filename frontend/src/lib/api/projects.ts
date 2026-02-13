import { api } from "./client";
import type {
  ProjectCreate,
  ProjectResponse,
  ProjectDetailResponse,
  TimelineResponse,
  ProjectStatusResponse,
} from "../types";

export function createProject(data: ProjectCreate): Promise<ProjectResponse> {
  return api.post<ProjectResponse>("/projects", data);
}

export function getProject(projectId: string): Promise<ProjectDetailResponse> {
  return api.get<ProjectDetailResponse>(`/projects/${projectId}`);
}

export function getTimeline(projectId: string): Promise<TimelineResponse> {
  return api.get<TimelineResponse>(`/projects/${projectId}/timeline`);
}

export function startRender(projectId: string): Promise<ProjectResponse> {
  return api.post<ProjectResponse>(`/projects/${projectId}/render`);
}

export function getProjectStatus(projectId: string): Promise<ProjectStatusResponse> {
  return api.get<ProjectStatusResponse>(`/projects/${projectId}/status`);
}
