UPDATE
    app.items
SET
    is_deleted = true,
    updated_at = NOW()
WHERE
    id = :item_id
;
