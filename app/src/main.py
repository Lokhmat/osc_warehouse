import logging

import psycopg2

from aiomisc.log import basic_config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.applications_router import applications_router
from .routers.items_router import items_router
from .routers.users_router import users_router
from .routers.warehouse_router import warehouse_router

psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

tags_metadata = [
    {
        "name": "osk-warehouse",
        "description": "Main API schema.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router)
app.include_router(items_router)
app.include_router(users_router)
app.include_router(warehouse_router)

basic_config(logging.DEBUG, buffered=True)
