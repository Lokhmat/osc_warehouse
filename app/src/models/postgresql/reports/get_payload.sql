SELECT 
    sent_from_warehouse_id,
    sent_to_warehouse_id,
    payload,
    updated_at,
    type,
    created_by_id
FROM app.applications
WHERE
    status = 'success'
    AND
    updated_at <= :to_date
    AND
    updated_at >= :from_date
ORDER BY updated_at ASC
;