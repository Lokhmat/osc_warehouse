SELECT
    i.id as id,
    i.item_name as item_name,
    i.codes as codes,
    m.count as count
FROM
    app.warehouse_to_items as m LEFT JOIN app.items as i ON m.item_id=i.id
WHERE
    m.warehouse_id = :warehouse_id
    AND NOT i.is_deleted;
