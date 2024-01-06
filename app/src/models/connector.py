import os

from sqlalchemy import create_engine

DB_CONTAINER_NAME='database'

class DBConnector:
    def __init__(self):
        user = os.environ.get('PGUSER')
        password = os.environ.get('PGPASSWORD')
        host = DB_CONTAINER_NAME
        port = os.environ.get('PGPORT')
        db = os.environ.get('PGDATABASE')

        database_url = f'postgresql://{user}:{password}@{host}:{port}/{db}'

        self.engine = create_engine(
            database_url
        )
