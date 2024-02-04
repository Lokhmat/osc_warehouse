SELECT 
    id,
    item_name,
    codes
FROM
    app.items
WHERE 
    NOT is_deleted;
