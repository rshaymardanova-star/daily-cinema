import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { setRequestLocale, getTranslations } from "next-intl/server";
import { routing } from "../../i18n/routing";
import { Link } from "../../i18n/navigation";
import Providers from "../../components/Providers";
import LanguageSwitcher from "../../components/LanguageSwitcher";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Daily Cinema",
  description: "Distributed video-generation pipeline",
};

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations({ locale, namespace: "nav" });

  return (
    <html lang={locale} className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-gray-950 text-gray-100`}
      >
        <NextIntlClientProvider locale={locale}>
          <Providers>
            <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
              <div className="mx-auto max-w-5xl flex items-center justify-between px-6 py-3">
                <Link href="/" className="text-lg font-bold tracking-tight text-white">
                  {t("brand")}
                </Link>
                <div className="flex items-center gap-4 text-sm">
                  <Link href="/projects/new" className="text-gray-400 hover:text-white transition-colors">
                    {t("newProject")}
                  </Link>
                  <Link href="/generate" className="text-gray-400 hover:text-white transition-colors">
                    {t("generate")}
                  </Link>
                  <Link href="/render" className="text-gray-400 hover:text-white transition-colors">
                    {t("render")}
                  </Link>
                  <LanguageSwitcher />
                </div>
              </div>
            </nav>
            <main className="mx-auto max-w-5xl px-6 py-8">
              {children}
            </main>
          </Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
