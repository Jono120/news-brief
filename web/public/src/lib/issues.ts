import fs from "fs";
import path from "path";
import { getEditionInfo } from "./edition";

const ROOT = process.env.BRIEF_ROOT ?? path.join(process.cwd(), "..", "..");
const OUTPUT_DIR = path.join(ROOT, "output");
const PLACEHOLDER_PATH = path.join(ROOT, "content", "placeholder", "issue.json");

export interface PublicStory {
  title: string;
  url: string;
  source_name: string;
  category: string;
  summary: string;
  why_it_matters: string;
  read_time_minutes: number;
  apac_score: number;
}

export interface PublicIssue {
  date: string;
  edition_slug: string;
  intro: string;
  apac_ratio: number;
  is_sample: boolean;
  stories: PublicStory[];
}

export interface IssueSummary {
  date: string;
  story_count: number;
  is_sample: boolean;
  apac_ratio: number;
}

// Issue dates become filesystem path components — accept plain YYYY-MM-DD only.
const ISSUE_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function isValidIssueDate(value: string): boolean {
  return ISSUE_DATE_RE.test(value);
}

function loadJsonIssue(filePath: string): PublicIssue | null {
  if (!fs.existsSync(filePath)) return null;
  try {
    const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    if (typeof data.date !== "string") throw new Error("missing date");
    return {
      date: data.date,
      edition_slug: data.edition_slug,
      intro: data.intro ?? "",
      apac_ratio: Number(data.apac_ratio ?? 0),
      is_sample: Boolean(data.is_sample),
      stories: (data.stories ?? []).map((s: PublicStory) => ({
        title: s.title,
        url: s.url,
        source_name: s.source_name,
        category: s.category ?? "misc",
        summary: s.summary ?? "",
        why_it_matters: s.why_it_matters ?? "",
        read_time_minutes: Number(s.read_time_minutes ?? 3),
        apac_score: Number(s.apac_score ?? 0),
      })),
    };
  } catch (error) {
    console.warn(`Skipping malformed issue file ${filePath}:`, error);
    return null;
  }
}

function editionSlug(): string {
  return getEditionInfo().slug;
}

function listPublishedDates(slug: string): string[] {
  const editionDir = path.join(OUTPUT_DIR, slug);
  if (!fs.existsSync(editionDir)) return [];
  return fs
    .readdirSync(editionDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter(isValidIssueDate)
    .filter((name) => fs.existsSync(path.join(editionDir, name, "issue.json")))
    .sort()
    .reverse();
}

export function loadPlaceholderIssue(): PublicIssue {
  const issue = loadJsonIssue(PLACEHOLDER_PATH);
  if (!issue) throw new Error(`Placeholder issue missing at ${PLACEHOLDER_PATH}`);
  return issue;
}

export function loadPublishedIssue(issueDate: string): PublicIssue | null {
  if (!isValidIssueDate(issueDate)) return null;
  const slug = editionSlug();
  return loadJsonIssue(path.join(OUTPUT_DIR, slug, issueDate, "issue.json"));
}

export function listPublicIssues(includeSample = true): IssueSummary[] {
  const slug = editionSlug();
  const summaries: IssueSummary[] = [];
  for (const issueDate of listPublishedDates(slug)) {
    const issue = loadPublishedIssue(issueDate);
    if (issue) {
      summaries.push({
        date: issue.date,
        story_count: issue.stories.length,
        is_sample: false,
        apac_ratio: issue.apac_ratio,
      });
    }
  }
  if (includeSample) {
    const sample = loadPlaceholderIssue();
    summaries.push({
      date: sample.date,
      story_count: sample.stories.length,
      is_sample: true,
      apac_ratio: sample.apac_ratio,
    });
  }
  return summaries;
}

export function getPublicIssue(issueDate: string): PublicIssue | null {
  if (issueDate === "sample") return loadPlaceholderIssue();
  const published = loadPublishedIssue(issueDate);
  if (published) return published;
  if (issueDate === loadPlaceholderIssue().date) return loadPlaceholderIssue();
  return null;
}

export function getFeaturedIssue(): PublicIssue {
  const dates = listPublishedDates(editionSlug());
  if (dates.length > 0) {
    const issue = loadPublishedIssue(dates[0]);
    if (issue) return issue;
  }
  return loadPlaceholderIssue();
}
