import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="text-center py-16">
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
          Daily Cinema
        </h1>
        <p className="mt-4 text-lg text-gray-400 max-w-2xl mx-auto">
          Distributed video-generation pipeline. Create projects, generate ML frames,
          and render cinematic videos with the Visual Universe style system.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link
            href="/projects/new"
            className="rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
          >
            Create Project
          </Link>
          <Link
            href="/generate"
            className="rounded-lg border border-gray-700 px-6 py-3 text-sm font-semibold text-gray-300 hover:border-gray-500 hover:text-white transition-colors"
          >
            ML Generate
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
          <h3 className="text-sm font-semibold text-indigo-400">Pipeline</h3>
          <p className="mt-2 text-sm text-gray-400">
            End-to-end orchestration: Project &rarr; ML Generation &rarr; Unity Render &rarr; Video
          </p>
        </div>
        <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
          <h3 className="text-sm font-semibold text-indigo-400">Visual Styles</h3>
          <p className="mt-2 text-sm text-gray-400">
            5 curated styles with full propagation through ML, Unity HDRP, and FFmpeg
          </p>
        </div>
        <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
          <h3 className="text-sm font-semibold text-indigo-400">Style Metadata</h3>
          <p className="mt-2 text-sm text-gray-400">
            visual_style + resolved_style in every response for full transparency
          </p>
        </div>
      </section>
    </div>
  );
}
