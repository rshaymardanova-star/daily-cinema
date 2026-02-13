"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createProject, startRender, ApiError } from "@/lib/api";

export default function CreatePage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [shots, setShots] = useState([{ prompt: "", order: 0 }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addShot = () => {
    setShots((prev) => [...prev, { prompt: "", order: prev.length }]);
  };

  const removeShot = (index: number) => {
    if (shots.length <= 1) return;
    setShots((prev) => prev.filter((_, i) => i !== index).map((s, i) => ({ ...s, order: i })));
  };

  const updateShot = (index: number, prompt: string) => {
    setShots((prev) => prev.map((s, i) => (i === index ? { ...s, prompt } : s)));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const project = await createProject({
        name: name.trim(),
        description: description.trim(),
        shots: shots.filter((s) => s.prompt.trim()).map((s, i) => ({ prompt: s.prompt.trim(), order: i })),
      });

      await startRender(project.id);
      router.push(`/status/${project.id}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-white">Create Project</h1>
        <p className="text-gray-400">
          Describe your video scenes and start the generation pipeline.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-1">
            Project Name
          </label>
          <input
            id="name"
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My Cinema Project"
            disabled={loading}
            className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your project..."
            rows={2}
            disabled={loading}
            className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
          />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-gray-300">Shots</label>
            <button
              type="button"
              onClick={addShot}
              disabled={loading}
              className="rounded-lg bg-gray-800 px-3 py-1.5 text-xs font-medium text-gray-300 hover:bg-gray-700 disabled:opacity-50 transition-colors"
            >
              + Add Shot
            </button>
          </div>

          {shots.map((shot, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="mt-3 text-xs font-mono text-gray-500 w-6 shrink-0 text-right">
                {i + 1}.
              </span>
              <textarea
                value={shot.prompt}
                onChange={(e) => updateShot(i, e.target.value)}
                placeholder="Describe this shot... (e.g. A beautiful sunset over the ocean)"
                rows={2}
                disabled={loading}
                className="flex-1 rounded-lg border border-gray-700 bg-gray-900 px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
              />
              {shots.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeShot(i)}
                  disabled={loading}
                  className="mt-2.5 text-gray-500 hover:text-red-400 disabled:opacity-50 transition-colors text-lg leading-none"
                  aria-label="Remove shot"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </div>

        {error && (
          <div className="rounded-lg border border-red-800 bg-red-900/30 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !name.trim()}
          className="w-full rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner />
              Creating & Starting Pipeline...
            </span>
          ) : (
            "Create & Generate"
          )}
        </button>
      </form>
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}
