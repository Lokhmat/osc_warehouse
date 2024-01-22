import typing

from ..models import users

def convert_user(user: users.InternalUser) -> users.ApiUser:
    return users.ApiUser(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        warehouses=user.warehouses,
        is_admin=user.is_admin,
        is_reviewer=user.is_reviewer,
        is_super_user=user.is_super_user,
    )

def convert_users(users: typing.List[users.InternalUser]) -> typing.List[users.ApiUser]:
    return [convert_user(user) for user in users]
