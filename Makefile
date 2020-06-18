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
	docker exec -it $(shell docker ps -qf label=nl.surfpol.tasks | head -n1) /usr/src/app/entrypoint.sh bash

run-harvest:
	docker exec -i $(shell docker ps -qf label=nl.surfpol.tasks | head -n1) /usr/src/app/entrypoint.sh python manage.py run_harvest --no-progress

start-postgres:
	psql -h localhost -U postgres -d postgres

run-seeds-harvest:
	cd harvester && python -u manage.py harvest_edurep_seeds -f delta -d | tee ../test.log

backup-seeds:
	cd harvester && python -u manage.py dump_resource edurep.EdurepOAIPMH

backup-indices:
	cd elastic/repositories
	docker cp $(shell docker ps -qf label=nl.surfpol.elastic):/usr/share/elasticsearch/repositories/backups backups
	zip -r data/pol.${now}.elastic.zip backups

dump-resources:
	docker exec -i $(shell docker ps -qf label=nl.surfpol.tasks | head -n1) /usr/src/app/entrypoint.sh python manage.py dump_harvester_data delta
	sed -i 's/"freeze"/"dataset"/g' ${HARVESTER_DATA_DIR}/pol_harvester/dumps/freeze/*
	sed -i 's/pol_harvester.freeze/core.dataset/g' ${HARVESTER_DATA_DIR}/pol_harvester/dumps/freeze/*
	sed -i 's/pol_harvester.collection/core.collection/g' ${HARVESTER_DATA_DIR}/pol_harvester/dumps/freeze/*
	sed -i 's/pol_harvester.arrangement/core.arrangement/g' ${HARVESTER_DATA_DIR}/pol_harvester/dumps/freeze/*
	sed -i 's/pol_harvester.document/core.document/g' ${HARVESTER_DATA_DIR}/pol_harvester/dumps/freeze/*
	aws s3 cp ${HARVESTER_DATA_DIR}/pol_harvester/dumps/freeze/* s3://edushare-data/datasets/harvester/core/dumps/dataset/
	aws s3 cp ${HARVESTER_DATA_DIR}/edurep/dumps/edurepoaipmh/* s3://edushare-data/datasets/harvester/edurep/dumps/edurepoaipmh/

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
