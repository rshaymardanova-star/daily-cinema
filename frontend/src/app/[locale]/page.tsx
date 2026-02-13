import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { Link } from "../../i18n/navigation";

export default async function Home({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <HomeContent />;
}

function HomeContent() {
  const t = useTranslations("home");

  return (
    <div className="space-y-12">
      <section className="text-center py-16">
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
          {t("title")}
        </h1>
        <p className="mt-4 text-lg text-gray-400 max-w-2xl mx-auto">
          {t("subtitle")}
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link
            href="/projects/new"
            className="rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
          >
            {t("createProject")}
          </Link>
          <Link
            href="/generate"
            className="rounded-lg border border-gray-700 px-6 py-3 text-sm font-semibold text-gray-300 hover:border-gray-500 hover:text-white transition-colors"
          >
            {t("mlGenerate")}
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
          <h3 className="text-sm font-semibold text-indigo-400">{t("pipeline")}</h3>
          <p className="mt-2 text-sm text-gray-400">{t("pipelineDesc")}</p>
        </div>
        <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
          <h3 className="text-sm font-semibold text-indigo-400">{t("visualStyles")}</h3>
          <p className="mt-2 text-sm text-gray-400">{t("visualStylesDesc")}</p>
        </div>
        <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
          <h3 className="text-sm font-semibold text-indigo-400">{t("styleMetadata")}</h3>
          <p className="mt-2 text-sm text-gray-400">{t("styleMetadataDesc")}</p>
        </div>
      </section>
    </div>
  );
}
