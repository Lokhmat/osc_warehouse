CREATE TABLE app.items (
    id TEXT PRIMARY KEY,
    item_name TEXT NOT NULL,
    item_type TEXT,
    manufacturer TEXT,
    model TEXT,
    description TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    codes TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
