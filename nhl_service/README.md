# NHL service

Django REST service backed by the NHL Web and Stats APIs. This service has its
own Django project and must be run separately from `espn_service`.

From this directory, install with `python -m pip install -e ".[dev]"` and run
`python -m pytest tests/ --no-cov`. Tests use isolated test settings; the suite covers HTTP routing, cleanup, ingestion rollback, standings, and read-only API behavior.

The development Compose file requires a local `.env` and exposes port 8001.
Run `docker compose up --build`, then apply migrations with
`docker compose exec web python manage.py migrate`.

Read-only endpoints under `/api/v1/`:

- `teams/`
- `players/`
- `games/`
- `standings/`
- `skater-stats/`
- `goalie-stats/`

OpenAPI schema: `/api/schema/`; interactive documentation: `/api/docs/`.
Records are populated by tasks in `apps/ingest/tasks.py`.

Production settings (`config.settings.production`) require explicit
`DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS`. Configure the database and Redis
for your environment. The development Compose configuration and Django
development server are not a production deployment.
