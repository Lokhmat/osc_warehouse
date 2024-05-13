#!/bin/bash

docker compose up --build --detach;

crontab -r;
echo "0 0 1,20 * * rm postgres_dump.gzip; sudo docker exec -t database pg_dumpall -c | gzip > ./postgres_dump.gzip" >> mycron;
crontab mycron;
rm mycron;

docker exec -it database /bin/bash -c ".venv/bin/python3 -m pgmigrate -c '' migrate -t latest";
