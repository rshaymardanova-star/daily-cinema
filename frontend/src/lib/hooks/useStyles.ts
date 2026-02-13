"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { getBackendStyles, validateStyle } from "../api/styles";

export function useStyles() {
  return useQuery({
    queryKey: ["styles"],
    queryFn: () => getBackendStyles(),
  });
}

export function useValidateStyle(style: string) {
  return useQuery({
    queryKey: ["styles", "validate", style],
    queryFn: () => validateStyle(style),
    enabled: style.length > 0,
  });
}
