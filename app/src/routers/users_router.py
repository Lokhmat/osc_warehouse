from datetime import datetime, timedelta
import logging
import os
import typing

from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm

from jose import jwt
from passlib.context import CryptContext

from ..constants import JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from ..models.connector import DBConnector
from ..models import users

users_router = APIRouter(tags=['users'])

connector = DBConnector()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expires_at = datetime.utcnow() + expires_delta
    to_encode.update({'exp': expires_at})
    encoded_jwt = jwt.encode(to_encode, key=os.environ.get('JWT_SECRET_KEY'), algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_password(password: str, password_hash: str):
    return pwd_context.verify(password, password_hash)

def authorize_user(connection, username: str, password: str) -> typing.Optional[users.SimpleUser]:
    user = users.get_simple_user(connection, username)
    if not user:
        logging.info('Could not fing user in DB')
        return False
    if not verify_password(password, user.password_hash):
        logging.info('Failed to verify user\'s password')
        return False
    return user

@users_router.post('/users/authorize', response_model=users.Token)
async def authorize(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authorize_user(connector.engine, form_data.username, form_data.password)
    if not user:
        logging.warning('Could not find user')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


#TODO: А кто может создавать пользователей??
@users_router.post('/users')
async def create_user(
    user: users.ApiUser
):
    users.create_user(connector.engine, user, pwd_context)
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}
