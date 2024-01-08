import logging

from aiomisc.log import basic_config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.users_router import users_router

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

app.include_router(users_router)

basic_config(logging.DEBUG, buffered=True)
