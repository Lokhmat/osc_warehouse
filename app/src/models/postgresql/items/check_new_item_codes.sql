-- $1 - codes
SELECT
    item_name
FROM
    app.items
WHERE
    codes && :codes
    AND NOT is_deleted;
