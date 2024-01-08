SELECT
    username,
    password_hash
FROM
    app.users
WHERE
    username = :username;