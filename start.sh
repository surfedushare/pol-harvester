#!/usr/bin/env bash


# This script starts all services that are needed to run the harvester
# It makes available an API on localhost:8000, which nginx can expose
# You can also run harvest commands through docker-compose. For example:
#     docker-compose run harvester ./manage.py freeze_edurep -f <freeze-name> -c <collection-name> -i <input-file>

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit 1
fi


# Set the environment variables and activates the Conda environment
source activate.sh


# Storing the git commit hash that belongs to this start
# This hash will be included in command output to be able to replicate results
export DJANGO_GIT_COMMIT=$(git rev-parse HEAD)
echo $DJANGO_GIT_COMMIT > harvester/.commit


# Clearing static files in order to collect them again
[[ -f "harvester/statics" ]] && rm -r harvester/statics


# Deploying containers to the stack
docker build . -t registry.surfedu.nl/surfpol/harvester:latest
docker stack deploy  -c docker-compose.yml -c docker-compose.prd.yml --prune pol-harvester
