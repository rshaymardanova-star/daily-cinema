"use client";

import { VISUAL_STYLES, type VisualStyle } from "../lib/types";

const STYLE_LABELS: Record<VisualStyle, string> = {
  ethereal_default: "Ethereal Default",
  cosmic_cinematic: "Cosmic Cinematic",
  luminous_dreamscape: "Luminous Dreamscape",
  spectral_mythology: "Spectral Mythology",
  neon_ritual: "Neon Ritual",
};

const STYLE_DESCRIPTIONS: Record<VisualStyle, string> = {
  ethereal_default: "Soft, luminous, meditative — the default visual universe",
  cosmic_cinematic: "Deep cosmic blues, cinematic depth, epic scale",
  luminous_dreamscape: "Pastel fog, dreamlike atmosphere, gentle diffusion",
  spectral_mythology: "Ancient wisdom, spectral scales, mythical guardians",
  neon_ritual: "Neon glow, ritual energy, vibrant spectral gradients",
};

interface StyleSelectorProps {
  value: VisualStyle;
  onChange: (style: VisualStyle) => void;
}

export default function StyleSelector({ value, onChange }: StyleSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">
        Visual Style
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
              {STYLE_LABELS[style]}
            </div>
            <div className="mt-1 text-xs text-gray-400">
              {STYLE_DESCRIPTIONS[style]}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
