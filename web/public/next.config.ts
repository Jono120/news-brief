import type { NextConfig } from "next";
import path from "path";

const projectRoot = path.join(__dirname, "..", "..");

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname, ".."),
  env: {
    BRIEF_ROOT: projectRoot,
  },
};

export default nextConfig;
