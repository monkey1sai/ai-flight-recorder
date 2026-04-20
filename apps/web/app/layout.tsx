import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "AERIS Flight Recorder",
  description:
    "Operator shell for AI / Agent / LLM observability, provenance review, replay, and governance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant">
      <body>
        <div className="app-frame">
          <header className="topbar">
            <div>
              <strong>AERIS Flight Recorder</strong>
              <p>Trace timeline, claim evidence, replay, research, and governance.</p>
            </div>
            <nav className="topbar-links" aria-label="Primary">
              <Link href="/">Home</Link>
              <Link href="/timeline">Timeline</Link>
              <Link href="/traces/22222222-2222-4222-8222-222222222222">Trace Detail</Link>
              <Link href="/replay/22222222-2222-4222-8222-222222222222">Replay</Link>
              <Link href="/research">Research</Link>
              <Link href="/admin">Admin</Link>
            </nav>
          </header>
          <div className="content-shell">{children}</div>
        </div>
      </body>
    </html>
  );
}
