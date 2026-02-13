export type VisualStyle =
  | "ethereal_default"
  | "cosmic_cinematic"
  | "luminous_dreamscape"
  | "spectral_mythology"
  | "neon_ritual";

export const VISUAL_STYLES: VisualStyle[] = [
  "ethereal_default",
  "cosmic_cinematic",
  "luminous_dreamscape",
  "spectral_mythology",
  "neon_ritual",
];

export interface ShotCreate {
  prompt: string;
  order: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  visual_style?: VisualStyle;
  shots?: ShotCreate[];
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
  visual_style?: string;
  resolved_style?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetailResponse extends ProjectResponse {
  shots: ShotResponse[];
  render_jobs: RenderJobResponse[];
}

export interface TimelineResponse {
  project_id: string;
  shots: ShotResponse[];
  render_jobs: RenderJobResponse[];
}

export interface ProjectStatusResponse {
  project_id: string;
  project_status: string;
  visual_style?: string;
  resolved_style?: string;
  shots: ShotResponse[];
  ml_jobs: MLJobResponse[];
  render_jobs: RenderJobResponse[];
}

export interface GenerateRequest {
  job_id: string;
  shot_id: string;
  project_id: string;
  prompt: string;
  model?: string;
  num_frames?: number;
  visual_style?: string;
}

export interface JobStatus {
  job_id: string;
  status: string;
  frame_urls: string[];
  model?: string;
  visual_style?: string;
  resolved_style?: string;
  duration_ms?: number;
  mock?: boolean;
  cache_hit?: boolean;
}

export interface RenderRequest {
  job_id: string;
  project_id: string;
  scene: Record<string, unknown>;
  template?: string;
  visual_style?: string;
}

export interface RenderStatus {
  job_id: string;
  status: string;
  video_url: string;
  template?: string;
  visual_style?: string;
  resolved_style?: string;
  duration_ms?: number;
  mock?: boolean;
  cache_hit?: boolean;
}

export interface StyleInfo {
  name: string;
  description?: string;
  hdrp_profile?: Record<string, unknown>;
  ml_keywords?: string[];
  ffmpeg_filters?: string[];
}

export interface StyleValidationResult {
  requested_style: string;
  resolved_style: string;
  is_valid: boolean;
  ml_keywords?: string[];
  hdrp_preset?: string;
  ffmpeg_chain?: string[];
}

export interface BatchGenerateResult {
  batch_size: number;
  jobs: Array<{
    job_id: string;
    status: string;
    visual_style?: string;
    resolved_style?: string;
  }>;
}

export interface FilterCheckResult {
  original: string[];
  deduplicated: string[];
  duplicates_found: boolean;
  removed_count: number;
}

export interface HealthResponse {
  status: string;
}

export type ProjectStatus =
  | "created"
  | "rendering"
  | "completed"
  | "failed";
