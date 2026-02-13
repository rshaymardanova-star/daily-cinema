import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Daily Cinema",
  description: "Distributed video-generation pipeline",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-gray-950 text-gray-100 antialiased">
        <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
          <div className="mx-auto max-w-3xl flex items-center justify-between px-6 py-4">
            <a href="/" className="text-lg font-bold tracking-tight text-white">
              Daily Cinema
            </a>
            <span className="text-xs text-gray-500">MVP</span>
          </div>
        </header>
        <main className="mx-auto max-w-3xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
