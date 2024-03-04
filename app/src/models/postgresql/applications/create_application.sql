WITH insert_result AS (
    INSERT INTO
        app.applications(
            application_id,
            name,
            description,
            type,
            status,
            created_by_id,
            approved_by_id,
            sent_from_warehouse_id,
            sent_to_warehouse_id,
            linked_to_application_id,
            payload,
            created_at,
            updated_at
        )
    VALUES
        (
            :application_id,
            :name,
            :description,
            :type,
            :status,
            :created_by_id,
            :approved_by_id,
            :sent_from_warehouse_id,
            :sent_to_warehouse_id,
            :linked_to_application_id,
            :payload,
            :created_at,
            :updated_at
        ) ON CONFLICT (application_id) DO
    UPDATE
    SET
        application_id = :application_id
    RETURNING
        application_id as id,
        name,
        description,
        type,
        status,
        created_by_id,
        approved_by_id,
        sent_from_warehouse_id,
        sent_to_warehouse_id,
        linked_to_application_id,
        payload,
        created_at,
        updated_at
)
SELECT
    result.application_id as id,
    result.name as name,
    result.description as description,
    result.type as type,
    result.status as status,
    created_by.username as created_by_username,
    created_by.first_name as created_by_first_name,
    created_by.last_name as created_by_last_name,
    approved_by.username as approved_by_username,
    approved_by.first_name as approved_by_first_name,
    approved_by.last_name as approved_by_last_name,
    sent_from.warehouse_name as sent_from_warehouse_name,
    sent_from.address as sent_from_address,
    sent_to.warehouse_name as sent_to_warehouse_name,
    sent_to.address as sent_to_address,
    result.linked_to_application_id as linked_to_application_id,
    result.payload as payload,
    result.created_at as created_at,
    result.updated_at as updated_at
FROM insert_result as result JOIN app.users as created_by ON result.created_by_id=created_by.id
JOIN app.users as approved_by ON result.approved_by_id=approved_by.id
JOIN app.warehouse as sent_to ON result.sent_to_warehouse_id=sent_to.id
JOIN app.warehouse as sent_from ON result.sent_from_warehouse_id=sent_from.id
;