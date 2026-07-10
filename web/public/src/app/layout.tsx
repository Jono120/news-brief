import type { Metadata } from "next";
import { getSiteInfo } from "@/lib/edition";
import "./globals.css";

const site = getSiteInfo();

export const metadata: Metadata = {
  title: {
    default: site.title,
    template: `%s — ${site.title}`,
  },
  description: site.description,
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-NZ">
      <head>
        <link
          rel="alternate"
          type="application/rss+xml"
          title={`${site.title} RSS`}
          href="/feed.xml"
        />
        <link rel="preconnect" href="https://fonts.bunny.net" crossOrigin="" />
        <link
          rel="stylesheet"
          href="https://fonts.bunny.net/css?family=atkinson-hyperlegible:400,400i,700,700i&display=swap"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
