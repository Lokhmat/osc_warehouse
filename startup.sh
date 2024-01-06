#!/bin/bash

docker compose up --build --detach

docker exec -it database /bin/bash -c ".venv/bin/python3 -m pgmigrate -c '' migrate -t latest"
