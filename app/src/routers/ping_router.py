import logging

from fastapi import APIRouter

from ..models.connector import DBConnector
from ..models.ping import *

ping_router = APIRouter(tags=['ping'])

@ping_router.get("/ping")
async def ping():
    connector = DBConnector()
    with connector.engine.connect() as connection:
        result = get_ping_status(connection=connection)
        logging.debug("Successfull ping")
        return {"status": result}
