"use client";

import { useState } from "react";
import type { ShotCreate } from "../lib/types";

interface ShotEditorProps {
  shots: ShotCreate[];
  onChange: (shots: ShotCreate[]) => void;
}

export default function ShotEditor({ shots, onChange }: ShotEditorProps) {
  const addShot = () => {
    onChange([...shots, { prompt: "", order: shots.length }]);
  };

  const updateShot = (index: number, prompt: string) => {
    const updated = shots.map((s, i) => (i === index ? { ...s, prompt } : s));
    onChange(updated);
  };

  const removeShot = (index: number) => {
    onChange(shots.filter((_, i) => i !== index).map((s, i) => ({ ...s, order: i })));
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-300">Shots</label>
        <button
          type="button"
          onClick={addShot}
          className="rounded bg-indigo-600 px-3 py-1 text-xs font-medium text-white hover:bg-indigo-500"
        >
          + Add Shot
        </button>
      </div>
      {shots.length === 0 && (
        <p className="text-sm text-gray-500">
          No shots added. A default shot will be created automatically.
        </p>
      )}
      {shots.map((shot, i) => (
        <div key={i} className="flex items-start gap-2">
          <span className="mt-2.5 text-xs font-mono text-gray-500 w-6 shrink-0">
            #{i + 1}
          </span>
          <textarea
            value={shot.prompt}
            onChange={(e) => updateShot(i, e.target.value)}
            placeholder="Describe this shot..."
            rows={2}
            className="flex-1 rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="button"
            onClick={() => removeShot(i)}
            className="mt-2 text-gray-500 hover:text-red-400"
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  );
}
