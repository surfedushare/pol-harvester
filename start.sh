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
# And it determines if the frontend needs a (re)build
export DJANGO_GIT_COMMIT=$(git rev-parse HEAD)
if [[ ! -e harvester/search/static/.commit || $(< harvester/search/static/.commit) != "$DJANGO_GIT_COMMIT" ]]; then
    cd rateapp;
    npm run build;
    cd -;
    echo $DJANGO_GIT_COMMIT > harvester/search/static/.commit;
    echo "Build rate app inside of search application";
    rm -r harvester/statics  # this forces static file collection at container start to get frontend into Django
fi
echo $DJANGO_GIT_COMMIT > harvester/.commit


# (Re-)building the containers and (re)starting them
docker-compose build
docker-compose down
docker-compose up -d -f docker-compose.yml -f docker-compose.prd.yml
