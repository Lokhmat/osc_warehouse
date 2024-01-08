from datetime import datetime
import logging
import typing
import uuid

from pydantic import BaseModel

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

class Token(BaseModel):
    access_token: str
    token_type: str

class SimpleUser(BaseModel):
    username: str
    password_hash: str

class User(SimpleUser):
    id: str
    first_name: str
    last_name: str
    phone_number: str
    about: str
    created_at: datetime

class ApiUser(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    phone_number: str
    about: str
    created_at: datetime

    def get_user_model(self, pwd_context) -> User:
        return User(
            id=str(uuid.uuid4()),
            username=self.username,
            password_hash=pwd_context.hash(self.password),
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            about=self.about,
            created_at=self.created_at
        )

def get_simple_user(engine, username) -> typing.Optional[SimpleUser]:
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/get_simple_user.sql') as sql:
            query = text(sql.read())
            args = {'username': username}
            for row in connection.execute(query, args):
                return SimpleUser(username=row.username, password_hash=row.password_hash)
    return None

def create_user(engine, user: ApiUser, pwd_context):
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/create_user.sql') as sql:
            query = text(sql.read())
            args = user.get_user_model(pwd_context).model_dump()
            connection.execute(query, args)
        connection.commit()
    logging.info('Created user successfully')
