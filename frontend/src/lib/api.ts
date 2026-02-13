import type {
  ProjectCreate,
  ProjectResponse,
  ProjectDetailResponse,
  ProjectStatusResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {}
    throw new ApiError(detail, res.status);
  }

  return res.json() as Promise<T>;
}

export async function createProject(data: ProjectCreate): Promise<ProjectResponse> {
  return request<ProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getProject(id: string): Promise<ProjectDetailResponse> {
  return request<ProjectDetailResponse>(`/projects/${id}`);
}

export async function startRender(projectId: string): Promise<ProjectResponse> {
  return request<ProjectResponse>(`/projects/${projectId}/render`, {
    method: "POST",
  });
}

export async function getProjectStatus(projectId: string): Promise<ProjectStatusResponse> {
  return request<ProjectStatusResponse>(`/projects/${projectId}/status`);
}

export async function checkHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health");
}

export { ApiError };
