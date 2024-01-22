INSERT INTO
    app.warehouse
VALUES
    (
        :id,
        :warehouse_name,
        :address,
        :created_at,
        :updated_at
    )
RETURNING 
    id,
    warehouse_name,
    address,
    created_at,
    updated_at;