UPDATE
    app.users
SET
    is_deleted = TRUE
WHERE
    username = :username;
