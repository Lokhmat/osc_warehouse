SELECT
    id,
    username,
    password_hash,
    first_name,
    last_name,
    phone_number,
    created_at,
    updated_at,
    warehouses,
    is_admin,
    is_reviewer,
    is_superuser
FROM
    app.users
WHERE
    id = :user_id
    AND NOT is_deleted;
