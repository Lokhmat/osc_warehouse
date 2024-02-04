SELECT
    w.warehouse_name as warehouse_name,
    m.count as item_count
FROM
    app.warehouse_to_items as m LEFT JOIN app.warehouse as w ON m.warehouse_id=w.id
WHERE
    m.item_id = :item_id
    AND NOT w.is_deleted;
