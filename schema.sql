-- =====================================================
-- SIAMA TOOLBOX — Supabase PostgreSQL Schema
-- Run this entire file in Supabase → SQL Editor → New Query
-- =====================================================

-- Enable UUID extension (already on by default in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ─────────────────────────────────────────────
-- 1. PROJECTS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS projects (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at on every row change
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ─────────────────────────────────────────────
-- 2. SIT — Stakeholder Identification Toolkit
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sit_stakeholders (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    responses   JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sit_actors (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    name        TEXT NOT NULL,
    location    TEXT DEFAULT '',
    contact     TEXT DEFAULT '',
    details     TEXT DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sit_stakeholders_project ON sit_stakeholders(project_id);
CREATE INDEX IF NOT EXISTS idx_sit_actors_project        ON sit_actors(project_id);


-- ─────────────────────────────────────────────
-- 3. SAT — Stakeholder Analysis Toolkit
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sat_relationship_data (
    id           BIGSERIAL PRIMARY KEY,
    project_id   BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stakeholder  TEXT NOT NULL,
    power        INTEGER CHECK (power BETWEEN 1 AND 10),
    interest     INTEGER CHECK (interest BETWEEN 1 AND 10),
    legitimacy   INTEGER CHECK (legitimacy BETWEEN 1 AND 10),
    urgency      INTEGER CHECK (urgency BETWEEN 1 AND 10),
    interactions TEXT DEFAULT '',
    tasks        TEXT DEFAULT '',
    knowledge    TEXT DEFAULT '',
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (project_id, stakeholder)          -- upsert target
);

CREATE TABLE IF NOT EXISTS sat_subgroups (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (project_id, name)                 -- upsert target
);

CREATE TABLE IF NOT EXISTS sat_subgroup_members (
    id           BIGSERIAL PRIMARY KEY,
    subgroup_id  BIGINT NOT NULL REFERENCES sat_subgroups(id) ON DELETE CASCADE,
    stakeholder  TEXT NOT NULL,
    UNIQUE (subgroup_id, stakeholder)         -- upsert target
);

CREATE TABLE IF NOT EXISTS sat_conflict_data (
    id               BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stakeholder      TEXT NOT NULL,
    cooperativeness  INTEGER CHECK (cooperativeness BETWEEN 1 AND 10),
    competitiveness  INTEGER CHECK (competitiveness BETWEEN 1 AND 10),
    description      TEXT DEFAULT '',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sat_knowledge_data (
    id               BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    group_name       TEXT NOT NULL,
    knowledge        TEXT DEFAULT '',
    responsibilities TEXT DEFAULT '',
    skills           TEXT DEFAULT '',
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (project_id, group_name)           -- upsert target
);

CREATE TABLE IF NOT EXISTS sat_value_map (
    id               BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stakeholder      TEXT NOT NULL,
    pains            TEXT DEFAULT '',
    gains            TEXT DEFAULT '',
    jobs             TEXT DEFAULT '',
    pain_relievers   TEXT DEFAULT '',
    gain_creators    TEXT DEFAULT '',
    products_services TEXT DEFAULT '',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sat_relationship_project ON sat_relationship_data(project_id);
CREATE INDEX IF NOT EXISTS idx_sat_subgroups_project    ON sat_subgroups(project_id);
CREATE INDEX IF NOT EXISTS idx_sat_conflict_project     ON sat_conflict_data(project_id);
CREATE INDEX IF NOT EXISTS idx_sat_knowledge_project    ON sat_knowledge_data(project_id);
CREATE INDEX IF NOT EXISTS idx_sat_value_map_project    ON sat_value_map(project_id);


-- ─────────────────────────────────────────────
-- 4. MAT — Market Analysis Toolkit
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mat_pestel (
    id            BIGSERIAL PRIMARY KEY,
    project_id    BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE UNIQUE,
    political     TEXT DEFAULT '',
    economic      TEXT DEFAULT '',
    social        TEXT DEFAULT '',
    technological TEXT DEFAULT '',
    environmental TEXT DEFAULT '',
    legal         TEXT DEFAULT '',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_gap (
    id                  BIGSERIAL PRIMARY KEY,
    project_id          BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE UNIQUE,
    current_state       TEXT DEFAULT '',
    current_strengths   TEXT DEFAULT '',
    current_weaknesses  TEXT DEFAULT '',
    desired_state       TEXT DEFAULT '',
    opportunities       TEXT DEFAULT '',
    threats             TEXT DEFAULT '',
    action_plan         TEXT DEFAULT '',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_behavioral_segments (
    id                BIGSERIAL PRIMARY KEY,
    project_id        BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name              TEXT NOT NULL,
    purchase_behavior TEXT DEFAULT '',
    usage_rate        TEXT DEFAULT '',
    benefits_sought   TEXT DEFAULT '',
    loyalty_status    TEXT DEFAULT '',
    occasion          TEXT DEFAULT '',
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_personas (
    id             BIGSERIAL PRIMARY KEY,
    project_id     BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name           TEXT NOT NULL,
    age_range      TEXT DEFAULT '',
    occupation     TEXT DEFAULT '',
    location       TEXT DEFAULT '',
    income_level   TEXT DEFAULT '',
    education      TEXT DEFAULT '',
    family_status  TEXT DEFAULT '',
    lifestyle      TEXT DEFAULT '',
    goals          TEXT DEFAULT '',
    pain_points    TEXT DEFAULT '',
    shopping_habits TEXT DEFAULT '',
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_customer_journey (
    id           BIGSERIAL PRIMARY KEY,
    project_id   BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    stage        TEXT NOT NULL,
    touchpoints  TEXT DEFAULT '',
    actions      TEXT DEFAULT '',
    emotions     TEXT DEFAULT '',
    pain_points  TEXT DEFAULT '',
    opportunities TEXT DEFAULT '',
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (project_id, stage)               -- upsert target
);

CREATE TABLE IF NOT EXISTS mat_mystery_shopping (
    id               BIGSERIAL PRIMARY KEY,
    project_id       BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    location         TEXT DEFAULT '',
    visit_date       DATE,
    ambiance         INTEGER CHECK (ambiance BETWEEN 1 AND 10),
    accessibility    INTEGER CHECK (accessibility BETWEEN 1 AND 10),
    product_display  INTEGER CHECK (product_display BETWEEN 1 AND 10),
    staff_behavior   INTEGER CHECK (staff_behavior BETWEEN 1 AND 10),
    product_knowledge INTEGER CHECK (product_knowledge BETWEEN 1 AND 10),
    response_time    INTEGER CHECK (response_time BETWEEN 1 AND 10),
    observations     TEXT DEFAULT '',
    recommendations  TEXT DEFAULT '',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_complaints (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    source      TEXT DEFAULT '',
    complaint_date DATE,
    category    TEXT DEFAULT '',
    description TEXT DEFAULT '',
    severity    TEXT DEFAULT '',
    status      TEXT DEFAULT '',
    resolution  TEXT DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_brand_audit (
    id                  BIGSERIAL PRIMARY KEY,
    project_id          BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE UNIQUE,
    brand_mission       TEXT DEFAULT '',
    brand_vision        TEXT DEFAULT '',
    brand_values        TEXT DEFAULT '',
    usp                 TEXT DEFAULT '',
    personality         TEXT DEFAULT '',
    promise             TEXT DEFAULT '',
    awareness           INTEGER DEFAULT 5,
    recognition         INTEGER DEFAULT 5,
    loyalty             INTEGER DEFAULT 5,
    satisfaction        INTEGER DEFAULT 5,
    position            INTEGER DEFAULT 5,
    consistency         INTEGER DEFAULT 5,
    strengths           TEXT DEFAULT '',
    weaknesses          TEXT DEFAULT '',
    recommendations     TEXT DEFAULT '',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mat_pestel_project       ON mat_pestel(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_gap_project          ON mat_gap(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_segments_project     ON mat_behavioral_segments(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_personas_project     ON mat_personas(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_journey_project      ON mat_customer_journey(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_mystery_project      ON mat_mystery_shopping(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_complaints_project   ON mat_complaints(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_brand_project        ON mat_brand_audit(project_id);


-- ─────────────────────────────────────────────
-- 5. NATURE OF CRAFT
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS nature_of_craft (
    id                BIGSERIAL PRIMARY KEY,
    project_id        BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    status_type       TEXT NOT NULL CHECK (status_type IN ('current', 'desired')),
    primary_dimension TEXT NOT NULL,
    item              TEXT NOT NULL,
    selected          BOOLEAN DEFAULT FALSE,
    UNIQUE (project_id, status_type, primary_dimension, item)  -- upsert target
);

CREATE INDEX IF NOT EXISTS idx_nature_project ON nature_of_craft(project_id);


-- ─────────────────────────────────────────────
-- 6. STEP PROGRESS TRACKING (Deliverable 2)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS step_progress (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    section     TEXT NOT NULL,   -- 'SIT', 'SAT', 'MAT', 'CRAFT'
    step        INTEGER NOT NULL, -- 1, 2, 3, …
    completed   BOOLEAN DEFAULT FALSE,
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (project_id, section, step)           -- upsert target
);

CREATE INDEX IF NOT EXISTS idx_progress_project ON step_progress(project_id);


-- ─────────────────────────────────────────────
-- 7. ROW-LEVEL SECURITY (optional but recommended)
-- Uncomment after you add Supabase Auth to the app
-- ─────────────────────────────────────────────
-- ALTER TABLE projects              ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sit_stakeholders      ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sit_actors            ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sat_relationship_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sat_subgroups         ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sat_subgroup_members  ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sat_conflict_data     ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sat_knowledge_data    ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sat_value_map         ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_pestel            ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_gap               ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_behavioral_segments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_personas          ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_customer_journey  ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_mystery_shopping  ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_complaints        ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mat_brand_audit       ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE nature_of_craft       ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE step_progress         ENABLE ROW LEVEL SECURITY;
