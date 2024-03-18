from datetime import datetime
from enum import Enum
import logging
import typing

from pydantic import BaseModel

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY
from ..models import helpers
from ..models.items import ItemWithCount, ListItemsWithCount
from ..models.users import ApiUser, get_user_by_id_transaction
from ..models.warehouse import SimpleWarehouse, get_simple_warehouse_by_id_transaction
from ..utils.converters import convert_user


class ApplicationType(str, Enum):
    SEND = "send"
    RECIEVE = "recieve"
    DEFECT = "defect"
    USE = "use"
    REVERT = "revert"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    REJECTED = "rejected"
    DELETED = "deleted"


class ApplicationAction(str, Enum):
    REJECT = "reject"
    APPROVE = "approve"
    EDIT = "edit"
    DELETE = "delete"


class InternalApplication(BaseModel):
    application_id: str
    description: str
    type: ApplicationType
    status: ApplicationStatus
    payload: typing.Mapping[str, int]
    created_by_id: str
    finished_by_id: typing.Optional[str] = None
    sent_from_warehouse_id: typing.Optional[str] = None
    sent_to_warehouse_id: typing.Optional[str] = None
    linked_to_application_id: typing.Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApplicationData(BaseModel):
    serial_number: int
    description: str
    type: ApplicationType
    status: ApplicationStatus
    created_by: ApiUser
    finished_by: typing.Optional[ApiUser] = None
    sent_from_warehouse: typing.Optional[SimpleWarehouse] = None
    sent_to_warehouse: typing.Optional[SimpleWarehouse] = None
    linked_to_application_id: typing.Optional[str] = None


class MutableApplicationData(BaseModel):
    description: str
    type: ApplicationType
    sent_from_warehouse_id: typing.Optional[str] = None
    sent_to_warehouse_id: typing.Optional[str] = None
    linked_to_application_id: typing.Optional[str] = None


class ApplicationPayload(ListItemsWithCount):
    def to_db_view(self) -> typing.Mapping[str, int]:
        return {item.id: item.count for item in self.items}


class Application(BaseModel):
    id: str
    application_data: ApplicationData
    application_payload: ApplicationPayload
    created_at: datetime
    updated_at: datetime


class ApplicationWithActions(Application):
    actions: typing.List[ApplicationAction]


class ApplicationsList(BaseModel):
    items: typing.List[Application]
    cursor: typing.Optional[datetime] = None


class ChangeApplicationRequest(BaseModel):
    application_data: MutableApplicationData
    application_payload: ApplicationPayload

    def get_internal_application(self, idempotency_token: str, created_by_id: str):
        return InternalApplication(
            application_id=idempotency_token,
            description=self.application_data.description,
            type=self.application_data.type,
            status=ApplicationStatus.PENDING,
            payload=self.application_payload.to_db_view(),
            created_by_id=created_by_id,
            sent_from_warehouse_id=self.application_data.sent_from_warehouse_id,
            sent_to_warehouse_id=self.application_data.sent_to_warehouse_id,
            linked_to_application_id=self.application_data.linked_to_application_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


def _get_application_payload(
    connection, item_id_to_count: typing.Mapping[str, id]
) -> ApplicationPayload:
    with open(
        f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_application_payload.sql"
    ) as sql:
        query = text(sql.read())
        items = connection.execute(
            query, {"item_ids": list(item_id_to_count.keys())}
        ).all()
        return ApplicationPayload(
            items=[
                ItemWithCount(
                    id=item.id,
                    item_name=item.item_name,
                    item_type=item.item_type,
                    codes=item.codes,
                    manufacturer=item.manufacturer,
                    model=item.model,
                    description=item.description,
                    count=item_id_to_count[item.id],
                )
                for item in items
            ]
        )


def _repack_payload_from_application(
    warehouse_id, item_id_to_count: typing.Mapping[str, id]
) -> typing.List[tuple]:
    warehouse_ids = []
    item_ids = []
    counts = []
    for item_id, count in item_id_to_count.items():
        warehouse_ids.append(warehouse_id)
        item_ids.append(item_id)
        counts.append(count)
    return warehouse_ids, item_ids, counts


def _validate_application(connection, new_application: ChangeApplicationRequest):
    created_by = get_user_by_id_transaction(connection, new_application.created_by_id)
    if not created_by:
        raise helpers.get_bad_request(
            "Нельзя создать заявку от имени этого пользователя"
        )
    sent_to_warehouse = (
        get_simple_warehouse_by_id_transaction(
            connection, new_application.sent_to_warehouse_id
        )
        if new_application.sent_to_warehouse_id
        else None
    )
    if bool(new_application.sent_to_warehouse_id) != bool(sent_to_warehouse):
        raise helpers.get_bad_request("Склад отправки не существует")
    sent_from_warehouse = (
        get_simple_warehouse_by_id_transaction(
            connection, new_application.sent_from_warehouse_id
        )
        if new_application.sent_from_warehouse_id
        else None
    )
    if bool(new_application.sent_from_warehouse_id) != bool(sent_from_warehouse):
        raise helpers.get_bad_request("Склад получения не существует")
    return created_by, sent_from_warehouse, sent_to_warehouse


def _get_application_data(connection, application):
    application_payload = _get_application_payload(connection, application.payload)
    created_by = get_user_by_id_transaction(connection, application.created_by_id)
    finished_by = (
        get_user_by_id_transaction(connection, application.finished_by_id)
        if application.finished_by_id
        else None
    )
    sent_to_warehouse = (
        get_simple_warehouse_by_id_transaction(
            connection, application.sent_to_warehouse_id
        )
        if application.sent_to_warehouse_id
        else None
    )
    sent_from_warehouse = (
        get_simple_warehouse_by_id_transaction(
            connection, application.sent_from_warehouse_id
        )
        if application.sent_from_warehouse_id
        else None
    )
    return (
        application_payload,
        created_by,
        finished_by,
        sent_to_warehouse,
        sent_from_warehouse,
    )


def get_application_with_actions(
    application: Application,
    actions: typing.List[ApplicationAction],
):
    return ApplicationWithActions(
        id=application.id,
        application_data=application.application_data,
        application_payload=application.application_payload,
        created_at=application.created_at,
        updated_at=application.updated_at,
        actions=actions,
    )


def create_application(
    engine,
    new_application: InternalApplication,
) -> Application:
    with engine.connect() as connection:
        created_by, sent_from_warehouse, sent_to_warehouse = _validate_application(
            connection, new_application
        )
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/create_application.sql"
        ) as sql:
            # Может все таки переписать на классы?
            # Кривовато получается что тут нужно импортить модуль другой модели
            query = text(sql.read())
            args = new_application.model_dump()
            application = connection.execute(query, args).all()
            if not application:
                raise RuntimeError("Failed to create application")
            application = application[0]
            application_payload = _get_application_payload(
                connection, application.payload
            )
            result = Application(
                id=application.id,
                application_data=ApplicationData(
                    serial_number=application.serial_number,
                    description=application.description,
                    type=application.type,
                    status=application.status,
                    created_by=convert_user(created_by),
                    finished_by=None,
                    sent_from_warehouse=sent_from_warehouse,
                    sent_to_warehouse=sent_to_warehouse,
                    linked_to_application_id=application.linked_to_application_id,
                ),
                application_payload=application_payload,
                created_at=application.created_at,
                updated_at=application.updated_at,
            )
        connection.commit()
    logging.info("Created item card")
    return result


def update_application(
    engine, new_application: InternalApplication, user_id: str
) -> Application:
    with engine.connect() as connection:
        created_by, sent_from_warehouse, sent_to_warehouse = _validate_application(
            connection, new_application
        )
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/patch_application.sql"
        ) as sql:
            query = text(sql.read())
            args = new_application.model_dump()
            application = connection.execute(query, args).all()
            if not application:
                raise RuntimeError("Failed to create application")
            application = application[0]
            application_payload = _get_application_payload(
                connection, application.payload
            )
            result = Application(
                id=application.id,
                application_data=ApplicationData(
                    serial_number=application.serial_number,
                    description=application.description,
                    type=application.type,
                    status=application.status,
                    created_by=convert_user(created_by),
                    finished_by=None,
                    sent_from_warehouse=sent_from_warehouse,
                    sent_to_warehouse=sent_to_warehouse,
                    linked_to_application_id=application.linked_to_application_id,
                ),
                application_payload=application_payload,
                created_at=application.created_at,
                updated_at=application.updated_at,
            )
        connection.commit()
    logging.info("Created item card")
    return result


def get_application_by_id(
    engine,
    id: str,
):
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            application = connection.execute(query, {"application_id": id}).all()
            if not application:
                return None
            application = application[0]
            (
                application_payload,
                created_by,
                finished_by,
                sent_to_warehouse,
                sent_from_warehouse,
            ) = _get_application_data(connection, application)
            return Application(
                id=application.id,
                application_data=ApplicationData(
                    serial_number=application.serial_number,
                    description=application.description,
                    type=application.type,
                    status=application.status,
                    created_by=convert_user(created_by),
                    finished_by=convert_user(finished_by) if finished_by else None,
                    sent_from_warehouse=sent_from_warehouse,
                    sent_to_warehouse=sent_to_warehouse,
                    linked_to_application_id=application.linked_to_application_id,
                ),
                application_payload=application_payload,
                created_at=application.created_at,
                updated_at=application.updated_at,
            )


def approve_application(engine, id: str, approver_id: str):
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            application = connection.execute(query, {"application_id": id}).all()
            if not application:
                raise helpers.NOT_FOUND_ERROR
            application = application[0]
            if application.status != ApplicationStatus.PENDING:
                raise helpers.get_bad_request(
                    "Подтвердить можно заявку только в не финальном статусе"
                )
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/approve_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            result = connection.execute(
                query, {"application_id": id, "finished_by_id": approver_id}
            ).all()
            sent_from_warehouse_id, sent_to_warehouse_id, application_type, payload = (
                result[0].sent_from_warehouse_id,
                result[0].sent_to_warehouse_id,
                result[0].type,
                result[0].payload,
            )
        if sent_from_warehouse_id and (
            not sent_to_warehouse_id
            or sent_to_warehouse_id
            and application_type == ApplicationType.SEND
        ):
            with open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/deduct_items_from_warehouse.sql"
            ) as sql:
                query = text(sql.read())
                _, item_ids, counts = _repack_payload_from_application(
                    sent_from_warehouse_id, payload
                )
                result = connection.execute(
                    query,
                    {
                        "warehouse_id": sent_from_warehouse_id,
                        "item_ids": item_ids,
                        "counts": counts,
                    },
                )
                if result.rowcount != len(item_ids):
                    connection.rollback()
                    raise helpers.get_bad_request(
                        "Нельзя списать больше товаров чем есть на складе"
                    )
        if sent_to_warehouse_id and (
            not sent_from_warehouse_id
            or sent_from_warehouse_id
            and application_type == ApplicationType.RECIEVE
        ):
            with open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/deposit_items_on_warehouse.sql"
            ) as sql:
                query = text(sql.read())
                warehouse_ids, item_ids, counts = _repack_payload_from_application(
                    sent_to_warehouse_id, payload
                )
                connection.execute(
                    query,
                    {
                        "warehouse_ids": warehouse_ids,
                        "item_ids": item_ids,
                        "counts": counts,
                    },
                )
        connection.commit()
    logging.info(f"Successfully approved application {id}")


def reject_application(engine, id: str, reviewer_id: str):
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            application = connection.execute(query, {"application_id": id}).all()
            if not application:
                raise helpers.NOT_FOUND_ERROR
            application = application[0]
            if application.status != ApplicationStatus.PENDING:
                raise helpers.get_bad_request(
                    "Отклонить можно заявку только в не финальном статусе"
                )
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/reject_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            result = connection.execute(
                query, {"application_id": id, "finished_by_id": reviewer_id}
            ).all()
            if not result:
                raise helpers.NOT_FOUND_ERROR
        connection.commit()
    logging.info(f"Successfully rejected application {id}")


def delete_application(engine, id: str, user_id: str):
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            application = connection.execute(query, {"application_id": id}).all()
            if not application:
                raise helpers.NOT_FOUND_ERROR
            application = application[0]
            if application.created_by_id != user_id:
                raise helpers.get_bad_request(
                    "Только создатель заявки может ее отклонить"
                )
            if application.status != ApplicationStatus.PENDING:
                raise helpers.get_bad_request(
                    "Удалить можно заявку только в не финальном статусе"
                )
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/delete_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            connection.execute(query, {"application_id": id, "finished_by_id": user_id})
        connection.commit()
    logging.info(f"Successfully deleted application {id}")


def get_applications_list(
    engine,
    chained_to_user_id: typing.Optional[str],
    cursor: datetime,
    limit: int,
    status_filter: typing.Optional[ApplicationStatus],
):
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_applications_list.sql"
        ) as sql:
            query = text(sql.read())
            applications = connection.execute(
                query,
                {
                    "cursor": cursor,
                    "limit": limit,
                    "chained_to_user_id": chained_to_user_id,
                    "status_filter": status_filter,
                },
            ).all()
            result = ApplicationsList(
                items=[],
                cursor=applications[-1].created_at
                if len(applications) == limit
                else None,
            )
            for application in applications:
                (
                    application_payload,
                    created_by,
                    finished_by,
                    sent_to_warehouse,
                    sent_from_warehouse,
                ) = _get_application_data(connection, application)
                result.items.append(
                    Application(
                        id=application.id,
                        application_data=ApplicationData(
                            serial_number=application.serial_number,
                            description=application.description,
                            type=application.type,
                            status=application.status,
                            created_by=convert_user(created_by),
                            finished_by=convert_user(finished_by)
                            if finished_by
                            else None,
                            sent_from_warehouse=sent_from_warehouse,
                            sent_to_warehouse=sent_to_warehouse,
                            linked_to_application_id=application.linked_to_application_id,
                        ),
                        application_payload=application_payload,
                        created_at=application.created_at,
                        updated_at=application.updated_at,
                    )
                )
            return result
