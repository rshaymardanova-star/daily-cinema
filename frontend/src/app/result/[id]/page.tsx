"use client";

import { useEffect, useState, use } from "react";
import { getProjectStatus } from "@/lib/api";
import type { ProjectStatusResponse } from "@/lib/types";

type PageProps = { params: Promise<{ id: string }> };

export default function ResultPage({ params }: PageProps) {
  const { id } = use(params);
  const [status, setStatus] = useState<ProjectStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProjectStatus(id)
      .then((s) => {
        setStatus(s);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message ?? "Failed to load project");
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner />
        <span className="ml-3 text-gray-400">Loading result...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 text-center">
        <div className="rounded-lg border border-red-800 bg-red-900/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
        <a
          href="/"
          className="inline-block rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
        >
          Back to Home
        </a>
      </div>
    );
  }

  const renderJob = status?.render_jobs?.[0];
  const videoUrl = renderJob?.video_url;
  const projectDone = status?.project_status === "completed";

  if (!projectDone || !videoUrl) {
    return (
      <div className="space-y-6 text-center">
        <h1 className="text-3xl font-bold text-white">Not Ready Yet</h1>
        <p className="text-gray-400">This project hasn't finished rendering.</p>
        <a
          href={`/status/${id}`}
          className="inline-block rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 transition-colors"
        >
          View Status
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-white">Your Video is Ready</h1>
        <p className="text-gray-400">
          Generation complete. Preview or download your video below.
        </p>
      </div>

      <div className="rounded-xl border border-gray-800 bg-gray-900 overflow-hidden">
        <video
          src={videoUrl}
          controls
          autoPlay
          className="w-full aspect-video bg-black"
        >
          Your browser does not support video playback.
        </video>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
        <a
          href={videoUrl}
          download
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
        >
          Download Video
        </a>
        <a
          href="/"
          className="rounded-lg bg-gray-800 px-6 py-2.5 text-sm font-medium text-gray-300 hover:bg-gray-700 transition-colors"
        >
          Create Another
        </a>
      </div>

      {status.shots.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            Shots
          </h2>
          {status.shots.map((shot, i) => (
            <div
              key={shot.id}
              className="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-900/50 px-4 py-3"
            >
              <span className="text-xs font-mono text-gray-500 w-5 text-right">{i + 1}.</span>
              <span className="flex-1 text-sm text-gray-300">{shot.prompt}</span>
              <span className="h-2 w-2 rounded-full bg-green-400" />
            </div>
          ))}
        </div>
      )}

      {status.ml_jobs.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            Generated Frames
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {status.ml_jobs
              .filter((j) => j.frame_urls)
              .map((job) => {
                const urls = typeof job.frame_urls === "string" ? job.frame_urls.split(",") : [];
                return urls.map((url, fi) => (
                  <div
                    key={`${job.id}-${fi}`}
                    className="rounded-lg border border-gray-800 bg-gray-900 overflow-hidden aspect-video"
                  >
                    <img
                      src={url.trim()}
                      alt={`Frame ${fi + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ));
              })}
          </div>
        </div>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}
