-- CensusMinds database schema for Supabase
-- Run this in the Supabase SQL Editor to create the simulations table

CREATE TABLE IF NOT EXISTS simulations (
    id TEXT PRIMARY KEY,
    zip_code TEXT NOT NULL,
    policy TEXT NOT NULL,
    support_pct REAL DEFAULT 0,
    oppose_pct REAL DEFAULT 0,
    num_personas INTEGER DEFAULT 0,
    results JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (allow public read/write for now)
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public access" ON simulations
    FOR ALL USING (true) WITH CHECK (true);

-- Index for faster sorting by date
CREATE INDEX IF NOT EXISTS idx_simulations_created_at ON simulations (created_at DESC);
