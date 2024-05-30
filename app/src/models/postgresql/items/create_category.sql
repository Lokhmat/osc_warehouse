INSERT INTO
    app.item_category (category_name)
VALUES
    (:category_name) ON CONFLICT (category_name) DO NOTHING;