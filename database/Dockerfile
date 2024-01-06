FROM postgres:14.10

RUN apt-get update

RUN apt-get install -y python3 python3-pip python3-venv

RUN python3 -m venv .venv

RUN . .venv/bin/activate

# psycopg2 fix aparently
RUN apt-get install -y libpq-dev

RUN .venv/bin/pip3 install --no-cache-dir --upgrade yandex-pgmigrate

COPY ./migrations /migrations
