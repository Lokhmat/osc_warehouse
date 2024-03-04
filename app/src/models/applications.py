from datetime import datetime
from enum import Enum
import logging
import typing

from pydantic import BaseModel

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY
from ..models.items import ItemWithCount, ListItemsWithCount
from ..models.users import ShortApiUser
from ..models.warehouse import SimpleWarehouse


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
    created_by: ShortApiUser
    approved_by: typing.Optional[ShortApiUser] = None
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


# def parse_to_application(
#     internal_application: InternalApplication,
#     creator: ApplicationModifier,
#     approver: typing.Optional[ApplicationModifier] = None,
# ) -> Application:
#     return Application(
#         id=internal_application.id,
#         application_data=ApplicationData(
#             name=internal_application.application_id,
#             description=internal_application.description,
#             type=internal_application.type,
#             status=internal_application.status,
#             created_by=creator,
#             approved_by=approver
#             sent_from_warehouse: typing.Optional[str] = None
#             sent_to_warehouse: typing.Optional[str] = None
#             linked_to_application: typing.Optional[str] = None
#         ),
#         application_payload=ApplicationPayload(),
#         created_at=internal_application.created_at,
#         updated_at=internal_application.updated_at,
#     )


def _get_application_payload(
    connection, item_id_to_count: typing.Mapping[str, id]
) -> ApplicationPayload:
    with open(
        f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/get_application_payload.sql"
    ) as sql:
        query = text(sql.read())
        items = connection.execute(query, {"item_ids": item_id_to_count.keys()}).all()
        return ApplicationPayload(
            items=[
                ItemWithCount(
                    id=item.id,
                    item_name=item.item_name,
                    codes=item.codes,
                    count=item_id_to_count[item.id],
                )
                for item in items
            ]
        )


def create_application(
    engine,
    new_application: InternalApplication,
) -> Application:
    with engine.connect() as connection:
        with open(
            f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/applications/create_application.sql"
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
                    name=application.name,
                    description=application.description,
                    type=application.type,
                    status=application.status,
                    created_by=ShortApiUser(
                        username=application.created_by_username,
                        first_name=application.created_by_firstname,
                        last_name=application.created_by_lastname,
                    ),
                    approved_by=ShortApiUser(
                        username=application.created_by_username,
                        first_name=application.created_by_firstname,
                        last_name=application.created_by_lastname,
                    )
                    if application.approved_by_username
                    else None,
                    sent_from_warehouse=SimpleWarehouse(
                        warehouse_name=application.sent_from_warehouse_name,
                        address=application.sent_from_warehouse_address,
                    )
                    if application.sent_from_warehouse_name
                    else None,
                    sent_to_warehouse=SimpleWarehouse(
                        warehouse_name=application.sent_to_warehouse_name,
                        address=application.sent_to_warehouse_address,
                    )
                    if application.sent_to_warehouse_name
                    else None,
                    linked_to_application_id=application.linked_to_application_id,
                ),
                application_payload=application_payload,
                created_at=application.created_at,
                updated_at=application.updated_at,
            )
        connection.commit()
    logging.info("Created item card")
    return result
