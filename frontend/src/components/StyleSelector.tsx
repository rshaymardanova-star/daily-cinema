"use client";

import { useTranslations } from "next-intl";
import { VISUAL_STYLES, type VisualStyle } from "../lib/types";

interface StyleSelectorProps {
  value: VisualStyle;
  onChange: (style: VisualStyle) => void;
}

export default function StyleSelector({ value, onChange }: StyleSelectorProps) {
  const t = useTranslations("style");

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">
        {t("label")}
      </label>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {VISUAL_STYLES.map((style) => (
          <button
            key={style}
            type="button"
            onClick={() => onChange(style)}
            className={`rounded-lg border p-3 text-left transition-all ${
              value === style
                ? "border-indigo-500 bg-indigo-500/10 ring-1 ring-indigo-500"
                : "border-gray-700 bg-gray-800/50 hover:border-gray-500"
            }`}
          >
            <div className="text-sm font-medium text-gray-100">
              {t(style)}
            </div>
            <div className="mt-1 text-xs text-gray-400">
              {t(`${style}_desc`)}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
