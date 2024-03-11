WITH update_dict AS (
    SELECT
        unnest(:item_ids) AS item_id,
        unnest(:counts) AS count
)
UPDATE
    app.warehouse_to_items AS wti
SET
    count = wti.count - upd.count
FROM
    update_dict AS upd
WHERE
    wti.warehouse_id = :warehouse_id
    AND wti.item_id = upd.item_id
    AND wti.count >= upd.count;