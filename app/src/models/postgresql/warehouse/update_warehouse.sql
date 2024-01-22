UPDATE
    app.warehouse
SET
    warehouse_name = COALESCE(:warehouse_name, warehouse_name),
    address = COALESCE(:address, address),
    updated_at = NOW()
WHERE
    id = :id
RETURNING 
    id,
    warehouse_name,
    address,
    created_at,
    updated_at;