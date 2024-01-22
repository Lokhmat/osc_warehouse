import typing

from fastapi import APIRouter, Depends

from ..models import helpers
from ..models import warehouse
from ..models.connector import db_connector
from ..utils import crypto

warehouse_router = APIRouter(tags=['warehouse'])


@warehouse_router.post('/warehouse', response_model=warehouse.Warehouse)
async def create_warehouse(api_warehouse: warehouse.SimpleWarehouse, is_valid_request: typing.Annotated[bool, Depends(crypto.authorize_admin_with_token)]):
    return warehouse.create_warehouse(engine=db_connector.engine, warehouse=api_warehouse)

@warehouse_router.get('/warehouse', response_model=warehouse.Warehouse)
async def get_warehouse_by_id(warehouse_id: str, is_valid_request: typing.Annotated[bool, Depends(crypto.authorize_admin_with_token)]):
    db_warehouse = warehouse.get_warehouse_by_id(engine=db_connector.engine, id=warehouse_id)
    if not db_warehouse:
        raise helpers.NOT_FOUND_ERROR
    return db_warehouse

@warehouse_router.get('/warehouse/list', response_model=warehouse.ApiWarehouseList)
async def get_warehouse_list(is_valid_request: typing.Annotated[bool, Depends(crypto.authorize_admin_with_token)]):
    return warehouse.ApiWarehouseList(items=warehouse.get_warehouse_list(engine=db_connector.engine))

@warehouse_router.put('/warehouse', response_model=warehouse.Warehouse)
async def update_warehouse(warehouse_update: warehouse.WarehouseUpdate, is_valid_request: typing.Annotated[bool, Depends(crypto.authorize_admin_with_token)]):
    return warehouse.update_warehouse(engine=db_connector.engine, warehouse_update=warehouse_update)

@warehouse_router.delete('/warehouse', response_model=helpers.EmptyResponse)
async def delete_warehouse(warehouse_id: str, is_valid_request: typing.Annotated[bool, Depends(crypto.authorize_admin_with_token)]):
    warehouse.delete_warehouse(engine=db_connector.engine, id=warehouse_id)
    return helpers.EmptyResponse()
