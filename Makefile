now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;
	find . -type d -name "__pycache__" -delete;

backup-db:
	pg_dumpall -h localhost -U postgres > data/pol.${now}.postgres.sql

import-db:
	psql -h localhost -U postgres < $(backup)

start-postgres:
	psql -h localhost -U postgres -d postgres
