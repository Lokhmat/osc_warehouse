-- $1 - codes
-- $2 - id
SELECT
    item_name
FROM
    app.items
WHERE
    :codes IS NOT NULL
    AND (id != :id OR :id IS NULL)
    AND codes && :codes
    AND NOT is_deleted;
