-- Security hardening for the stories table.
-- Apply with: supabase db push  OR  run in the SQL editor
--
-- 1. The previous anon policy exposed the entire editorial pipeline
--    (candidates, rejected stories, unpublished drafts) to anyone holding
--    the public anon key. Anon may now only read published stories.
-- 2. Add CHECK constraints so bad writes fail loudly at the database.

DROP POLICY IF EXISTS "Allow anon read stories" ON stories;

CREATE POLICY "Allow anon read published stories"
    ON stories FOR SELECT
    TO anon
    USING (status = 'published');

ALTER TABLE stories
    ADD CONSTRAINT stories_status_check CHECK (
        status IN ('candidate', 'drafted', 'approved', 'rejected', 'published')
    );

ALTER TABLE stories
    ADD CONSTRAINT stories_apac_score_check CHECK (apac_score >= 0 AND apac_score <= 1);

ALTER TABLE stories
    ADD CONSTRAINT stories_read_time_check CHECK (read_time_minutes >= 1);
