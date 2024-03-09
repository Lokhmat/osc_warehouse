INSERT INTO
    app.warehouse_to_items (warehouse_id, item_id, count)
SELECT
    *
FROM
    UNNEST(:warehouse_ids, :item_ids, :counts) ON CONFLICT (warehouse_id, item_id) DO
UPDATE
SET
    count = app.warehouse_to_items.count + EXCLUDED.count;