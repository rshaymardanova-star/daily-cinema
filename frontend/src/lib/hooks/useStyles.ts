"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { getBackendStyles, validateStyle } from "../api/styles";

export function useStyles() {
  return useQuery({
    queryKey: ["styles"],
    queryFn: () => getBackendStyles(),
  });
}

export function useValidateStyle() {
  return useMutation({
    mutationFn: (style: string) => validateStyle(style),
  });
}
