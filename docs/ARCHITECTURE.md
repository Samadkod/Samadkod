# 🏗️ Architecture — Sentinel QDD-S2 V1

## Vue d'ensemble

**Sentinel QDD-S2** est un framework industrialisé de Qualité des Données (QDD) pour Solvabilité 2, construit en 6 couches:

```
┌─────────────────────────────────────────────────────────┐
│  6. Couche IA (V5+)                                      │
│     Agent en lecture seule diagnostiquant anomalies     │
├─────────────────────────────────────────────────────────┤
│  5. Gouvernance (Auto-générée)                           │
│     - Dictionnaire de données                           │
│     - Lignage et cartographie                           │
│     - Fiches de contrôle                                │
│     - Dossier de preuve d'audit (PDF/Markdown)          │
├─────────────────────────────────────────────────────────┤
│  4. Restitution (Streamlit)                              │
│     - Dashboard QDD (scorecard par dimension)           │
│     - Détail anomalies avec causes                      │
│     - Piste d'audit pour ACPR                           │
├─────────────────────────────────────────────────────────┤
│  3. Résultats (Historisés en CSV)                        │
│     - control_runs: exécutions                          │
│     - anomalies: liste complète avec statut             │
├─────────────────────────────────────────────────────────┤
│  2. Moteur (DuckDB Python + SAS Macros)                  │
│     - Générique, paramétré par métadonnées              │
│     - Exécute tous les contrôles du registre            │
│     - Double moteur (SAS + Python/DuckDB)              │
├─────────────────────────────────────────────────────────┤
│  1. Registre des Contrôles (Métadonnées CSV)            │
│     - Définition centralisée                            │
│     - Ajouter contrôle = 1 ligne au CSV                │
└─────────────────────────────────────────────────────────┘
```

---

## Structure du repo

```
sentinel-qdd-s2/
├── data/                          # Données fictives + générateur
│   ├── generator.py              # Générateur BTP reproductible
│   └── *.csv                     # Données générées
│
├── metadata/                      # Métadonnées (CSV)
│   ├── control_registry.csv       # 15 contrôles à exécuter
│   ├── data_dictionary.csv        # Dictionnaire de données
│   ├── lineage_edges.csv          # Lignage flux source → cible
│   ├── control_runs.csv           # Historique d'exécution (vide)
│   ├── anomalies.csv              # Anomalies détectées (vide)
│   └── pannes_catalogue.csv       # 10 pannes de test
│
├── engine/                        # Moteur générique
│   ├── metadata_loader.py         # Charge les CSV
│   ├── control_engine.py          # Moteur principal
│   ├── generic_controls.py        # 8 types de contrôles
│   └── __init__.py
│
├── sas/                          # Code SAS
│   ├── qdd_macros.sas            # Macros %qdd_* (parité moteur)
│   └── qdd_main.sas              # Programme principal
│
├── tests/                         # Tests pytest
│   ├── test_control_engine.py    # Tests moteur
│   ├── test_data_generator.py    # Tests données
│   └── conftest.py               # Fixtures
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md            # Ce fichier
│   ├── COMMENT_AJOUTER_CONTROLE.md
│   └── GLOSSAIRE.md
│
├── app.py                         # App Streamlit (refondue)
├── requirements.txt               # Dépendances
├── CHANGELOG.md                   # Historique
├── CLAUDE.md                      # Spec du projet (pour CI/CD)
└── README.md                      # Guide utilisateur
```

---

## 1. Registre des Contrôles (Métadonnées)

**Fichier:** `metadata/control_registry.csv`

### Colonnes

| Colonne | Type | Description |
|---------|------|------------|
| **ctrl_id** | STRING | Identifiant unique (ex: `EXHAUS_01`) |
| **libelle** | STRING | Description lisible (ex: `Champs obligatoires non nuls`) |
| **table_cible** | STRING | Table à contrôler (ex: `contrats`) |
| **champ** | STRING | Champ(s) à tester (ex: `police,assure,prime_emise`) |
| **type_controle** | STRING | Type générique (ex: `NON_NUL`) |
| **parametres** | JSON | Config (ex: `{"champs": ["police"]}`) |
| **critere_art82** | STRING | Critère Solvabilité 2 (ex: `Complétude`) |
| **criticite** | STRING | `Bloquant`, `Majeur`, `Mineur` |
| **domaine** | STRING | Domaine métier (ex: `Exhaustivité`) |
| **proprietaire** | STRING | Équipe responsable |
| **seuil_tolerance** | FLOAT | Tolérance (%) |
| **actif** | INT | 1 = exécuter, 0 = ignorer |

### Ajouter un contrôle

**Étape 1:** Ajouter 1 ligne au CSV

```csv
NOUVEAU_01,Nouvelle vérification,ma_table,mon_champ,NON_NUL,"{…}",Completude,Majeur,Domaine,QDD,0,1
```

**Étape 2:** Le moteur exécute automatiquement au prochain run.

**Pas besoin de coder!**

---

## 2. Moteur Générique

### Architecture

**`engine/control_engine.py`** — Classe `ControlEngine`

```python
engine = ControlEngine(metadata_dir="metadata")
runs_df, anomalies_df = engine.run(datasets, date_arrete="2024-12-31")
```

**Flux:**
1. Charge `control_registry.csv`
2. Pour chaque contrôle actif:
   - Récupère la table cible
   - Exécute le type de contrôle approprié
   - Enregistre le run (OK/KO)
   - Enregistre les anomalies détectées
3. Retourne DataFrames structurés

### 8 Types de Contrôles Génériques

| Type | Exemple | Détecte |
|------|---------|---------|
| **NON_NUL** | Champ NULL | Valeurs manquantes |
| **UNIQUE** | Doublon police | Clés non uniques |
| **PLAGE** | Montant < 0 ou > 999999 | Valeurs hors limites |
| **REFERENTIEL** | Branche ∉ {RC_PRO, DO, …} | Valeurs hors domaine |
| **FORMAT** | Taux non numérique | Erreurs de type |
| **COHERENCE_DATES** | date_declaration < date_survenance | Incohérences temporelles |
| **RECONCILIATION** | &#124;source - cible&#124; / moyenne > 5% | Écarts d'agrégation |
| **VARIATION_N_N1** | Volume ↓ 10% entre N-1 et N | Anomalies volumétriques |

### Ajouter un type de contrôle

**Étape 1:** Implémenter dans `engine/generic_controls.py`

```python
def _mon_type_controle(self, df, row, datasets):
    # Retourner pd.Series booléenne (True = anomalie)
    pass
```

**Étape 2:** Ajouter à `type_map` dans `execute()`

```python
"MON_TYPE": self._mon_type_controle,
```

**Étape 3:** Utiliser dans le registre

---

## 3. Résultats Structurés

### Fichiers générés après chaque run

**`control_runs.csv`** — Résumé de chaque exécution

| Colonne | Exemple |
|---------|---------|
| run_id | `run_a1b2c3d4` |
| ctrl_id | `EXHAUS_01` |
| date_arrete | `2024-12-31` |
| statut | `OK` ou `KO` |
| nb_lignes_controlees | `2500` |
| nb_anomalies | `47` |

**`anomalies.csv`** — Détail de chaque anomalie

| Colonne | Exemple |
|---------|---------|
| anomaly_id | `anom_xyz789` |
| run_id | `run_a1b2c3d4` |
| cle_metier | `P001` |
| champ | `assure` |
| valeur_constatee | `NULL` |
| statut | `OUVERT` |
| famille_cause | `NON_NUL` |

---

## 4. Restitution Streamlit

### Onglets de l'app V1

| Onglet | Fonction |
|--------|----------|
| 📊 **Synthèse** | Scorecard QDD (% conformité par dimension) |
| 💰 **Solvabilité 2** | Impact provisioning, SCR/MCR |
| ✅ **Contrôles** | Registre détaillé + statuts |
| 🔎 **Anomalies** | Liste complète avec filtres |
| 📖 **Dictionnaire** | Définition de tous les champs |
| 🗺️ **Lignage** | Cartographie flux source → cible |
| 🧾 **Piste d'audit** | Export pour ACPR/commissaires |

### Dépendances

- **streamlit==1.41.1** — Framework UI
- **pandas** — Data manipulation
- **plotly** — Visualisations
- **duckdb** — Moteur SQL (optionnel pour perfs)

---

## 5. Double Moteur (SAS + Python/DuckDB)

### Parité garantie

Les deux implémentations produisent les **mêmes résultats** sur les mêmes données:

**Python/DuckDB** (`engine/control_engine.py`)
- Exécution: Streamlit Cloud
- Dépendances: pandas, duckdb
- Avantage: Portable, pas de SAS requis

**SAS** (`sas/qdd_macros.sas`)
- Exécution: SAS OnDemand for Academics
- Dépendances: Base SAS + SQL
- Avantage: Production-ready

### Tester la parité

```bash
# 1. Run Python
pytest tests/test_control_engine.py -v

# 2. Run SAS
sas qdd_main.sas

# 3. Comparer anomalies.csv des deux exécutions
diff -u python_anomalies.csv sas_anomalies.csv
```

---

## 6. Pipeline de données (Données fictives BTP)

**Reproductibilité:** Seed fixe → mêmes données à chaque exécution

### Tables générées

| Table | Lignes | Contenu |
|-------|--------|---------|
| **contrats** | 2000 | Polices, primes, branches BTP |
| **sinistres** | 900 | Déclarations, dates, montants |
| **primes** | ~2000 | Émis/acquis par exercice |
| **provisions** | ~900 | Réserves par arrêté |

### 10 Pannes injectables

```csv
panne_id,libelle,criticite
1,Date survenance manquante,Bloquant
2,Doublon de police,Bloquant
3,Montant provision négative,Bloquant
...
```

Chaque panne est détectable par au moins 1 contrôle.

---

## 7. Roadmap V2-V6

| Version | Livrables | Efforts |
|---------|-----------|---------|
| **V1** (Current) | 15 contrôles, moteur générique, 10 pannes, tests | 13h |
| **V2** | Contrôles métier réalistes (sinistres rouverts, réassurance) | 2 semaines |
| **V3** | Lignage automatique (parser SAS/SQL) | 1 semaine |
| **V4** | Jeu d'évaluation 20 pannes + fiabilité détection | 1 semaine |
| **V5** | Agent IA diagnostiquant anomalies | 2 semaines |
| **V6** | API, journalisation audit complète, dossier de preuve enrichi | 1 semaine |

---

## 8. Déploiement

### Local

```bash
# Installer
pip install -r requirements.txt

# Tests
pytest tests/ -v

# App
streamlit run app.py
```

### Streamlit Cloud

```bash
git push origin v1
# GitHub → Streamlit Cloud → Auto-déploie depuis main
```

---

## Contacts & Support

- **Auteur:** Samadou Kodon
- **Mentorship:** Claude Code (Claude Haiku 4.5)
- **Documentation:** `/docs/`
- **Tests:** `/tests/`

---

**Last updated:** 2026-09-21  
**Version:** 1.0  
**Status:** STABLE
