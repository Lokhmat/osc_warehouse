UPDATE
    app.applications
SET
    status = 'success',
    finished_by_id = :finished_by_id,
    updated_at = NOW()
WHERE
    application_id = :application_id
    AND status = 'pending'
RETURNING
    sent_from_warehouse_id,
    sent_to_warehouse_id,
    type,
    payload;