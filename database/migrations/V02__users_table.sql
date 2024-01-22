CREATE TABLE app.users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    phone_number TEXT,
    created_at TIMESTAMPTZ NOT NULL UNIQUE,
    updated_at TIMESTAMPTZ NOT NULL UNIQUE,
    warehouses TEXT[] NOT NULL DEFAULT array[]::TEXT[],
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_reviewer BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX users_username ON app.users(username);
