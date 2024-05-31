SELECT 
    id,
    first_name,
    last_name
FROM
    app.users
WHERE 
    id = ANY(:ids);
