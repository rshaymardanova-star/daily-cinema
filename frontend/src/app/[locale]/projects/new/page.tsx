"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "../../../../i18n/navigation";
import { useCreateProject } from "../../../../lib/hooks/useProjects";
import StyleSelector from "../../../../components/StyleSelector";
import ShotEditor from "../../../../components/ShotEditor";
import type { VisualStyle, ShotCreate } from "../../../../lib/types";

export default function NewProjectPage() {
  const t = useTranslations("project");
  const router = useRouter();
  const createProject = useCreateProject();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [visualStyle, setVisualStyle] = useState<VisualStyle>("ethereal_default");
  const [shots, setShots] = useState<ShotCreate[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    createProject.mutate(
      {
        name: name.trim(),
        description: description.trim(),
        visual_style: visualStyle,
        shots: shots.length > 0 ? shots : undefined,
      },
      {
        onSuccess: (project) => {
          router.push(`/projects/${project.id}`);
        },
      }
    );
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-white">{t("newTitle")}</h1>
      <p className="mt-1 text-sm text-gray-400">{t("newSubtitle")}</p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-300">
            {t("nameLabel")}
          </label>
          <input
            id="name"
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("namePlaceholder")}
            className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-300">
            {t("descriptionLabel")}
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={t("descriptionPlaceholder")}
            rows={3}
            className="mt-1 block w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <StyleSelector value={visualStyle} onChange={setVisualStyle} />

        <ShotEditor shots={shots} onChange={setShots} />

        <div className="flex items-center gap-3 pt-4">
          <button
            type="submit"
            disabled={createProject.isPending || !name.trim()}
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {createProject.isPending ? t("creating") : t("create")}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-lg border border-gray-700 px-5 py-2.5 text-sm font-semibold text-gray-300 hover:border-gray-500 transition-colors"
          >
            {t("cancel")}
          </button>
        </div>

        {createProject.isError && (
          <p className="text-sm text-red-400">
            {t("createError", { error: createProject.error.message })}
          </p>
        )}
      </form>
    </div>
  );
}
