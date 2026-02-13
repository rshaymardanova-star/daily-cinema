export interface ShotCreate {
  prompt: string;
  order: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  shots: ShotCreate[];
}

export interface ShotResponse {
  id: string;
  project_id: string;
  order: number;
  prompt: string;
  status: string;
  created_at: string;
}

export interface MLJobResponse {
  id: string;
  shot_id: string;
  status: string;
  frame_urls: string;
  created_at: string;
  updated_at: string;
}

export interface RenderJobResponse {
  id: string;
  project_id: string;
  status: string;
  video_url: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectResponse {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetailResponse extends ProjectResponse {
  shots: ShotResponse[];
  render_jobs: RenderJobResponse[];
}

export interface ProjectStatusResponse {
  project_id: string;
  project_status: string;
  shots: ShotResponse[];
  ml_jobs: MLJobResponse[];
  render_jobs: RenderJobResponse[];
}
