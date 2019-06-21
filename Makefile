now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;
	find . -type d -name "__pycache__" -delete;

backup-db:
	sudo docker-compose exec postgres pg_dumpall -h localhost -U postgres -c > data/pol.${now}.postgres.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker-compose ps -q postgres) psql -h localhost -U postgres

start-postgres:
	psql -h localhost -U postgres -d postgres
