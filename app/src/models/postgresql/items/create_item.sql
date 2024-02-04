INSERT INTO
    app.items (id, item_name, codes, created_at, updated_at)
VALUES
    (:id, :item_name, :codes, NOW(), NOW()) ON CONFLICT (id) DO
UPDATE
SET
    id = :id
RETURNING id, item_name, codes;