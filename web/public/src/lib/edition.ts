import path from "path";
import fs from "fs";
import yaml from "js-yaml";

const ROOT = process.env.BRIEF_ROOT ?? path.join(process.cwd(), "..", "..");

export interface EditionInfo {
  slug: string;
  name: string;
  tagline: string;
}

export interface SiteInfo {
  title: string;
  tagline: string;
  description: string;
}

export function getEditionInfo(): EditionInfo {
  const configPath = path.join(ROOT, "config", "edition.yaml");
  const raw = yaml.load(fs.readFileSync(configPath, "utf-8")) as {
    edition: EditionInfo;
  };
  return raw.edition;
}

export function getSiteInfo(): SiteInfo {
  const edition = getEditionInfo();
  return {
    title: edition.name,
    tagline: edition.tagline,
    description:
      "A concise weekday briefing on technology across the Asia-Pacific region, edited for APAC context.",
  };
}

export function getCategoryLabels(): Record<string, string> {
  const configPath = path.join(ROOT, "config", "edition.yaml");
  const raw = yaml.load(fs.readFileSync(configPath, "utf-8")) as {
    categories: Array<{ slug: string; label: string }>;
  };
  return Object.fromEntries(raw.categories.map((c) => [c.slug, c.label]));
}
