import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "NBA Fantasy Helper",
  description: "Player Value Engine + Opportunity Engine for points-league fantasy NBA",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="site">
          <h1>🏀 NBA Fantasy Helper</h1>
          <nav>
            <Link href="/">Players</Link>
            <Link href="/streamers">Streamers</Link>
            <Link href="/about">About</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
