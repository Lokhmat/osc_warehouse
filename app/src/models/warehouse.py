from datetime import datetime
import logging
import typing

from pydantic import BaseModel

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY


class Warehouse(BaseModel):
    id: str
    warehouse_name: str
    address: str
    created_at: datetime
    updated_at: datetime


class SimpleWarehouse(BaseModel):
    warehouse_name: str
    address: str

    def get_warehouse_model(self, idempotency_token: str) -> Warehouse:
        return Warehouse(
            id=idempotency_token,
            warehouse_name=self.warehouse_name,
            address=self.address,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class WarehouseUpdate(BaseModel):
    id: str
    warehouse_name: typing.Optional[str] = None
    address: typing.Optional[str] = None


class ApiWarehouseList(BaseModel):
    items: typing.List[Warehouse]


def create_warehouse(
    engine, idempotency_token, warehouse: SimpleWarehouse
) -> Warehouse:
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/warehouse/create_warehouse.sql"
        ) as sql:
            query = text(sql.read())
            args = warehouse.get_warehouse_model(idempotency_token).model_dump()
            result = connection.execute(query, args).all()
            if not result:
                raise RuntimeError("Failed to create warehouse")
            logging.info("Successfully created warehouse")
        connection.commit()
    return Warehouse(**result[0]._mapping)


def get_warehouse_list(engine) -> typing.List[Warehouse]:
    result: typing.List[Warehouse] = []
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/warehouse/get_warehouse_list.sql"
        ) as sql:
            query = text(sql.read())
            for row in connection.execute(query):
                result.append(Warehouse(**row._mapping))
    return result


def get_warehouse_by_id(engine, id: str) -> typing.Optional[Warehouse]:
    result: typing.Optional[Warehouse] = None
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/warehouse/get_warehouse_by_id.sql"
        ) as sql:
            query = text(sql.read())
            for row in connection.execute(query, {"id": id}):
                result = Warehouse(**row._mapping)
        connection.commit()
    return result


def update_warehouse(
    engine, warehouse_update: WarehouseUpdate
) -> typing.Optional[Warehouse]:
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/warehouse/update_warehouse.sql"
        ) as sql:
            query = text(sql.read())
            args = warehouse_update.model_dump()
            result = connection.execute(query, args).all()
            if not result:
                return None
        connection.commit()
        logging.info("Successfully updated warehouse")
        return Warehouse(**result[0]._mapping)


def delete_warehouse(engine, id: str) -> None:
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/warehouse/delete_warehouse.sql"
        ) as sql:
            query = text(sql.read())
            connection.execute(query, {"id": id})
            connection.commit()
            logging.info("Successfully deleted warehouse")
