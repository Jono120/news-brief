import Link from "next/link";
import Script from "next/script";
import type { ReactNode } from "react";
import { getSiteInfo } from "@/lib/edition";

interface SiteShellProps {
  children: ReactNode;
  currentPath?: string;
}

export default function SiteShell({ children, currentPath = "/" }: SiteShellProps) {
  const site = getSiteInfo();

  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <div className="page">
        <header className="site-header" role="banner">
          <div className="site-brand">
            <p className="site-kicker">{site.tagline}</p>
            <Link className="site-logo" href="/">
              {site.title}
            </Link>
          </div>
          <div className="header-tools">
            <button
              type="button"
              className="nav-toggle"
              data-nav-toggle
              aria-expanded="false"
              aria-controls="site-nav"
            >
              Menu
            </button>
            <nav aria-label="Primary">
              <ul id="site-nav" className="site-nav">
                <li>
                  <Link href="/" aria-current={currentPath === "/" ? "page" : undefined}>
                    Latest
                  </Link>
                </li>
                <li>
                  <Link
                    href="/issues"
                    aria-current={currentPath === "/issues" ? "page" : undefined}
                  >
                    Archive
                  </Link>
                </li>
                <li>
                  <Link href="/feed.xml">RSS feed</Link>
                </li>
                <li>
                  <Link
                    href="/accessibility"
                    aria-current={currentPath === "/accessibility" ? "page" : undefined}
                  >
                    Accessibility
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
        </header>

        <main id="main-content" tabIndex={-1}>
          {children}
        </main>

        <footer className="site-footer" role="contentinfo">
          <div className="footer-grid">
            <div>
              <p>
                <strong>{site.title}</strong> — curated technology stories for builders and
                operators across Asia-Pacific.
              </p>
              <p className="meta">
                Weekday briefings · about five minutes · independent editorial · en-NZ
              </p>
            </div>
            <div>
              <p className="meta">Site</p>
              <ul className="footer-links">
                <li>
                  <Link href="/issues">Issue archive</Link>
                </li>
                <li>
                  <Link href="/feed.xml">RSS feed</Link>
                </li>
                <li>
                  <Link href="/accessibility">Accessibility</Link>
                </li>
              </ul>
            </div>
          </div>
        </footer>
      </div>
      <Script src="/js/site.js" strategy="afterInteractive" />
    </>
  );
}
