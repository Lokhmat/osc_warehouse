SELECT
    username,
    password_hash
FROM
    app.users
WHERE
    username = :username
    AND NOT is_deleted;