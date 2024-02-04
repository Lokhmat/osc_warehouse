UPDATE
    app.items
SET
    item_name = COALESCE(:item_name, item_name),
    codes = COALESCE(:codes, codes),
    updated_at = NOW()
RETURNING
    id,
    item_name,
    codes
;
