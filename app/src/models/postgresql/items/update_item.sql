UPDATE
    app.items
SET
    item_name = COALESCE(:item_name, item_name),
    item_type = :item_type,
    manufacturer = :manufacturer,
    model = :model,
    description = :description,
    codes = COALESCE(:codes, codes),
    updated_at = NOW()
WHERE
    id = :id
RETURNING
    id,
    item_name,
    item_type,
    manufacturer,
    model,
    description,
    codes
;
