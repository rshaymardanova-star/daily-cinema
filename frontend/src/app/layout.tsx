import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import Providers from "../components/Providers";
import "./globals.css";

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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-gray-950 text-gray-100`}
      >
        <Providers>
          <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
            <div className="mx-auto max-w-5xl flex items-center justify-between px-6 py-3">
              <Link href="/" className="text-lg font-bold tracking-tight text-white">
                Daily Cinema
              </Link>
              <div className="flex items-center gap-4 text-sm">
                <Link href="/projects/new" className="text-gray-400 hover:text-white transition-colors">
                  New Project
                </Link>
                <Link href="/generate" className="text-gray-400 hover:text-white transition-colors">
                  Generate
                </Link>
                <Link href="/render" className="text-gray-400 hover:text-white transition-colors">
                  Render
                </Link>
              </div>
            </div>
          </nav>
          <main className="mx-auto max-w-5xl px-6 py-8">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
