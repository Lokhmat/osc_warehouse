SELECT 
    id,
    manufacturer,
    model
FROM
    app.items
WHERE 
    id = ANY(:ids);
