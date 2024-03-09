UPDATE
    app.applications
SET
    status = 'rejected',
    finished_by_id = :finished_by_id,
    updated_at = NOW()
WHERE
    application_id = :application_id
    AND status = 'pending'
RETURNING
    1;