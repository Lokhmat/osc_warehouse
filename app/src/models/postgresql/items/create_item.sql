INSERT INTO
    app.items (
        id,
        item_name,
        item_type,
        manufacturer,
        model,
        description,
        codes,
        created_at,
        updated_at
    )
VALUES
    (
        :id,
        :item_name,
        :item_type,
        :manufacturer,
        :model,
        :description,
        :codes,
        NOW(),
        NOW()
    ) ON CONFLICT (id) DO
UPDATE
SET
    id = :id
RETURNING
    id,
    item_name,
    item_type,
    manufacturer,
    model,
    description,
    codes;