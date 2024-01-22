CREATE TABLE app.warehouse (
    id TEXT PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    address TEXT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
