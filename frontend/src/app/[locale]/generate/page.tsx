"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useGenerate } from "../../../lib/hooks/useGenerate";
import { useValidateStyle } from "../../../lib/hooks/useStyles";
import StyleSelector from "../../../components/StyleSelector";
import StatusBadge from "../../../components/StatusBadge";
import ACUHint from "../../../components/ACUHint";
import CacheHitBadge from "../../../components/CacheHitBadge";
import type { VisualStyle } from "../../../lib/types";

export default function GeneratePage() {
  const t = useTranslations("generate");
  const tAcu = useTranslations("acu");
  const tCache = useTranslations("cache");
  const [prompt, setPrompt] = useState("");
  const [visualStyle, setVisualStyle] = useState<VisualStyle>("ethereal_default");

  const { mutate, data, isPending, error } = useGenerate();
  const { data: validation } = useValidateStyle(visualStyle);
  const isStyleValid = validation?.is_valid !== false;

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !isStyleValid) return;
    mutate({
      job_id: crypto.randomUUID(),
      shot_id: crypto.randomUUID(),
      project_id: crypto.randomUUID(),
      prompt: prompt.trim(),
      visual_style: visualStyle,
    });
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">{t("title")}</h1>
        <p className="mt-1 text-sm text-gray-400">{t("subtitle")}</p>
        <ACUHint level="info">{tAcu("lightDefault")}</ACUHint>
      </div>

      <form onSubmit={handleGenerate} className="space-y-6">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-300">
            {t("promptLabel")}
          </label>
          <textarea
            id="prompt"
            required
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={t("promptPlaceholder")}
            rows={4}
            className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <StyleSelector value={visualStyle} onChange={setVisualStyle} />

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={isPending || !prompt.trim() || !isStyleValid}
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={!isStyleValid ? t("fixStyle") : undefined}
          >
            {isPending ? t("generating") : t("generateButton")}
          </button>
          <ACUHint level="high">{tAcu("highGeneration")}</ACUHint>
        </div>

        {!isStyleValid && (
          <p className="text-xs text-amber-400">{t("fixStyle")}</p>
        )}

        {error && (
          <p className="text-sm text-red-400">{error.message}</p>
        )}
      </form>

      {data && (
        <section className="rounded-lg border border-gray-800 bg-gray-900/50 p-6 space-y-3">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-white">{t("result")}</h2>
            <StatusBadge status={data.status} />
            {data.cache_hit && <CacheHitBadge>{tCache("hitBadge")}</CacheHitBadge>}
          </div>
          <dl className="grid grid-cols-2 gap-2 text-sm">
            <dt className="text-gray-500">{t("jobId")}</dt>
            <dd className="font-mono text-gray-300 truncate">{data.job_id}</dd>
            <dt className="text-gray-500">{t("styleLabel")}</dt>
            <dd className="text-gray-300">{data.resolved_style ?? data.visual_style}</dd>
          </dl>
          {data.frame_urls && data.frame_urls.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400">{t("frames")}</h3>
              <ul className="mt-1 space-y-1">
                {data.frame_urls.map((url, i) => (
                  <li key={i}>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-indigo-400 hover:text-indigo-300 truncate block"
                    >
                      {url}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
