"use client";

import { useState } from "react";
import { useRender, useRenderPreview, useRenderStatus } from "../../lib/hooks/useRender";
import StatusBadge from "../../components/StatusBadge";
import type { VisualStyle } from "../../lib/types";
import { VISUAL_STYLES } from "../../lib/types";

export default function RenderPage() {
  const [jobId, setJobId] = useState("");
  const [projectId, setProjectId] = useState("");
  const [visualStyle, setVisualStyle] = useState<VisualStyle>("ethereal_default");
  const [activeJobId, setActiveJobId] = useState<string | undefined>();
  const [polling, setPolling] = useState(false);
  const [isPreview, setIsPreview] = useState(false);

  const renderMutation = useRender();
  const previewMutation = useRenderPreview();
  const { data: renderStatus } = useRenderStatus(activeJobId, polling);

  if (renderStatus?.status === "completed" || renderStatus?.status === "failed") {
    if (polling) setPolling(false);
  }

  const handleSubmit = (e: React.FormEvent, preview: boolean) => {
    e.preventDefault();
    const id = jobId.trim() || `render-${Date.now()}`;
    const pid = projectId.trim() || `proj-${Date.now()}`;
    const payload = {
      job_id: id,
      project_id: pid,
      scene: { project_id: pid, shots: [] },
      visual_style: visualStyle,
    };

    const mutation = preview ? previewMutation : renderMutation;
    setIsPreview(preview);
    mutation.mutate(payload, {
      onSuccess: (data) => {
        setActiveJobId(data.job_id);
        setPolling(true);
      },
    });
  };

  const activeMutation = isPreview ? previewMutation : renderMutation;

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Unity Render</h1>
        <p className="mt-1 text-sm text-gray-400">
          Send a render request directly to the Unity worker.
        </p>
      </div>

      <form className="space-y-4">
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
            <label htmlFor="projectId" className="block text-sm font-medium text-gray-300">
              Project ID (optional)
            </label>
            <input
              id="projectId"
              type="text"
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              placeholder="Auto-generated"
              className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
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
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={(e) => handleSubmit(e, false)}
            disabled={renderMutation.isPending || previewMutation.isPending}
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {renderMutation.isPending ? "Rendering..." : "Full Render"}
          </button>
          <button
            type="button"
            onClick={(e) => handleSubmit(e, true)}
            disabled={renderMutation.isPending || previewMutation.isPending}
            className="rounded-lg border border-gray-700 px-5 py-2.5 text-sm font-semibold text-gray-300 hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {previewMutation.isPending ? "Previewing..." : "Preview (micro)"}
          </button>
        </div>

        {activeMutation.isError && (
          <p className="text-sm text-red-400">{activeMutation.error.message}</p>
        )}
      </form>

      {renderStatus && (
        <section className="rounded-lg border border-gray-800 bg-gray-900/50 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Render Result</h2>
            <StatusBadge status={renderStatus.status} />
          </div>
          <dl className="grid grid-cols-2 gap-2 text-xs">
            <dt className="text-gray-500">Job ID</dt>
            <dd className="font-mono text-gray-300">{renderStatus.job_id}</dd>
            <dt className="text-gray-500">Visual Style</dt>
            <dd className="text-gray-300">{renderStatus.visual_style ?? "—"}</dd>
            <dt className="text-gray-500">Resolved Style</dt>
            <dd className="text-gray-300">{renderStatus.resolved_style ?? "—"}</dd>
            {renderStatus.template && (
              <>
                <dt className="text-gray-500">Template</dt>
                <dd className="text-gray-300">{renderStatus.template}</dd>
              </>
            )}
            {renderStatus.duration_ms !== undefined && (
              <>
                <dt className="text-gray-500">Duration</dt>
                <dd className="text-gray-300">{renderStatus.duration_ms.toFixed(1)} ms</dd>
              </>
            )}
            {renderStatus.mock !== undefined && (
              <>
                <dt className="text-gray-500">Mock</dt>
                <dd className="text-gray-300">{renderStatus.mock ? "Yes" : "No"}</dd>
              </>
            )}
          </dl>
          {renderStatus.video_url && (
            <div>
              <h3 className="text-xs font-medium text-gray-400">Video URL</h3>
              <a
                href={renderStatus.video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-1 block truncate text-xs text-indigo-400 hover:text-indigo-300"
              >
                {renderStatus.video_url}
              </a>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
