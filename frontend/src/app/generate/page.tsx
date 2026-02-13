"use client";

import { useState, useEffect } from "react";
import { useGenerate, useGenerateStatus } from "../../lib/hooks/useGenerate";
import { useValidateStyle } from "../../lib/hooks/useStyles";
import StatusBadge from "../../components/StatusBadge";
import ACUHint from "../../components/ACUHint";
import CacheHitBadge from "../../components/CacheHitBadge";
import type { VisualStyle } from "../../lib/types";
import { VISUAL_STYLES } from "../../lib/types";

export default function GeneratePage() {
  const [jobId, setJobId] = useState("");
  const [prompt, setPrompt] = useState("");
  const [visualStyle, setVisualStyle] = useState<VisualStyle>("ethereal_default");
  const [activeJobId, setActiveJobId] = useState<string | undefined>();

  const generateMutation = useGenerate();
  const { data: jobStatus } = useGenerateStatus(activeJobId);

  const validateMutation = useValidateStyle();
  const [styleValid, setStyleValid] = useState(true);

  useEffect(() => {
    validateMutation.mutate(visualStyle, {
      onSuccess: (result) => setStyleValid(result.is_valid),
      onError: () => setStyleValid(true),
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visualStyle]);

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    if (jobStatus?.cache_hit) return;
    const id = jobId.trim() || `job-${Date.now()}`;
    generateMutation.mutate(
      {
        job_id: id,
        shot_id: `shot-${Date.now()}`,
        project_id: `proj-${Date.now()}`,
        prompt: prompt.trim(),
        visual_style: visualStyle,
        num_frames: 1,
      },
      {
        onSuccess: (data) => {
          setActiveJobId(data.job_id);
        },
      }
    );
  };

  const generateDisabled = generateMutation.isPending || !styleValid;

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">ML Generate</h1>
        <p className="mt-1 text-sm text-gray-400">
          Send a generation request directly to the ML service.
        </p>
        <div className="mt-2">
          <ACUHint level="info">ACU_MODE=light is enabled by default</ACUHint>
        </div>
      </div>

      <form onSubmit={handleGenerate} className="space-y-4">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-300">
            Prompt
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ethereal light, cosmic aura, transcendent energy..."
            rows={3}
            className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="jobId" className="block text-sm font-medium text-gray-300">
              Job ID (optional)
            </label>
            <input
              id="jobId"
              type="text"
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              placeholder="Auto-generated"
              className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label htmlFor="style" className="block text-sm font-medium text-gray-300">
              Visual Style
            </label>
            <select
              id="style"
              value={visualStyle}
              onChange={(e) => setVisualStyle(e.target.value as VisualStyle)}
              className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {VISUAL_STYLES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            {!styleValid && (
              <p className="mt-1 text-xs text-amber-400">Fix style to continue</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative group">
            <button
              type="submit"
              disabled={generateDisabled}
              className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {generateMutation.isPending ? "Submitting..." : "Generate"}
            </button>
            {!styleValid && (
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block whitespace-nowrap rounded bg-gray-800 px-2 py-1 text-xs text-amber-400 shadow-lg ring-1 ring-gray-700">
                Fix style to continue
              </span>
            )}
          </div>
          <ACUHint level="high">Full generation — high ACU usage</ACUHint>
        </div>

        {generateMutation.isError && (
          <p className="text-sm text-red-400">{generateMutation.error.message}</p>
        )}
      </form>

      {jobStatus && (
        <section className="rounded-lg border border-gray-800 bg-gray-900/50 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-white">Job Result</h2>
              <CacheHitBadge cacheHit={jobStatus.cache_hit} />
            </div>
            <StatusBadge status={jobStatus.status} />
          </div>
          <dl className="grid grid-cols-2 gap-2 text-xs">
            <dt className="text-gray-500">Job ID</dt>
            <dd className="font-mono text-gray-300">{jobStatus.job_id}</dd>
            <dt className="text-gray-500">Visual Style</dt>
            <dd className="text-gray-300">{jobStatus.visual_style ?? "—"}</dd>
            <dt className="text-gray-500">Resolved Style</dt>
            <dd className="text-gray-300">{jobStatus.resolved_style ?? "—"}</dd>
            {jobStatus.model && (
              <>
                <dt className="text-gray-500">Model</dt>
                <dd className="text-gray-300">{jobStatus.model}</dd>
              </>
            )}
            {jobStatus.duration_ms !== undefined && (
              <>
                <dt className="text-gray-500">Duration</dt>
                <dd className="text-gray-300">{jobStatus.duration_ms.toFixed(1)} ms</dd>
              </>
            )}
            {jobStatus.mock !== undefined && (
              <>
                <dt className="text-gray-500">Mock</dt>
                <dd className="text-gray-300">{jobStatus.mock ? "Yes" : "No"}</dd>
              </>
            )}
          </dl>
          {jobStatus.frame_urls.length > 0 && (
            <div>
              <h3 className="text-xs font-medium text-gray-400">Frames</h3>
              <ul className="mt-1 space-y-1">
                {jobStatus.frame_urls.map((url, i) => (
                  <li key={i} className="truncate text-xs text-indigo-400">
                    <a href={url} target="_blank" rel="noopener noreferrer">{url}</a>
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
