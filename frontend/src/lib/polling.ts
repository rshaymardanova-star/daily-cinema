import { getProjectStatus } from "./api";
import type { ProjectStatusResponse } from "./types";

const INITIAL_INTERVAL = 1000;
const MAX_INTERVAL = 8000;
const BACKOFF_FACTOR = 1.5;

export type PollCallback = (status: ProjectStatusResponse) => void;
export type PollErrorCallback = (error: Error) => void;

export function startPolling(
  projectId: string,
  onUpdate: PollCallback,
  onError: PollErrorCallback
): () => void {
  let interval = INITIAL_INTERVAL;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let stopped = false;

  async function poll() {
    if (stopped) return;

    try {
      const status = await getProjectStatus(projectId);
      if (stopped) return;

      onUpdate(status);

      const s = status.project_status;
      if (s === "completed" || s === "failed") {
        return;
      }

      if (s === "rendering") {
        interval = Math.min(interval, 2000);
      } else {
        interval = Math.min(interval * BACKOFF_FACTOR, MAX_INTERVAL);
      }
    } catch (err) {
      if (stopped) return;
      onError(err instanceof Error ? err : new Error(String(err)));
      interval = Math.min(interval * BACKOFF_FACTOR, MAX_INTERVAL);
    }

    timeoutId = setTimeout(poll, interval);
  }

  poll();

  return () => {
    stopped = true;
    if (timeoutId) clearTimeout(timeoutId);
  };
}
