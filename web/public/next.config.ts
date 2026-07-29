import type { NextConfig } from "next";
import path from "path";

const projectRoot = path.join(__dirname, "..", "..");
const isDev = process.env.NODE_ENV !== "production";

// Dev: 'unsafe-inline'/'unsafe-eval' are required by the Next.js dev runtime.
// Production: drop 'unsafe-eval'; keep 'unsafe-inline' for Next's script bootstrap.
const scriptSrc = isDev
  ? "'self' 'unsafe-inline' 'unsafe-eval'"
  : "'self' 'unsafe-inline'";

const contentSecurityPolicy = [
  "default-src 'self'",
  `script-src ${scriptSrc}`,
  "style-src 'self' 'unsafe-inline' https://fonts.bunny.net",
  "font-src 'self' https://fonts.bunny.net",
  "img-src 'self' data:",
  "connect-src 'self'",
  "frame-ancestors 'none'",
].join("; ");

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname, ".."),
  env: {
    BRIEF_ROOT: projectRoot,
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Content-Security-Policy", value: contentSecurityPolicy },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "DENY" },
        ],
      },
    ];
  },
};

export default nextConfig;
