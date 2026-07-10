-- Brief APAC stories table for Supabase (PostgreSQL)
-- Apply with: supabase db push  OR  run in the SQL editor

CREATE TABLE IF NOT EXISTS stories (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    source_name TEXT NOT NULL,
    published_at TEXT NOT NULL,
    excerpt TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'misc',
    apac_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    summary TEXT NOT NULL DEFAULT '',
    why_it_matters TEXT NOT NULL DEFAULT '',
    read_time_minutes INTEGER NOT NULL DEFAULT 3,
    status TEXT NOT NULL DEFAULT 'candidate',
    issue_date TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status);
CREATE INDEX IF NOT EXISTS idx_stories_apac_score ON stories(apac_score DESC);
CREATE INDEX IF NOT EXISTS idx_stories_issue_date ON stories(issue_date);

ALTER TABLE stories ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS; anon can read for local dev if needed.
CREATE POLICY "Allow anon read stories"
    ON stories FOR SELECT
    TO anon
    USING (true);

CREATE POLICY "Allow service role full access"
    ON stories FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
