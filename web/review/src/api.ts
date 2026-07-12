export type StoryStatus =
  | "candidate"
  | "drafted"
  | "approved"
  | "rejected"
  | "published";

export interface Story {
  id: number;
  url: string;
  title: string;
  source_name: string;
  published_at: string;
  excerpt: string;
  category: string;
  apac_score: number;
  summary: string;
  why_it_matters: string;
  read_time_minutes: number;
  status: StoryStatus;
  issue_date: string | null;
}

export interface QueueStats {
  candidates: number;
  drafted: number;
  approved: number;
  stories_per_issue: number;
  tagline: string;
}

const base = import.meta.env.VITE_API_URL ?? "";
const apiToken = import.meta.env.VITE_API_TOKEN ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(apiToken ? { Authorization: `Bearer ${apiToken}` } : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchQueueStats(): Promise<QueueStats> {
  return request<QueueStats>("/api/queue/stats");
}

export function fetchStories(status?: StoryStatus): Promise<Story[]> {
  const query = status ? `?status=${status}` : "";
  return request<Story[]>(`/api/stories${query}`);
}

export function fetchStory(id: number): Promise<Story> {
  return request<Story>(`/api/stories/${id}`);
}

export function saveStory(
  id: number,
  fields: Pick<Story, "summary" | "why_it_matters" | "category" | "read_time_minutes">,
): Promise<Story> {
  return request<Story>(`/api/stories/${id}`, {
    method: "PATCH",
    body: JSON.stringify(fields),
  });
}

export function approveStory(id: number): Promise<Story> {
  return request<Story>(`/api/stories/${id}/approve`, { method: "POST" });
}

export function rejectStory(id: number): Promise<Story> {
  return request<Story>(`/api/stories/${id}/reject`, { method: "POST" });
}
