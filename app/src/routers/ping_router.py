import logging

from fastapi import APIRouter

ping_router = APIRouter(tags=['ping'])

@ping_router.get("/ping")
async def ping():
    logging.debug("Successfull ping")
    return {"status": 'ok'}
