# Schema — ESPN API Service

> Dernière mise à jour : 2026-03-12

---

## Couche 1 — Référentiel

### Sport
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| slug | CharField(50) | unique, indexed |
| name | CharField(100) | |
| created_at | DateTimeField | auto |
| updated_at | DateTimeField | auto |

---

### League
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| sport | FK → Sport | CASCADE |
| slug | CharField(50) | indexed |
| name | CharField(100) | |
| abbreviation | CharField(20) | blank |
| created_at | DateTimeField | auto |
| updated_at | DateTimeField | auto |
| unique_together | (sport, slug) | |

---

### Venue
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| espn_id | CharField(50) | unique, indexed |
| name | CharField(200) | |
| city | CharField(100) | blank |
| state | CharField(100) | blank |
| country | CharField(100) | blank, default="USA" |
| is_indoor | BooleanField | default=True |
| capacity | PositiveIntegerField | nullable |
| raw_data | JSONField | default={} |
| created_at | DateTimeField | auto |
| updated_at | DateTimeField | auto |

---

### Team
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| league | FK → League | CASCADE |
| espn_id | CharField(50) | indexed |
| uid | CharField(100) | blank |
| slug | CharField(100) | blank |
| abbreviation | CharField(10) | |
| display_name | CharField(100) | |
| short_display_name | CharField(50) | blank |
| name | CharField(50) | blank |
| nickname | CharField(50) | blank |
| location | CharField(100) | blank |
| color | CharField(10) | blank |
| alternate_color | CharField(10) | blank |
| is_active | BooleanField | default=True |
| is_all_star | BooleanField | default=False |
| logos | JSONField | default=[] |
| links | JSONField | default=[] |
| raw_data | JSONField | default={} |
| created_at | DateTimeField | auto |
| updated_at | DateTimeField | auto |
| unique_together | (league, espn_id) | |

---

## Couche 2 — Événements

### Event
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| league | FK → League | CASCADE |
| venue | FK → Venue | SET_NULL, nullable |
| espn_id | CharField(50) | indexed |
| uid | CharField(100) | blank |
| date | DateTimeField | |
| name | CharField(200) | |
| short_name | CharField(100) | blank |
| season_year | PositiveIntegerField | |
| season_type | PositiveSmallIntegerField | default=2 (1=pre, 2=regular, 3=post) |
| season_slug | CharField(50) | blank |
| week | PositiveSmallIntegerField | nullable |
| status | CharField(20) | choices: scheduled/in_progress/final/postponed/cancelled |
| status_detail | CharField(100) | blank |
| clock | CharField(20) | blank |
| period | PositiveSmallIntegerField | nullable |
| attendance | PositiveIntegerField | nullable |
| broadcasts | JSONField | default=[] |
| links | JSONField | default=[] |
| raw_data | JSONField | default={} |
| created_at | DateTimeField | auto |
| updated_at | DateTimeField | auto |
| unique_together | (league, espn_id) | |

> Home/away, scores et stats sont portés par Competitor, pas dupliqués ici.

---

### Competitor
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| event | FK → Event | CASCADE |
| team | FK → Team | CASCADE |
| home_away | CharField(4) | choices: home/away |
| score | CharField(10) | blank |
| winner | BooleanField | nullable |
| line_scores | JSONField | default=[] |
| records | JSONField | default=[] |
| statistics | JSONField | default=[] |
| leaders | JSONField | default=[] |
| order | PositiveSmallIntegerField | default=0 |
| raw_data | JSONField | default={} |
| created_at | DateTimeField | auto |
| updated_at | DateTimeField | auto |
| unique_together | (event, team) | |

---

### Odds
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| event | FK → Event | CASCADE |
| provider | CharField(50) | default="bet365" |
| odds_home | DecimalField(8,4) | nullable |
| odds_draw | DecimalField(8,4) | nullable |
| odds_away | DecimalField(8,4) | nullable |
| odds_over | DecimalField(8,4) | nullable |
| odds_under | DecimalField(8,4) | nullable |
| over_under_line | DecimalField(4,2) | nullable — ligne O/U (ex: 2.5, 3.25) |
| raw_data | JSONField | default={} |
| fetched_at | DateTimeField | auto |
| unique_together | (event, provider) | |

---

## Couche 3 — ML

### EventFeatures
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| event | OneToOneField → Event | CASCADE |
| computed_at | DateTimeField | auto |
| **Elo** | | |
| home_elo | DecimalField(8,2) | nullable |
| away_elo | DecimalField(8,2) | nullable |
| elo_diff | DecimalField(8,2) | nullable |
| **Forme (5 derniers matchs)** | | |
| home_form_5 | DecimalField(5,2) | nullable — pts/match |
| away_form_5 | DecimalField(5,2) | nullable |
| **Buts moyens (5 derniers matchs)** | | |
| home_avg_goals_scored_5 | DecimalField(5,2) | nullable |
| home_avg_goals_conceded_5 | DecimalField(5,2) | nullable |
| away_avg_goals_scored_5 | DecimalField(5,2) | nullable |
| away_avg_goals_conceded_5 | DecimalField(5,2) | nullable |
| **H2H (5 dernières confrontations)** | | |
| h2h_home_wins | PositiveSmallIntegerField | nullable |
| h2h_draws | PositiveSmallIntegerField | nullable |
| h2h_away_wins | PositiveSmallIntegerField | nullable |
| **Contexte** | | |
| home_days_rest | PositiveSmallIntegerField | nullable |
| away_days_rest | PositiveSmallIntegerField | nullable |

---

### Prediction
| Champ | Type | Contraintes |
|-------|------|-------------|
| id | BigAutoField | PK |
| event | FK → Event | CASCADE |
| model_version | CharField(20) | |
| predicted_at | DateTimeField | auto |
| **Probabilités** | | |
| prob_home | DecimalField(5,4) | nullable |
| prob_draw | DecimalField(5,4) | nullable |
| prob_away | DecimalField(5,4) | nullable |
| prob_over25 | DecimalField(5,4) | nullable |
| prob_btts | DecimalField(5,4) | nullable |
| **Expected Value** | | |
| ev_home | DecimalField(8,4) | nullable |
| ev_draw | DecimalField(8,4) | nullable |
| ev_away | DecimalField(8,4) | nullable |
| ev_over25 | DecimalField(8,4) | nullable |
| **Tip** | | |
| tip | CharField(10) | choices: HOME/DRAW/AWAY/OVER25/BTTS, nullable |
| tip_confidence | CharField(10) | choices: HIGH/MEDIUM/LOW, nullable |
| unique_together | (event, model_version) | |

---

## Vue d'ensemble

```
Sport
 └── League
      ├── Team
      └── Event ──── league ──→ League
               ├──── venue ───→ Venue
               ├──── Competitor (×2) ──→ Team
               ├──── Odds (×n providers)
               ├──── EventFeatures (×1)
               └──── Prediction (×n versions)
```

---

## V2 — Extensions prévues

> Non implémentées pour l'instant. Modèle Athlete déjà présent dans le fork, mis de côté pour la v1.

### Athlete
- Profil joueur complet (nom, position, taille, poids, date de naissance)
- FK → Team (nullable)
- Déjà dans le fork avec champs ESPN (espn_id, headshot, jersey, etc.)

### MatchLineup / LineupPlayer
- Composition des équipes par event
- Titulaires, remplaçants, formation

### AthleteSeasonStats
- Stats agrégées par joueur, saison, league
