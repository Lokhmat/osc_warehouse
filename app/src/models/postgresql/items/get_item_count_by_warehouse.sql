SELECT
    i.id as id,
    i.item_name as item_name,
    i.item_type as item_type,
    i.manufacturer as manufacturer,
    i.model as model,
    i.description as description,
    i.codes as codes,
    m.count as count
FROM
    app.warehouse_to_items as m LEFT JOIN app.items as i ON m.item_id=i.id
WHERE
    m.warehouse_id = :warehouse_id
    AND NOT i.is_deleted
    AND (:item_name IS NULL OR i.item_name LIKE ('%' || :item_name || '%'))
    AND (:item_cat IS NULL OR i.item_type LIKE ('%' || :item_cat || '%'));
