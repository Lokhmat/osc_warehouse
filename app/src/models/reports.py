from datetime import datetime
import logging
import typing

from pydantic import BaseModel

import pytz

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

from .connector import db_connector
from .applications import ApplicationType

MOSCOW_TIMEZONE = pytz.timezone("Europe/Moscow")


class Interval(BaseModel):
    from_date: datetime
    to_date: datetime


class ReportRequest(BaseModel):
    interval: Interval


class Report(BaseModel):
    header: typing.Optional[tuple]
    items: typing.List[tuple]


class RawRow(BaseModel):
    serial_number: int
    description: str
    warehouse_id: str
    item_id: str
    count: int
    deposited_at: typing.Optional[datetime] = None
    deducted_at: typing.Optional[datetime] = None
    created_by_id: str


class ReportGenerator:
    def __init__(self, engine):
        self.engine = engine

    def _get_header(self) -> tuple:
        return (
            "Производитель",
            "Модель",
            "Количество",
            "Склад",
            "Заявка создана",
            "Номер заявки",
            "Описание заявки",
            "Дата поступления",
            "Дата списания",
        )

    def _get_raw_data(
        self, interval: Interval, connection
    ) -> typing.Tuple[
        typing.List[RawRow], typing.List[str], typing.List[str], typing.List[str]
    ]:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/reports/get_payload.sql"
        ) as sql:
            query = text(sql.read())
            db_applications = connection.execute(query, interval.model_dump()).all()
            item_ids = set()
            warehouse_ids = set()
            created_by_ids = set()
            for row in db_applications:
                item_ids.update(list(row.payload.keys()))
                warehouse_ids.update(
                    [row.sent_from_warehouse_id, row.sent_to_warehouse_id]
                )
                created_by_ids.add(row.created_by_id)
            result = []
            for row in db_applications:
                result.extend(
                    [
                        RawRow(
                            serial_number=row.serial_number,
                            description=row.description,
                            warehouse_id=(
                                row.sent_to_warehouse_id
                                if row.type == ApplicationType.RECIEVE
                                else row.sent_from_warehouse_id
                            ),
                            item_id=key,
                            count=value,
                            deposited_at=(
                                row.updated_at
                                if row.type == ApplicationType.RECIEVE
                                else None
                            ),
                            deducted_at=(
                                row.updated_at
                                if row.type != ApplicationType.RECIEVE
                                else None
                            ),
                            created_by_id=row.created_by_id,
                        )
                        for key, value in row.payload.items()
                    ]
                )
            return result, list(item_ids), list(warehouse_ids), list(created_by_ids)

    def _get_items_data(self, item_ids: typing.List[str], connection):
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/reports/get_items.sql"
        ) as sql:
            query = text(sql.read())
            return connection.execute(query, {"ids": item_ids}).all()

    def _get_warehouses_data(self, warehouse_ids: typing.List[str], connection):
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/reports/get_warehouses.sql"
        ) as sql:
            query = text(sql.read())
            return connection.execute(query, {"ids": warehouse_ids}).all()

    def _get_users_names(self, created_by_ids: typing.List[str], connection):
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/reports/get_users_names.sql"
        ) as sql:
            query = text(sql.read())
            return connection.execute(query, {"ids": created_by_ids}).all()

    def prepare_report(self, interval: Interval):
        with self.engine.connect() as connection:
            rows, item_ids, warehouse_ids, created_by_ids = self._get_raw_data(
                interval, connection
            )
            items = {
                item.id: (item.manufacturer, item.model)
                for item in self._get_items_data(item_ids, connection)
            }
            warehouses = {
                warehouse.id: warehouse.warehouse_name
                for warehouse in self._get_warehouses_data(warehouse_ids, connection)
            }
            created_by = {
                user.id: f"{user.last_name} {user.first_name}"
                for user in self._get_users_names(created_by_ids, connection)
            }
            connection.commit()

        return Report(
            header=self._get_header(),
            items=[
                (
                    items.get(row.item_id)[0],
                    items.get(row.item_id)[1],
                    row.count,
                    warehouses.get(row.warehouse_id),
                    created_by.get(row.created_by_id),
                    row.serial_number,
                    row.description,
                    (
                        row.deposited_at.astimezone(MOSCOW_TIMEZONE).strftime(
                            "%H:%M %d %m %Y"
                        )
                        if row.deposited_at
                        else None
                    ),
                    (
                        row.deducted_at.astimezone(MOSCOW_TIMEZONE).strftime(
                            "%H:%M %d %m %Y"
                        )
                        if row.deducted_at
                        else None
                    ),
                )
                for row in rows
            ],
        )


report_generator = ReportGenerator(db_connector.engine)
