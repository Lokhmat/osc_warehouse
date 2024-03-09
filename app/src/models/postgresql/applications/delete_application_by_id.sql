UPDATE
    app.applications
SET
    status = 'deleted',
    finished_by_id = :finished_by_id,
    updated_at = NOW()
WHERE
    application_id = :application_id
    AND status = 'pending'
;