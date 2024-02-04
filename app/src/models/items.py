import logging
import typing

from pydantic import BaseModel

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY


class Item(BaseModel):
    id: str
    item_name: str
    codes: typing.List[str]


class CreateItem(BaseModel):
    item_name: str
    codes: typing.List[str]

    def get_item(self, idempotency_token: str) -> Item:
        return Item(id=idempotency_token, item_name=self.item_name, codes=self.codes)


class UpdateItem(BaseModel):
    id: str
    item_name: typing.Optional[str] = None
    codes: typing.Optional[typing.List[str]] = None


class ItemWithCount(Item):
    count: int


class ItemWithWarehouseCount(Item):
    warehouse_count: typing.Mapping[
        str, int
    ] = dict()  # warehouse name to item count on warehouse


class ListItems(BaseModel):
    items: typing.List[Item]


class ListItemsWithCount(BaseModel):
    items: typing.List[ItemWithCount]


def create_item(engine, idempotency_token: str, new_item: CreateItem):
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/items/create_item.sql"
        ) as sql:
            query = text(sql.read())
            args = new_item.get_item(idempotency_token).model_dump()
            for row in connection.execute(query, args):
                result = Item(**row._mapping)
        connection.commit()
    logging.info("Created item card")
    return result


def get_item_by_id(engine, item_id: str):
    item: typing.Optional[ItemWithWarehouseCount] = None
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/items/get_item_by_id.sql"
        ) as sql:
            query = text(sql.read())
            for row in connection.execute(query, {"item_id": item_id}):
                item = ItemWithWarehouseCount(**row._mapping)
        if item:
            with open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/items/get_item_count_by_id.sql"
            ) as sql:
                query = text(sql.read())
                for row in connection.execute(query, {"item_id": item_id}):
                    item.warehouse_count[row.warehouse_name] = row.item_count
        connection.commit()
    return item


def get_items_list(engine):
    items: typing.List[Item] = []
    with engine.connect() as connection:
        with open(f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/items/get_items.sql") as sql:
            query = text(sql.read())
            for row in connection.execute(query):
                items.append(Item(**row._mapping))
        connection.commit()
    return ListItems(items=items)


def get_items_by_warehouse(engine, warehouse_id: str):
    items: typing.List[ItemWithCount] = []
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/items/get_item_count_by_warehouse.sql"
        ) as sql:
            query = text(sql.read())
            for row in connection.execute(query, {"warehouse_id": warehouse_id}):
                items.append(ItemWithCount(**row._mapping))
        connection.commit()
    return ListItemsWithCount(items=items)


def update_item(engine, new_item_data: UpdateItem):
    result: typing.Optional[Item] = None
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/items/update_item.sql"
        ) as sql:
            query = text(sql.read())
            args = new_item_data.model_dump()
            for row in connection.execute(query, args):
                result = Item(**row._mapping)
        connection.commit()
    return result


def delete_item(engine, item_id: str):
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/items/delete_item.sql"
        ) as sql:
            query = text(sql.read())
            connection.execute(query, {"item_id": item_id})
        connection.commit()
