"use client";

import { useLocale } from "next-intl";
import { usePathname, useRouter } from "../i18n/navigation";

export default function LanguageSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();

  const switchTo = locale === "en" ? "ru" : "en";

  const handleSwitch = () => {
    router.replace(pathname, { locale: switchTo });
  };

  return (
    <button
      onClick={handleSwitch}
      className="rounded border border-gray-700 px-2 py-1 text-xs font-medium text-gray-300 hover:border-gray-500 hover:text-white transition-colors"
    >
      {locale === "en" ? "RU" : "EN"}
    </button>
  );
}
