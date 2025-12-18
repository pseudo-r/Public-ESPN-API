# ESPN Service API

A production-ready Django REST API for ingesting and querying ESPN sports data.

## Features

- **Data Ingestion**: Fetch and persist data from ESPN's public/undocumented API endpoints
- **REST API**: Clean, paginated endpoints for querying teams, events, and games
- **Background Jobs**: Celery tasks for scheduled data refresh
- **Multi-Sport Support**: NBA, NFL, MLB, NHL, WNBA, and more
- **Production-Ready**: Docker, PostgreSQL, Redis, structured logging, health checks

## Quick Start

### Using Docker (Recommended)

```bash
cd espn_service
cp .env.example .env
docker compose up --build

# API: http://localhost:8000
# Docs: http://localhost:8000/api/docs/
```

### Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e ".[dev]"
pre-commit install
python manage.py migrate
python manage.py runserver
```

---

## Service API Endpoints

### Health Check

```bash
GET /healthz
```

### Data Ingestion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ingest/teams/` | POST | Ingest teams from ESPN |
| `/api/v1/ingest/scoreboard/` | POST | Ingest events/games |

**Request Body:**
```json
{
    "sport": "basketball",
    "league": "nba",
    "date": "20241215"  // Optional for scoreboard
}
```

### Query Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/teams/` | GET | List teams (with filters) |
| `/api/v1/teams/{id}/` | GET | Team details |
| `/api/v1/teams/espn/{espn_id}/` | GET | Team by ESPN ID |
| `/api/v1/events/` | GET | List events (with filters) |
| `/api/v1/events/{id}/` | GET | Event details |
| `/api/v1/events/espn/{espn_id}/` | GET | Event by ESPN ID |

**Filter Parameters:**
- `sport` - Filter by sport slug
- `league` - Filter by league slug
- `search` - Search teams by name
- `date` - Filter events by date (YYYY-MM-DD)
- `team` - Filter events by team abbreviation
- `status` - Filter events by status

---

## ESPN API Endpoints Reference

This service consumes ESPN's undocumented public APIs. Below is a reference of available endpoints.

### Base URLs

| Domain | Purpose |
|--------|---------|
| `site.api.espn.com` | Scores, news, teams, standings |
| `sports.core.api.espn.com` | Athletes, stats, odds |
| `cdn.espn.com` | CDN-optimized live data |

### Supported Sports & Leagues

| Sport | League | Sport Slug | League Slug |
|-------|--------|------------|-------------|
| Football | NFL | `football` | `nfl` |
| Football | College | `football` | `college-football` |
| Basketball | NBA | `basketball` | `nba` |
| Basketball | WNBA | `basketball` | `wnba` |
| Basketball | College Men's | `basketball` | `mens-college-basketball` |
| Baseball | MLB | `baseball` | `mlb` |
| Hockey | NHL | `hockey` | `nhl` |
| Soccer | Various | `soccer` | See below |
| MMA | UFC | `mma` | `ufc` |
| Golf | PGA | `golf` | `pga` |
| Racing | F1 | `racing` | `f1` |

### Soccer League Codes

| League | Code |
|--------|------|
| Premier League | `eng.1` |
| La Liga | `esp.1` |
| Bundesliga | `ger.1` |
| Serie A | `ita.1` |
| Ligue 1 | `fra.1` |
| MLS | `usa.1` |
| Champions League | `uefa.champions` |

### ESPN Endpoint Patterns

**Site API (General Data):**
```
https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/{resource}
```

| Resource | Path |
|----------|------|
| Scoreboard | `/scoreboard` |
| Teams | `/teams` |
| Team Detail | `/teams/{id}` |
| Standings | `/standings` |
| News | `/news` |
| Game Summary | `/summary?event={id}` |

**Core API (Detailed Data):**
```
https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/{resource}
```

| Resource | Path |
|----------|------|
| Athletes | `/athletes?limit=1000` |
| Seasons | `/seasons` |
| Events | `/events?dates=2024` |
| Odds | `/events/{id}/competitions/{id}/odds` |

### ESPN Client Configuration

```python
ESPN_CLIENT = {
    "SITE_API_BASE_URL": "https://site.api.espn.com",
    "CORE_API_BASE_URL": "https://sports.core.api.espn.com",
    "TIMEOUT": 30.0,
    "MAX_RETRIES": 3,
    "RETRY_BACKOFF": 1.0,
}
```

---

## Example Commands

### curl Examples

```bash
# Ingest NBA teams
curl -X POST http://localhost:8000/api/v1/ingest/teams/ \
  -H "Content-Type: application/json" \
  -d '{"sport": "basketball", "league": "nba"}'

# Ingest NFL scoreboard
curl -X POST http://localhost:8000/api/v1/ingest/scoreboard/ \
  -H "Content-Type: application/json" \
  -d '{"sport": "football", "league": "nfl"}'

# Query teams
curl "http://localhost:8000/api/v1/teams/?league=nba"
curl "http://localhost:8000/api/v1/teams/?search=Lakers"

# Query events
curl "http://localhost:8000/api/v1/events/?league=nba&date=2024-12-15"
curl "http://localhost:8000/api/v1/events/?team=LAL&status=final"

# Health check
curl http://localhost:8000/healthz
```

### Management Commands

```bash
python manage.py ingest_teams basketball nba
python manage.py ingest_scoreboard basketball nba --date=20241215
```

---

## Celery Background Jobs

```bash
# Start worker
celery -A config worker -l INFO

# Start scheduler
celery -A config beat -l INFO
```

### Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `refresh_scoreboard_task` | Hourly | Refresh NBA/NFL scoreboards |
| `refresh_all_teams_task` | Weekly | Refresh all team data |

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required in prod |
| `DEBUG` | Debug mode | `False` |
| `DATABASE_URL` | PostgreSQL URL | sqlite for local |
| `CELERY_BROKER_URL` | Redis URL | `redis://localhost:6379/0` |
| `ESPN_TIMEOUT` | API timeout (sec) | `30.0` |
| `ESPN_MAX_RETRIES` | Max retries | `3` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |

---

## Project Structure

```
espn_service/
├── config/                # Django configuration
│   ├── settings/
│   │   ├── base.py       # Base settings
│   │   ├── local.py      # Local development
│   │   ├── production.py # Production
│   │   └── test.py       # Test settings
│   ├── celery.py         # Celery config
│   └── urls.py           # URL routing
├── apps/
│   ├── core/             # Core utilities
│   ├── espn/             # ESPN data models & API
│   └── ingest/           # Data ingestion
├── clients/
│   └── espn_client.py    # ESPN API client
├── tests/                # Test suite
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Database Models

| Model | Description |
|-------|-------------|
| `Sport` | Sport types (basketball, football) |
| `League` | Leagues within sports (NBA, NFL) |
| `Team` | Team info with logos, colors |
| `Venue` | Stadium/arena information |
| `Event` | Games with status, scores |
| `Competitor` | Team participation in events |
| `Athlete` | Player information |

---

## Testing

```bash
# All tests with coverage
make test

# Quick tests
make test-fast

# Specific file
pytest tests/test_api.py -v
```

---

## Production Deployment

### Docker Production

```bash
docker compose -f docker-compose.prod.yml up -d
```

### Cloud Platforms

**AWS ECS/Fargate:**
```bash
docker build -t espn-service:latest .
docker push <account>.dkr.ecr.<region>.amazonaws.com/espn-service:latest
```

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/espn-service
gcloud run deploy espn-service --image gcr.io/PROJECT_ID/espn-service
```

**Fly.io:**
```bash
fly launch
fly secrets set SECRET_KEY=your-key DATABASE_URL=your-url
fly deploy
```

---

## API Documentation

Once running:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## License

MIT License - See LICENSE file
