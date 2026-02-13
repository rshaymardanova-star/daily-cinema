"use client";

import { useQuery } from "@tanstack/react-query";
import { getPollingInterval } from "../constants";

interface AdaptivePollingOptions<T> {
  queryKey: unknown[];
  queryFn: () => Promise<T>;
  enabled: boolean;
  getStatus: (data: T | undefined) => string | undefined;
}

export function useAdaptivePolling<T>({
  queryKey,
  queryFn,
  enabled,
  getStatus,
}: AdaptivePollingOptions<T>) {
  const query = useQuery({
    queryKey,
    queryFn,
    enabled,
    refetchInterval: (query) => {
      const status = getStatus(query.state.data);
      return getPollingInterval(status);
    },
  });

  return query;
}
