INSERT INTO
    app.warehouse
VALUES
    (
        :id,
        :warehouse_name,
        :address,
        false,
        :created_at,
        :updated_at
    )
ON CONFLICT (id)
DO UPDATE SET id = :id
RETURNING 
    id,
    warehouse_name,
    address,
    created_at,
    updated_at;