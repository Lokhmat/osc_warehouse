SELECT 
    id,
    item_name,
    codes
FROM
    app.items
WHERE 
    id=:item_id;
