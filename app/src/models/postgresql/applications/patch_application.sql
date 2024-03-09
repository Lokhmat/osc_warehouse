UPDATE app.applications SET 
    application_id = :application_id,
    name = :name,
    description = :description,
    type = :type,
    status = :status,
    sent_from_warehouse_id = :sent_from_warehouse_id,
    sent_to_warehouse_id = :sent_to_warehouse_id,
    linked_to_application_id = :linked_to_application_id,
    payload = :payload,
    updated_at = NOW()
WHERE application_id = :application_id
RETURNING 
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
;
