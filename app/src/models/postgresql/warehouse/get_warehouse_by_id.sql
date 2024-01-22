SELECT
    id,
    warehouse_name,
    address,
    created_at,
    updated_at
FROM
    app.warehouse
WHERE
    id = :id
LIMIT 1;