CREATE TABLE app.warehouse_to_items (
    warehouse_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    count BIGINT NOT NULL,

    PRIMARY KEY (warehouse_id, item_id)
);
