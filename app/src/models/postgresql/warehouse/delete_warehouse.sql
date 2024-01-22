UPDATE
    app.warehouse
SET
    is_deleted = TRUE
WHERE
    id = :id;