SELECT
    application_id as id,
    name,
    description,
    type,
    status,
    created_by_id,
    finished_by_id,
    sent_from_warehouse_id,
    sent_to_warehouse_id,
    linked_to_application_id,
    payload,
    created_at,
    updated_at
FROM
    app.applications
WHERE
    created_at < COALESCE(:cursor, NOW())
ORDER BY created_at DESC
LIMIT :limit
;