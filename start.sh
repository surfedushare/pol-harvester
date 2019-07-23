#!/usr/bin/env bash


# This script starts all services that are needed to run the harvester
# It makes available an API on localhost:8000, which nginx can expose
# You can also run harvest commands through docker-compose. For example:
#     docker-compose run harvester ./manage.py freeze_edurep -f <freeze-name> -c <collection-name> -i <input-file>

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit 1
fi


# Storing the git commit hash that belongs to this start
# This hash will be included in command output to be able to replicate results
export DJANGO_GIT_COMMIT=$(git rev-parse HEAD)
echo $DJANGO_GIT_COMMIT > harvester/.commit


# Clearing static files in order to collect them again
[[ -f "statics" ]] && rm -r statics


# (Re-)building the containers and (re)starting them
docker-compose build
docker-compose down
docker-compose  -f docker-compose.yml -f docker-compose.prd.yml up -d
