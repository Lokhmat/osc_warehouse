INSERT INTO
    app.users
VALUES
(
        :id,
        :username,
        :first_name,
        :last_name,
        :password_hash,
        :phone_number,
        :created_at,
        :updated_at,
        :warehouses,
        :is_admin,
        :is_reviewer,
        :is_superuser
    )
ON CONFLICT (id)
DO UPDATE SET id = :id
RETURNING
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
    is_superuser;
