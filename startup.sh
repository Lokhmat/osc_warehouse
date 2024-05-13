#!/bin/bash

docker compose up --build --detach

crontab -r

crontab -l > mycron
echo "1 * * * * sudo docker exec -t database pg_dumpall -c > dump_$(date +%Y-%m-%d_%H_%M_%S).sql" >> mycron
crontab mycron
rm mycron

docker exec -it database /bin/bash -c ".venv/bin/python3 -m pgmigrate -c '' migrate -t latest"
