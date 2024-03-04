SELECT
    *
FROM
    app.items
WHERE
    id IN :item_ids;