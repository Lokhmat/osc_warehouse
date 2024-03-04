from datetime import datetime
import logging
import typing

from fastapi import APIRouter, Depends, Header

from ..models import helpers
from ..models import applications
from ..models import users
from ..models.connector import db_connector
from ..utils import crypto

applications_router = APIRouter(tags=["applications"])


@applications_router.post(
    "/applications",
    response_model=applications.Application,
    responses=helpers.BAD_REQUEST_RESPONSE,
)
async def create_application(
    x_request_idempotency_token: typing.Annotated[str, Header()],
    new_application: applications.ChangeApplicationRequest,
    user: typing.Annotated[
        users.InternalUser, Depends(crypto.authorize_user_with_token)
    ],
):
    return applications.create_application(
        db_connector.engine,
        new_application.get_internal_application(x_request_idempotency_token, user.id),
    )


@applications_router.get(
    "/applications",
    response_model=applications.ApplicationWithActions,
    responses=helpers.NOT_FOUND_RESPONSE,
)
async def get_application(
    id: str,
    user: typing.Annotated[
        users.InternalUser, Depends(crypto.authorize_user_with_token)
    ],
):
    pass


@applications_router.patch(
    "/applications",
    response_model=applications.Application,
    responses={**helpers.BAD_REQUEST_RESPONSE, **helpers.NOT_FOUND_RESPONSE},
)
async def patch_application(
    id: str,
    new_application: applications.ChangeApplicationRequest,
    user: typing.Annotated[
        users.InternalUser, Depends(crypto.authorize_user_with_token)
    ],
):
    pass


@applications_router.put(
    "/applications/approve",
    response_model=helpers.EmptyResponse,
    responses=helpers.UNATHORIZED_RESPONSE,
)
async def approve_application(
    id: str,
    user: typing.Annotated[
        users.InternalUser, Depends(crypto.authorize_admin_with_token)
    ],
):
    pass


@applications_router.get(
    "/applications/list",
    response_model=applications.ApplicationsList,
    responses=helpers.UNATHORIZED_RESPONSE,
)
async def get_applications_list(
    limit: int,
    cursor: typing.Optional[datetime],
    user: typing.Annotated[
        users.InternalUser, Depends(crypto.authorize_user_with_token)
    ],
):
    pass
