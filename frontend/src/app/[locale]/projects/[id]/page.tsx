"use client";

import { use, useState } from "react";
import { useTranslations } from "next-intl";
import { useProject, useProjectStatus, useStartRender } from "../../../../lib/hooks/useProjects";
import StatusBadge from "../../../../components/StatusBadge";
import ACUHint from "../../../../components/ACUHint";

export default function ProjectDetailPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id } = use(params);
  const t = useTranslations("project");
  const tAcu = useTranslations("acu");
  const { data: project, isLoading, error } = useProject(id);
  const [polling, setPolling] = useState(false);
  const { data: status } = useProjectStatus(id, polling);
  const startRender = useStartRender(id);

  const isActive = project?.status === "rendering" || status?.project_status === "rendering";

  const handleRender = () => {
    startRender.mutate(undefined, {
      onSuccess: () => setPolling(true),
    });
  };

  if (isLoading) {
    return <div className="text-gray-400">{t("loading")}</div>;
  }

  if (error || !project) {
    return <div className="text-red-400">{t("loadError", { error: error?.message ?? t("notFound") })}</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{project.name}</h1>
          {project.description && (
            <p className="mt-1 text-sm text-gray-400">{project.description}</p>
          )}
          <div className="mt-3 flex items-center gap-3">
            <StatusBadge status={status?.project_status ?? project.status} />
            {project.resolved_style && (
              <span className="rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-300">
                {project.resolved_style}
              </span>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <button
            onClick={handleRender}
            disabled={startRender.isPending || isActive}
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {startRender.isPending ? t("starting") : isActive ? t("rendering") : t("startRender")}
          </button>
          <ACUHint level="high">{tAcu("highRender")}</ACUHint>
        </div>
      </div>

      {startRender.isError && (
        <p className="text-sm text-red-400">{startRender.error.message}</p>
      )}

      <section>
        <h2 className="text-lg font-semibold text-white">{t("shots")}</h2>
        <div className="mt-3 space-y-2">
          {project.shots.length === 0 && (
            <p className="text-sm text-gray-500">{t("noShots")}</p>
          )}
          {project.shots.map((shot) => (
            <div
              key={shot.id}
              className="flex items-center justify-between rounded-lg border border-gray-800 bg-gray-900/50 px-4 py-3"
            >
              <div className="min-w-0 flex-1">
                <span className="text-xs font-mono text-gray-500">#{shot.order}</span>
                <p className="mt-0.5 truncate text-sm text-gray-200">{shot.prompt || t("defaultShot")}</p>
              </div>
              <StatusBadge status={shot.status} />
            </div>
          ))}
        </div>
      </section>

      {status?.ml_jobs && status.ml_jobs.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-white">{t("mlJobs")}</h2>
          <div className="mt-3 space-y-2">
            {status.ml_jobs.map((job) => (
              <div
                key={job.id}
                className="flex items-center justify-between rounded-lg border border-gray-800 bg-gray-900/50 px-4 py-3"
              >
                <span className="truncate text-xs font-mono text-gray-400">{job.id}</span>
                <StatusBadge status={job.status} />
              </div>
            ))}
          </div>
        </section>
      )}

      {project.render_jobs.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-white">{t("renderJobs")}</h2>
          <div className="mt-3 space-y-2">
            {project.render_jobs.map((job) => (
              <div
                key={job.id}
                className="rounded-lg border border-gray-800 bg-gray-900/50 px-4 py-3"
              >
                <div className="flex items-center justify-between">
                  <span className="truncate text-xs font-mono text-gray-400">{job.id}</span>
                  <StatusBadge status={job.status} />
                </div>
                {job.video_url && (
                  <a
                    href={job.video_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 block text-xs text-indigo-400 hover:text-indigo-300 truncate"
                  >
                    {job.video_url}
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="text-xs text-gray-600">
        <p>{t("created", { date: new Date(project.created_at).toLocaleString() })}</p>
        <p>{t("updated", { date: new Date(project.updated_at).toLocaleString() })}</p>
      </section>
    </div>
  );
}
