SELECT
    warehouse_name,
    address
FROM
    app.warehouse
WHERE
    id = :id
LIMIT 1;