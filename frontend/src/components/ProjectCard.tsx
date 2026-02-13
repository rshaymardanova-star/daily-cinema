import Link from "next/link";
import StatusBadge from "./StatusBadge";
import type { ProjectResponse } from "../lib/types";

export default function ProjectCard({ project }: { project: ProjectResponse }) {
  return (
    <Link
      href={`/projects/${project.id}`}
      className="block rounded-lg border border-gray-700 bg-gray-800/50 p-4 transition-all hover:border-gray-500 hover:bg-gray-800"
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold text-gray-100">
            {project.name}
          </h3>
          {project.description && (
            <p className="mt-1 truncate text-xs text-gray-400">
              {project.description}
            </p>
          )}
        </div>
        <StatusBadge status={project.status} />
      </div>
      <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
        {project.resolved_style && (
          <span className="rounded bg-gray-700/50 px-1.5 py-0.5">
            {project.resolved_style}
          </span>
        )}
        <span>{new Date(project.created_at).toLocaleDateString()}</span>
      </div>
    </Link>
  );
}
