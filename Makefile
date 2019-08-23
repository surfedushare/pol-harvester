now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;
	find . -type d -name "__pycache__" -delete;

backup-db:
	docker exec -i $(shell docker ps -aqf label=nl.surfpol.db) pg_dump -h localhost -U postgres -c pol > data/pol.${now}.postgres.sql

export-swarm:
	docker exec -i $(shell docker ps -aqf label=nl.surfpol.db) pg_dumpall -h localhost -U postgres -c > data/pol.${now}.postgres-swarm.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker ps -aqf label=nl.surfpol.db) psql -h localhost -U postgres pol

start-postgres:
	psql -h localhost -U postgres -d postgres
