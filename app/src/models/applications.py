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


class ApplicationAction(str, Enum):
    REJECT = "reject"
    APPROVE = "approve"
    EDIT = "edit"


class InternalApplication(BaseModel):
    application_id: str
    name: str
    description: str
    type: ApplicationType
    status: ApplicationStatus
    payload: typing.Mapping[str, int]
    created_by_id: str
    approved_by_id: typing.Optional[str] = None
    sent_from_warehouse_id: typing.Optional[str] = None
    sent_to_warehouse_id: typing.Optional[str] = None
    linked_to_application_id: typing.Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApplicationModifier(BaseModel):
    username: str
    first_name: str
    last_name: str


class ApplicationData(BaseModel):
    name: str
    description: str
    type: ApplicationType
    status: ApplicationStatus
    created_by: ApiUser
    approved_by: typing.Optional[ApiUser] = None
    sent_from_warehouse: typing.Optional[SimpleWarehouse] = None
    sent_to_warehouse: typing.Optional[SimpleWarehouse] = None
    linked_to_application_id: typing.Optional[str] = None


class MutableApplicationData(BaseModel):
    name: str
    description: str
    type: ApplicationType
    status: ApplicationStatus
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
    cursor: typing.Optional[datetime]


class ChangeApplicationRequest(BaseModel):
    application_data: MutableApplicationData
    application_payload: ApplicationPayload

    def get_internal_application(self, idempotency_token: str, created_by_id: str):
        return InternalApplication(
            application_id=idempotency_token,
            name=self.application_data.name,
            description=self.application_data.description,
            type=self.application_data.type,
            status=self.application_data.status,
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
        created_by = get_user_by_id_transaction(
            connection, new_application.created_by_id
        )
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
                    name=application.name,
                    description=application.description,
                    type=application.type,
                    status=application.status,
                    created_by=convert_user(created_by),
                    approved_by=None,
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
    item: typing.Optional[Application] = None
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_application_by_id.sql"
        ) as sql:
            query = text(sql.read())
            application = connection.execute(query, {"application_id": id}).all()
            if not application:
                return None
            application = application[0]
            application_payload = _get_application_payload(
                connection, application.payload
            )
            created_by = get_user_by_id_transaction(
                connection, application.created_by_id
            )
            approved_by = (
                get_user_by_id_transaction(connection, application.approved_by_id)
                if application.approved_by_id
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
            return Application(
                id=application.id,
                application_data=ApplicationData(
                    name=application.name,
                    description=application.description,
                    type=application.type,
                    status=application.status,
                    created_by=convert_user(created_by),
                    approved_by=convert_user(approved_by) if approved_by else None,
                    sent_from_warehouse=sent_from_warehouse,
                    sent_to_warehouse=sent_to_warehouse,
                    linked_to_application_id=application.linked_to_application_id,
                ),
                application_payload=application_payload,
                created_at=application.created_at,
                updated_at=application.updated_at,
            )
