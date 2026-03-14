# Migration Celery → Django-Q2

_Date : 2026-03-14_

## Objectif

Remplacer Celery par Django-Q2 pour gérer les tâches d'ingestion (scoreboard, teams, backfill) avec :
- IHM dans l'admin Django (historique, scheduling, exécution manuelle)
- Pas de schedule hardcodé dans le code
- Singleton : pas de chevauchement d'une même tâche
- Rotation automatique des résultats à 90 jours

## Contexte

Celery est configuré dans le projet mais jamais utilisé en async (aucun `.delay()` / `.apply_async()`). Les endpoints et management commands appellent les services de manière synchrone. Celery Beat schedule 3 tâches en dur dans les settings. Il n'y a pas d'IHM ni d'historique.

## Design

### 1. Dépendances

- Supprimer `celery[redis]>=5.3,<6.0` de `pyproject.toml`
- Ajouter `django-q2[redis]`
- Ajouter `"django_q"` dans `INSTALLED_APPS`
- Lancer `python manage.py migrate` (crée les tables Q2 : `django_q_task`, `django_q_schedule`, etc.)

### 2. Configuration

Un seul dict `Q_CLUSTER` dans `config/settings/base.py` :

```python
Q_CLUSTER = {
    "name": "espn_service",
    "workers": 2,
    "timeout": 1800,          # 30 min
    "retry": 2400,            # retry check après 40 min
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
    "redis": env("REDIS_URL", default="redis://localhost:6379/0"),
    "max_attempts": 1,        # pas de retry auto, relance manuelle
    "ack_failures": True,
    "save_limit": 0,
}
```

Overrides par environnement :
- `test.py` : `Q_CLUSTER["sync"] = True`
- `production.py` : override `workers` et `redis` si besoin via env vars

### 3. Tâches

Les 4 tâches de `apps/ingest/tasks.py` deviennent des fonctions simples sans décorateurs Celery. Le logging structlog est conservé.

```python
"""Task functions for Django-Q2.

These functions are referenced by name in Django-Q2 schedules
and can be triggered manually via the admin.
"""
from datetime import datetime

import structlog

from apps.ingest.services import ScoreboardIngestionService, TeamIngestionService

logger = structlog.get_logger(__name__)

ALL_LEAGUES_CONFIG: list[tuple[str, str]] = [
    # ... (inchangé)
]


def refresh_scoreboard(sport: str, league: str, date: str | None = None) -> dict:
    """Refresh scoreboard data for a sport/league."""
    logger.info("starting_scoreboard_refresh", sport=sport, league=league, date=date)
    service = ScoreboardIngestionService()
    result = service.ingest_scoreboard(sport, league, date)
    logger.info("completed_scoreboard_refresh", sport=sport, league=league,
                created=result.created, updated=result.updated, errors=result.errors)
    return result.to_dict()


def refresh_teams(sport: str, league: str) -> dict:
    """Refresh team data for a sport/league."""
    logger.info("starting_teams_refresh", sport=sport, league=league)
    service = TeamIngestionService()
    result = service.ingest_teams(sport, league)
    logger.info("completed_teams_refresh", sport=sport, league=league,
                created=result.created, updated=result.updated, errors=result.errors)
    return result.to_dict()


def refresh_all_teams() -> dict:
    """Refresh team data for all configured leagues."""
    results = {}
    for sport, league in ALL_LEAGUES_CONFIG:
        try:
            service = TeamIngestionService()
            result = service.ingest_teams(sport, league)
            results[f"{sport}/{league}"] = result.to_dict()
        except Exception as e:
            logger.error("league_teams_refresh_failed", sport=sport, league=league, error=str(e))
            results[f"{sport}/{league}"] = {"error": str(e)}
    return results


def refresh_daily_scoreboards() -> dict:
    """Refresh today's scoreboards for all configured leagues."""
    today = datetime.now().strftime("%Y%m%d")
    results = {}
    for sport, league in ALL_LEAGUES_CONFIG:
        try:
            service = ScoreboardIngestionService()
            result = service.ingest_scoreboard(sport, league, today)
            results[f"{sport}/{league}"] = result.to_dict()
        except Exception as e:
            logger.error("league_scoreboard_refresh_failed", sport=sport, league=league,
                         date=today, error=str(e))
            results[f"{sport}/{league}"] = {"error": str(e)}
    return results
```

Appel depuis le code ou l'admin :
```python
from django_q.tasks import async_task
async_task("apps.ingest.tasks.refresh_scoreboard", "basketball", "nba")
```

### 4. Admin

Django-Q2 enregistre automatiquement ses modèles dans l'admin :
- **Successful tasks** : historique des réussites
- **Failed tasks** : historique des échecs avec traceback
- **Scheduled tasks** : création/édition de schedules (cron, intervalle, one-shot)
- **Queued tasks** : tâches en attente

#### Action "Exécuter maintenant"

Extension de l'admin `Schedule` pour ajouter une action qui enqueue immédiatement la tâche d'un schedule existant :

```python
from django.contrib import admin
from django_q.models import Schedule
from django_q.tasks import async_task


class ScheduleAdminMixin(admin.ModelAdmin):
    actions = ["run_now"]

    @admin.action(description="Exécuter maintenant")
    def run_now(self, request, queryset):
        for schedule in queryset:
            async_task(schedule.func, *schedule.args(), **schedule.kwargs())
            self.message_user(request, f"Tâche '{schedule.name}' enqueue.")


admin.site.unregister(Schedule)
admin.site.register(Schedule, ScheduleAdminMixin)
```

### 5. Singleton (pas de chevauchement)

Utilisation du mécanisme natif de Django-Q2 : quand un schedule a un run en cours, le scheduler ne lance pas de nouvelle instance. Le champ `task` du modèle `Schedule` track l'exécution en cours.

### 6. Rotation 90 jours

Tâche de purge schedulée via Q2 elle-même :

```python
# apps/ingest/tasks.py
from datetime import timedelta
from django.utils import timezone
from django_q.models import Success, Failure


def purge_old_results() -> dict:
    """Delete task results older than 90 days."""
    cutoff = timezone.now() - timedelta(days=90)
    s_count, _ = Success.objects.filter(stopped__lt=cutoff).delete()
    f_count, _ = Failure.objects.filter(stopped__lt=cutoff).delete()
    return {"purged_success": s_count, "purged_failure": f_count}
```

Schedule créé dans l'admin : `purge_old_results`, cron quotidien.

### 7. Nettoyage Celery

Fichiers et code à supprimer :

| Cible | Action |
|-------|--------|
| `config/celery.py` | Supprimer le fichier |
| `config/__init__.py` | Vider (supprimer l'import celery_app) |
| `config/settings/base.py` | Supprimer `CELERY_*` (lignes 182-205) |
| `config/settings/local.py` | Supprimer `CELERY_*` |
| `config/settings/production.py` | Supprimer `CELERY_*` |
| `config/settings/test.py` | Supprimer `CELERY_*` |
| `pyproject.toml` | Supprimer `celery[redis]` |
| `docker-compose.yml` (racine) | Remplacer `worker` + `beat` par `qcluster` |
| `espn_service/docker-compose.yml` | Remplacer `celery` + `celery-beat` par `qcluster` |
| `espn_service/docker-compose.prod.yml` | Remplacer `celery` + `celery-beat` par `qcluster` |
| `Makefile` | Remplacer targets `celery` + `beat` par `qcluster` |
| `.env.example` (racine) | Supprimer `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` |
| `espn_service/.env.example` | Supprimer `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` |
| `.github/workflows/ci.yml` | Supprimer `CELERY_BROKER_URL` |

### 8. Docker Compose

Le service `qcluster` remplace `worker` + `beat` :

```yaml
qcluster:
  build: .
  command: python manage.py qcluster
  depends_on:
    - db
    - redis
  env_file:
    - .env
```

Un seul process au lieu de deux.

### 9. Makefile

```makefile
qcluster:
	cd espn_service && venv/bin/python manage.py qcluster
```

Remplace les targets `celery` et `beat`.
