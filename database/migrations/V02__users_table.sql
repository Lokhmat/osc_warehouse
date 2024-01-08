CREATE TABLE app.users (
    id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    phone_number TEXT,
    about TEXT,
    created_at TIMESTAMPTZ NOT NULL UNIQUE
);
