CREATE INDEX idx_gin_codes ON app.items USING GIN (codes);
