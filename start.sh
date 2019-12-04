#!/usr/bin/env bash


# This script starts a Docker Swarm that is needed to run the project.
# It makes available an API on localhost:8000, which nginx can expose.
# You can run harvest commands through the tasks server. For example:
#     docker exec -it $(docker ps -qf label=nl.surfpol.tasks) ./entrypoint.sh ./manage.py freeze_edurep -f <freeze-name>


# Set the environment variables and activates the Conda environment
source activate.sh


# Storing the git commit hash that belongs to this start
# This hash will be included in command output to be able to replicate results
export DJANGO_GIT_COMMIT=$(git rev-parse HEAD)
echo $DJANGO_GIT_COMMIT > harvester/.commit


# Clearing static files in order to collect them again
[[ -f "harvester/statics" ]] && rm -r harvester/statics


# Deploying containers to the stack

docker build . -t registry.surfedu.nl/edu/pol-harvester:$DJANGO_GIT_COMMIT
docker push registry.surfedu.nl/edu/pol-harvester:$DJANGO_GIT_COMMIT
docker-compose -f docker-compose.yml -f docker-compose.prd.yml --log-level ERROR config | docker stack deploy  -c - --prune pol-harvester
