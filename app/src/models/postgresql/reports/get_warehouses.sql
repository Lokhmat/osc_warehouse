SELECT
    id,
    warehouse_name
FROM
    app.warehouse
WHERE
    id = ANY(:ids)
;