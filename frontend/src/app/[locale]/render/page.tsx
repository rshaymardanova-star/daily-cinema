"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRender, useRenderPreview } from "../../../lib/hooks/useRender";
import StyleSelector from "../../../components/StyleSelector";
import StatusBadge from "../../../components/StatusBadge";
import ACUHint from "../../../components/ACUHint";
import CacheHitBadge from "../../../components/CacheHitBadge";
import type { VisualStyle } from "../../../lib/types";

export default function RenderPage() {
  const t = useTranslations("renderPage");
  const tAcu = useTranslations("acu");
  const tCache = useTranslations("cache");
  const [jobId, setJobId] = useState("");
  const [projectId, setProjectId] = useState("");
  const [visualStyle, setVisualStyle] = useState<VisualStyle>("ethereal_default");

  const render = useRender();
  const preview = useRenderPreview();

  const handleRender = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobId.trim() || !projectId.trim()) return;
    render.mutate({
      job_id: jobId.trim(),
      project_id: projectId.trim(),
      scene: {},
      visual_style: visualStyle,
    });
  };

  const handlePreview = () => {
    if (!jobId.trim() || !projectId.trim()) return;
    preview.mutate({
      job_id: jobId.trim(),
      project_id: projectId.trim(),
      scene: {},
      visual_style: visualStyle,
    });
  };

  const result = render.data ?? preview.data;
  const isPending = render.isPending || preview.isPending;
  const error = render.error ?? preview.error;

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">{t("title")}</h1>
        <p className="mt-1 text-sm text-gray-400">{t("subtitle")}</p>
        <ACUHint level="info">{tAcu("lightDefault")}</ACUHint>
      </div>

      <form onSubmit={handleRender} className="space-y-6">
        <div>
          <label htmlFor="jobId" className="block text-sm font-medium text-gray-300">
            {t("jobIdLabel")}
          </label>
          <input
            id="jobId"
            type="text"
            required
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
            placeholder={t("jobIdPlaceholder")}
            className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label htmlFor="projectId" className="block text-sm font-medium text-gray-300">
            {t("projectIdLabel")}
          </label>
          <input
            id="projectId"
            type="text"
            required
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            placeholder={t("projectIdPlaceholder")}
            className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <StyleSelector value={visualStyle} onChange={setVisualStyle} />

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={isPending || !jobId.trim() || !projectId.trim()}
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {render.isPending ? t("rendering") : t("renderButton")}
          </button>
          <ACUHint level="high">{tAcu("highRender")}</ACUHint>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handlePreview}
            disabled={isPending || !jobId.trim() || !projectId.trim()}
            className="rounded-lg border border-gray-700 px-5 py-2.5 text-sm font-semibold text-gray-300 hover:border-gray-500 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {preview.isPending ? t("previewing") : t("previewButton")}
          </button>
          <ACUHint level="low">{tAcu("lowPreview")}</ACUHint>
        </div>

        {error && (
          <p className="text-sm text-red-400">{error.message}</p>
        )}
      </form>

      {result && (
        <section className="rounded-lg border border-gray-800 bg-gray-900/50 p-6 space-y-3">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-white">{t("result")}</h2>
            <StatusBadge status={result.status} />
            {result.cache_hit && <CacheHitBadge>{tCache("hitBadge")}</CacheHitBadge>}
          </div>
          <dl className="grid grid-cols-2 gap-2 text-sm">
            <dt className="text-gray-500">{t("jobIdResult")}</dt>
            <dd className="font-mono text-gray-300 truncate">{result.job_id}</dd>
            <dt className="text-gray-500">{t("styleResult")}</dt>
            <dd className="text-gray-300">{result.resolved_style ?? result.visual_style}</dd>
          </dl>
          {result.video_url && (
            <a
              href={result.video_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-xs text-indigo-400 hover:text-indigo-300 truncate"
            >
              {result.video_url}
            </a>
          )}
        </section>
      )}
    </div>
  );
}
