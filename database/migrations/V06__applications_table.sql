CREATE TYPE app.application_type AS ENUM ('send', 'recieve', 'defect', 'use', 'revert');

CREATE TYPE app.application_status AS ENUM ('pending', 'success', 'rejected');

CREATE TABLE app.applications (
    application_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    type app.application_type NOT NULL,
    status app.application_status NOT NULL,
    payload JSONB NOT NULL,
    created_by_id TEXT NOT NULL,
    finished_by_id TEXT,
    sent_from_warehouse_id TEXT,
    sent_to_warehouse_id TEXT,
    linked_to_application_id TEXT,
    created_at TIMESTAMPTZ NOT NULL UNIQUE,
    updated_at TIMESTAMPTZ NOT NULL
);
