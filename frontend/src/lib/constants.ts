export const POLLING_INTERVALS = {
  queued: 4000,
  pending: 4000,
  processing: 1000,
  rendering: 1000,
  completed: false,
  failed: false,
} as const;

export type PollableStatus = keyof typeof POLLING_INTERVALS;

export function getPollingInterval(status: string | undefined): number | false {
  if (!status) return 4000;
  if (status in POLLING_INTERVALS) {
    return POLLING_INTERVALS[status as PollableStatus];
  }
  return false;
}
