# Data Foundation — Design Spec

> Date : 2026-03-12

## Objectif

Ajouter l'ingestion des odds Bet365 et le backfill historique au projet ESPN API existant. C'est la fondation data nécessaire avant le pipeline ML (Plan 2).

## Contexte

Le fork fournit déjà :
- Modèles : Sport, League, Venue, Team, Event, Competitor, Athlete
- Client ESPN avec retry/backoff exponentiel (`espn_service/clients/espn_client.py`)
- `TeamIngestionService` + `ScoreboardIngestionService` (`espn_service/apps/ingest/services.py`)
- Commandes : `ingest_teams`, `ingest_scoreboard`
- Celery tasks pour refresh automatique
- 74 tests

L'infra dev : code sur Mac, PostgreSQL + Redis sur Fedora (192.168.1.153) via Docker.

---

## 1. Modèle Odds

Nouveau modèle dans `espn_service/apps/espn/models.py` :

```python
class Odds(TimestampMixin):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="odds")
    provider = models.CharField(max_length=50, default="bet365")
    odds_home = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    odds_draw = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    odds_away = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    odds_over = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    odds_under = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    over_under_line = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["event", "provider"]]
```

Migration Django standard (`makemigrations` + `migrate`).

---

## 2. Source des odds — Bet365 (provider 2000)

### Endpoint ESPN

```
GET /v2/sports/soccer/leagues/{league}/events/{event_id}/competitions/{event_id}/odds/2000
```

### Extraction des cotes

Les cotes pre-match sont dans `bettingOdds.teamOdds` en format fractionnaire UK :

| Clé ESPN | Exemple | Conversion | Champ Odds |
|----------|---------|------------|------------|
| `preMatchFullTimeResultHome.value` | `"27/100"` | `27/100 + 1 = 1.27` | `odds_home` |
| `preMatchFullTimeResultDraw.value` | `"19/4"` | `19/4 + 1 = 5.75` | `odds_draw` |
| `preMatchFullTimeResultAway.value` | `"9/1"` | `9/1 + 1 = 10.0` | `odds_away` |
| `preMatchGoalLineOver.value` | `"7/8"` | `7/8 + 1 = 1.875` | `odds_over` |
| `preMatchGoalLineUnder.value` | `"39/40"` | `39/40 + 1 = 1.975` | `odds_under` |
| `preMatchOverUnderHandicap.value` | `"3.25"` | tel quel | `over_under_line` |

### Helper de conversion

```python
def fraction_to_decimal(fraction_str: str) -> Decimal:
    """Convertit une cote fractionnaire UK en décimale. '7/8' → 1.875"""
    num, den = fraction_str.split("/")
    return Decimal(num) / Decimal(den) + 1
```

### Cas particuliers

- `bettingOdds.teamOdds` absent → pas de cotes Bet365 pour cet event, on skip
- `value` absent sur une cote → on stocke `None` pour ce champ
- `homeTeamOdds.odds.summary == "OFF"` → cotes retirées (match en cours ou terminé récemment), les cotes pre-match dans `bettingOdds` restent exploitables

---

## 3. Enrichissement de l'ingestion

### Nouveau : `get_event_odds` sur le client ESPN

Ajouter une méthode au client :

```python
def get_event_odds(self, sport: str, league: str, event_id: str, provider: int = 2000) -> ESPNResponse:
    """Fetch odds d'un provider pour un event."""
    path = f"/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{event_id}/odds/{provider}"
    return self.get(path, domain=ESPNEndpointDomain.CORE)
```

### Enrichissement de `ScoreboardIngestionService`

Après la création/mise à jour des events et competitors, pour chaque event :
1. Appel `get_event_odds(sport, league, event.espn_id)`
2. Parse `bettingOdds.teamOdds`
3. Conversion fractionnaire → décimal
4. `Odds.objects.update_or_create(event=event, provider="bet365", defaults={...})`

Le tout dans la même transaction atomique.

---

## 4. Backfill historique

### Commande

```bash
python manage.py backfill --sport soccer --league fra.1 --season 2024
```

### Flow

1. **Lister les events** via core API : `GET /v2/sports/soccer/leagues/{league}/events?dates={year}` → paginé, retourne des `$ref` URLs
2. **Pour chaque page** : extraire les event IDs depuis les `$ref`
3. **Pour chaque event** :
   a. Fetch scoreboard summary (`get_event`) → créer/update Event + Competitors
   b. Fetch odds Bet365 (`get_event_odds`) → créer/update Odds
4. Afficher la progression : `[142/380] Event 746630 — Metz at Lens ✓`

### Méthode client existante à réutiliser

```python
# Lister les events d'une saison (déjà disponible via get())
client.get(f"/v2/sports/{sport}/leagues/{league}/events", domain=CORE, params={"dates": str(year), "limit": 100, "page": page})
```

### Rate limiting

**Critique** — le backfill fait ~3 appels par match (listing + summary + odds). Une saison = ~380 matchs = ~1140 appels.

Mesures :
- **Délai entre requêtes** : `time.sleep(delay)` configurable, défaut 0.5s entre chaque appel
- **Paramètre `--delay`** : `manage.py backfill --delay 1.0` pour augmenter si rate limité
- **Retry existant** : le client a déjà le retry avec backoff exponentiel (`ESPNRateLimitError` sur 429)
- **Reprise sur erreur** : les events déjà ingérés sont skippés grâce à `update_or_create`. Si le backfill plante à mi-chemin, on le relance et il reprend là où il en était.
- **Log structuré** : chaque event logué avec son statut (created/updated/skipped/error)

---

## 5. Admin Django

Enregistrer `Odds` dans l'admin :

```python
@admin.register(Odds)
class OddsAdmin(admin.ModelAdmin):
    list_display = ["event", "provider", "odds_home", "odds_draw", "odds_away", "over_under_line", "fetched_at"]
    list_filter = ["provider"]
    search_fields = ["event__name"]
```

---

## 6. Tests

### Tests modèle Odds
- Création, contrainte unique (event + provider), `__str__`

### Tests helper `fraction_to_decimal`
- Cas standard : `"7/8"` → `1.875`
- Cas entier : `"9/1"` → `10.0`
- Cas petit : `"27/100"` → `1.27`

### Tests parsing odds Bet365
- Response complète → extraction correcte des 6 champs
- `bettingOdds.teamOdds` absent → skip sans erreur
- Valeur manquante sur un marché → `None`

### Tests ingestion odds (dans ScoreboardIngestionService)
- Scoreboard + odds créés en une passe
- Update idempotent (re-run ne duplique pas)

### Tests backfill
- Pagination des events
- Création event + competitor + odds
- Reprise après erreur (events existants skippés)
- Mocks ESPN API

---

## 7. Ce qui est hors scope

- **EventFeatures** / **Prediction** → Plan 2 (ML)
- **Athlete** / **MatchLineup** / **LineupPlayer** → V2
- **Celery task pour le backfill** → pas nécessaire, c'est une commande one-shot
- **Autres providers** (DraftKings) → Bet365 suffit
- **API DRF** pour les odds → Plan 2

---

## Fichiers impactés

| Fichier | Action |
|---------|--------|
| `apps/espn/models.py` | Ajouter `Odds` |
| `apps/espn/admin.py` | Enregistrer `OddsAdmin` |
| `apps/espn/migrations/0002_odds.py` | Générée par `makemigrations` |
| `clients/espn_client.py` | Ajouter `get_event_odds()` |
| `apps/ingest/services.py` | Enrichir scoreboard + helper `fraction_to_decimal` |
| `apps/ingest/management/commands/backfill.py` | Nouveau |
| `tests/test_models.py` | Tests Odds |
| `tests/test_ingestion.py` | Tests parsing odds + backfill |
| `tests/test_espn_client.py` | Test `get_event_odds()` |
| `docs/schema.md` | Déjà à jour |
