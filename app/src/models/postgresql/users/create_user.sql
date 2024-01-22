INSERT INTO
    app.users
VALUES
(
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
        :is_super_user
    );
