import os
import logging

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

def get_ping_status(connection) -> str:
    with open(f'{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/ping.sql') as sql:
        query = text(sql.read())
        args = {'id': '1'}
        for row in connection.execute(query, args):
            return row.status_of_request
