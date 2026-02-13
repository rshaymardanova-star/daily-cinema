"use client";

import { useEffect, useState, useCallback, use } from "react";
import { useRouter } from "next/navigation";
import { startPolling } from "@/lib/polling";
import type { ProjectStatusResponse } from "@/lib/types";

type PageProps = { params: Promise<{ id: string }> };

export default function StatusPage({ params }: PageProps) {
  const { id } = use(params);
  const router = useRouter();
  const [status, setStatus] = useState<ProjectStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onUpdate = useCallback(
    (s: ProjectStatusResponse) => {
      setStatus(s);
      setError(null);
      if (s.project_status === "completed") {
        const videoUrl = s.render_jobs?.[0]?.video_url;
        if (videoUrl) {
          router.push(`/result/${id}`);
        }
      }
    },
    [id, router]
  );

  const onError = useCallback((err: Error) => {
    setError(err.message);
  }, []);

  useEffect(() => {
    const stop = startPolling(id, onUpdate, onError);
    return stop;
  }, [id, onUpdate, onError]);

  const projectStatus = status?.project_status ?? "loading";
  const mlJobs = status?.ml_jobs ?? [];
  const renderJobs = status?.render_jobs ?? [];
  const shots = status?.shots ?? [];

  const completedMl = mlJobs.filter((j) => j.status === "completed").length;
  const totalMl = mlJobs.length || shots.length || 1;
  const mlProgress = Math.round((completedMl / totalMl) * 100);

  const renderStarted = renderJobs.length > 0;
  const renderDone = renderJobs.some((j) => j.status === "completed");

  let overallProgress = 0;
  if (projectStatus === "completed") overallProgress = 100;
  else if (renderDone) overallProgress = 95;
  else if (renderStarted) overallProgress = 70 + Math.round(mlProgress * 0.2);
  else overallProgress = Math.round(mlProgress * 0.7);

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-white">Pipeline Status</h1>
        <p className="text-gray-400">
          Generating your video &mdash; this may take a few moments.
        </p>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-300">Overall Progress</span>
          <span className="font-mono text-gray-400">{overallProgress}%</span>
        </div>
        <div className="h-3 rounded-full bg-gray-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-indigo-500 transition-all duration-500 ease-out"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>

      <StatusBadge status={projectStatus} />

      {error && (
        <div className="rounded-lg border border-amber-800 bg-amber-900/30 px-4 py-3 text-sm text-amber-300">
          Connection issue: {error}. Retrying...
        </div>
      )}

      {projectStatus === "failed" && (
        <div className="rounded-lg border border-red-800 bg-red-900/30 px-4 py-3 space-y-3">
          <p className="text-sm text-red-300">
            The pipeline encountered an error. Please try again.
          </p>
          <a
            href="/"
            className="inline-block rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
          >
            Create New Project
          </a>
        </div>
      )}

      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
          Pipeline Steps
        </h2>

        <StepCard
          label="ML Generation"
          sublabel={`${completedMl} / ${totalMl} shots`}
          done={mlProgress === 100}
          active={projectStatus === "rendering" && mlProgress < 100}
        />

        <StepCard
          label="Video Rendering"
          sublabel={renderDone ? "Complete" : renderStarted ? "In progress" : "Waiting for ML"}
          done={renderDone}
          active={renderStarted && !renderDone}
        />

        <StepCard
          label="Final Output"
          sublabel={projectStatus === "completed" ? "Ready" : "Pending"}
          done={projectStatus === "completed"}
          active={false}
        />
      </div>

      {shots.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            Shots
          </h2>
          {shots.map((shot, i) => (
            <div
              key={shot.id}
              className="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-900/50 px-4 py-3"
            >
              <span className="text-xs font-mono text-gray-500 w-5 text-right">{i + 1}.</span>
              <span className="flex-1 text-sm text-gray-300 truncate">{shot.prompt}</span>
              <ShotStatusDot status={shot.status} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    loading: { bg: "bg-gray-800", text: "text-gray-400", label: "Loading..." },
    created: { bg: "bg-blue-900/40", text: "text-blue-300", label: "Created" },
    rendering: { bg: "bg-indigo-900/40", text: "text-indigo-300", label: "Processing" },
    completed: { bg: "bg-green-900/40", text: "text-green-300", label: "Completed" },
    failed: { bg: "bg-red-900/40", text: "text-red-300", label: "Failed" },
  };
  const c = config[status] ?? config.loading;

  return (
    <div className="flex justify-center">
      <span className={`inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium ${c.bg} ${c.text}`}>
        {(status === "rendering" || status === "loading") && <PulsingDot />}
        {c.label}
      </span>
    </div>
  );
}

function PulsingDot() {
  return <span className="relative flex h-2 w-2">
    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75" />
    <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-500" />
  </span>;
}

function StepCard({
  label,
  sublabel,
  done,
  active,
}: {
  label: string;
  sublabel: string;
  done: boolean;
  active: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-4 rounded-lg border px-4 py-3 transition-colors ${
        done
          ? "border-green-800 bg-green-900/20"
          : active
            ? "border-indigo-700 bg-indigo-900/20"
            : "border-gray-800 bg-gray-900/30"
      }`}
    >
      <div className="shrink-0">
        {done ? (
          <svg className="h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        ) : active ? (
          <PulsingDot />
        ) : (
          <div className="h-2 w-2 rounded-full bg-gray-600" />
        )}
      </div>
      <div className="flex-1">
        <div className="text-sm font-medium text-gray-200">{label}</div>
        <div className="text-xs text-gray-500">{sublabel}</div>
      </div>
    </div>
  );
}

function ShotStatusDot({ status }: { status: string }) {
  const color =
    status === "completed"
      ? "bg-green-400"
      : status === "processing"
        ? "bg-indigo-400 animate-pulse"
        : "bg-gray-600";
  return <span className={`h-2 w-2 rounded-full ${color}`} />;
}
