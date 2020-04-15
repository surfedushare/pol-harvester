now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;
	find . -type d -name "__pycache__" -delete;

backup-db:
	docker exec -i $(shell docker ps -qf label=nl.surfpol.db) pg_dump -h localhost -U postgres -c pol > data/pol.${now}.postgres.sql

export-swarm:
	docker exec -i $(shell docker ps -qf label=nl.surfpol.db) pg_dumpall -h localhost -U postgres -c > data/pol.${now}.postgres-swarm.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker ps -qf label=nl.surfpol.db) psql -h localhost -U postgres pol

run-bash:
	docker exec -it $(shell docker ps -qf label=nl.surfpol.harvester | head -n1) /usr/src/app/entrypoint.sh bash

run-harvest:
	docker exec -i $(shell docker ps -qf label=nl.surfpol.harvester | head -n1) /usr/src/app/entrypoint.sh python manage.py run_harvest

start-postgres:
	psql -h localhost -U postgres -d postgres

run-seeds-harvest:
	cd harvester && python -u manage.py harvest_edurep_seeds -f delta -d | tee ../test.log

backup-seeds:
	cd harvester && python -u manage.py dump_resource edurep.EdurepOAIPMH

pull-production-media:
	# Syncing production media to local media folder
	# -z means use compression
	# -r means recursive
	# -t means preserve creation and modification times
	# -h means human readable output
	# -v means verbose
	rsync -zrthv --progress search-prod.surfcatalog.nl:/opt/media/media .

push-test-media:
	# Syncing production media to local media folder
	# -z means use compression
	# -r means recursive
	# -t means preserve creation and modification times
	# -h means human readable output
	# -v means verbose
	rsync -zrthv --progress media search-test.surfcatalog.nl:/opt/media/
