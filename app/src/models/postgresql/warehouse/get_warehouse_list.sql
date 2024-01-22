SELECT
    id,
    warehouse_name,
    address,
    created_at,
    updated_at
FROM
    app.warehouse
WHERE
    NOT is_deleted
ORDER BY
    created_at DESC;