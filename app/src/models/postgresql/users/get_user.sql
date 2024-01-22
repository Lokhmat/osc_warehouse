SELECT
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
    is_super_user
FROM
    app.users
WHERE
    username = :username
    AND NOT is_deleted;
