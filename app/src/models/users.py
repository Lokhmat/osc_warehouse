from datetime import datetime
import logging
import typing

from pydantic import BaseModel

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

class Token(BaseModel):
    access_token: str
    token_type: str

class SimpleUser(BaseModel):
    username: str
    password_hash: str

class InternalUser(SimpleUser):
    first_name: str
    last_name: str
    phone_number: str
    created_at: datetime
    updated_at: datetime
    warehouses: typing.List[str]
    is_admin: bool
    is_reviewer: bool
    is_super_user: bool

class UpdateUser(BaseModel):
    username: str
    first_name: typing.Optional[str] = None
    last_name: typing.Optional[str] = None
    phone_number: typing.Optional[str] = None
    warehouses: typing.Optional[typing.List[str]] = None
    is_admin: typing.Optional[bool] = None
    is_reviewer: typing.Optional[bool] = None
    is_super_user: typing.Optional[bool] = None
    password_hash: typing.Optional[str] = None

class ApiUser(BaseModel):
    username: str
    first_name: str
    last_name: str
    phone_number: str
    warehouses: typing.List[str]
    is_admin: bool
    is_reviewer: bool
    is_super_user: bool

class CreateApiUser(ApiUser):
    password: str

    def get_internal_user(self, hash_f) -> InternalUser:
        return InternalUser(
            username = self.username,
            password_hash = hash_f(self.password),
            first_name = self.first_name,
            last_name = self.last_name,
            phone_number = self.phone_number,
            created_at = datetime.utcnow(),
            updated_at = datetime.utcnow(),
            warehouses = self.warehouses,
            is_admin = self.is_admin,
            is_reviewer = self.is_reviewer,
            is_super_user = self.is_super_user
        ) 

class UpdateApiUser(BaseModel):
    username: str
    first_name: typing.Optional[str] = None
    last_name: typing.Optional[str] = None
    phone_number: typing.Optional[str] = None
    warehouses: typing.Optional[typing.List[str]] = None
    is_admin: typing.Optional[bool] = None
    is_reviewer: typing.Optional[bool] = None
    is_super_user: typing.Optional[bool] = None
    password: typing.Optional[str] = None

    def get_update_user(self, hash_f):
        return UpdateUser(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            warehouses=self.warehouses,
            is_admin=self.is_admin,
            is_reviewer=self.is_reviewer,
            is_super_user=self.is_super_user,
            password_hash=None if not self.password else hash_f(self.password),
        )

class ListApiUsers(BaseModel):
    items: typing.List[ApiUser]

def get_simple_user(engine, username: str) -> typing.Optional[SimpleUser]:
    result: typing.Optional[SimpleUser] = None
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/users/get_simple_user.sql') as sql:
            query = text(sql.read())
            args = {'username': username}
            for row in connection.execute(query, args):
                result = SimpleUser(username=row.username, password_hash=row.password_hash)
        connection.commit()
    return result

def get_user(engine, username: str) -> typing.Optional[InternalUser]:
    result: typing.Optional[InternalUser] = None
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/users/get_user.sql') as sql:
            query = text(sql.read())
            args = {'username': username}
            for row in connection.execute(query, args):
                result = InternalUser(**row._mapping)
        connection.commit()
    return result

def get_users(engine) -> typing.List[InternalUser]:
    result: typing.List[InternalUser] = []
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/users/get_users.sql') as sql:
            query = text(sql.read())
            for row in connection.execute(query):
                result.append(InternalUser(**row._mapping))
        connection.commit()
    return result

def create_user(engine, user: CreateApiUser, hash_f):
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/users/create_user.sql') as sql:
            query = text(sql.read())
            args = user.get_internal_user(hash_f).model_dump()
            connection.execute(query, args)
        connection.commit()
    logging.info('Created user successfully')

def delete_user(engine, username: str):
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/users/delete_user.sql') as sql:
            query = text(sql.read())
            connection.execute(query, {'username': username})
        connection.commit()
    logging.info('Deleted user successfully')

def update_user(engine, new_data: UpdateApiUser, hash_f) -> ApiUser:
    with engine.connect() as connection:
        with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/users/update_user.sql') as sql:
            query = text(sql.read())
            args = new_data.get_update_user(hash_f).model_dump()
            result = connection.execute(query, args).all()
            if not result:
                raise RuntimeError('Failed to update user data')
            logging.info('Updated user successfully')
        connection.commit()
        return ApiUser(**result[0]._mapping)
