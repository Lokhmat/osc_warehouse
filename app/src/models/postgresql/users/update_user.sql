UPDATE
    app.users
SET
    first_name = COALESCE(:first_name, first_name),
    last_name = COALESCE(:last_name, last_name),
    phone_number = COALESCE(:phone_number, phone_number),
    warehouses = COALESCE(:warehouses, warehouses),
    is_admin = COALESCE(:is_admin, is_admin),
    is_reviewer = COALESCE(:is_reviewer, is_reviewer),
    is_superuser = COALESCE(:is_superuser, is_superuser),
    password_hash = COALESCE(:password_hash, password_hash)
WHERE
    username = :username
RETURNING
    username,
    first_name,
    last_name,
    phone_number,
    warehouses,
    is_admin,
    is_reviewer,
    is_superuser;
