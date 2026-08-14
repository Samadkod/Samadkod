# Architecture - Système d'Agrégation d'Erreurs de Migration

## 🎯 Objectif

Centraliser et tracker les erreurs de validation de migration (SSM) par semaine avec un focus sur les erreurs **bloquantes uniquement**.

## 📊 Flux de données

```
┌─────────────────────────────────────────────────────────────┐
│ Self-Service Migration (SSM) Tool                           │
│ Export CSV: erreursvalidationEST_1.txt (hebdomadaire)       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Python Script: aggregate_errors.py                          │
│ • Parse TSV/CSV (support multi-encoding)                    │
│ • Filter: Criticite = "Error" seulement                     │
│ • Agrège par: Scope + ErrorID + Message                     │
│ • Détecte sites résolus (disparus entre semaines)           │
└─────────────────┬───────────────────────────────────────────┘
                  │
          ┌───────┴────────┐
          │                │
          ▼                ▼
    ┌──────────────┐  ┌─────────────────────┐
    │ JSON History │  │ CSV (Power BI)      │
    │ data/history │  │ data/processed/     │
    │              │  │ errors_YYYY-Www.csv │
    └──────────────┘  └─────────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │   Power BI       │
                   │ Dashboard Rapport│
                   └──────────────────┘
```

## 🗂️ Structure du projet

```
migration-error-aggregation/
├── data/
│   ├── raw/                    # Exports bruts du SSM (déposer CSV ici)
│   │   └── erreursvalidation*.txt
│   ├── processed/              # Données agrégées en CSV pour Power BI
│   │   └── errors_2024-W33.csv
│   └── history/                # Historique JSON de tous les exports
│       └── error_history.json
├── scripts/
│   ├── aggregate_errors.py     # Script principal ✨
│   └── __init__.py
├── powerbi/
│   ├── error_aggregation.pbix  # Template Power BI professionnel
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md         # Ce fichier
│   └── procedures/             # Modes opératoires par erreur
│       └── ERROR_PROCEDURES.md
└── README.md
```

## 📈 Données et métriques

### Entrée
**Fichier TSV/CSV du SSM avec colonnes :**
- `Groupe` - Groupe de migration
- `CodeSite` - Code du site (AF796, AI362, etc.)
- `Scope` - Domaine (Contrat, Patrimoine, Exploitation, Valorisation)
- `Id` - Numéro d'erreur
- `Message` - Message d'erreur en français
- **`Criticite`** - **Filter: "Error" uniquement** ⚠️
- `NbOccurrence` - Nombre de fois l'erreur

### Sortie (JSON History)
```json
{
  "2024-W33": {
    "week": "2024-W33",
    "processed_date": "2026-08-14T22:30:00",
    "source_file": "erreursvalidationEST_1.txt",
    "total_blocking_errors": 250,
    "unique_error_types": 61,
    "affected_sites": ["AF796", "AI362", ...],
    "num_affected_sites": 187,
    "resolved_sites": [],
    "num_resolved": 0,
    "aggregated_errors": {
      "21104_Le local n'existe pas.": {
        "scope": "Patrimoine - PDS Eau Froide",
        "error_id": "21104",
        "message": "Le local n'existe pas.",
        "sites_affected": ["AF796", "AI362", ...],
        "num_sites": 22,
        "total_occurrences": 92
      }
    }
  }
}
```

### Sortie (CSV pour Power BI)
```
Week,ErrorType,Scope,ErrorID,Message,AffectedSites,NumSites,TotalOccurrences
2024-W33,21104_Le local...,Patrimoine - PDS Eau Froide,21104,Le local n'existe pas.,AF796;AI362;...,22,92
```

## 🔄 Processus hebdomadaire

### Étape 1️⃣ - Export depuis SSM
1. Dans le Self-Service Migration tool
2. Exporter les erreurs de validation: `erreursvalidationEST_2024-W34.txt`
3. Placer dans: `data/raw/`

### Étape 2️⃣ - Agrégation
```bash
cd migration-error-aggregation
python3 scripts/aggregate_errors.py
# Traite automatiquement les fichiers de data/raw
```

### Étape 3️⃣ - Vérification
- Fichier CSV généré: `data/processed/errors_2024-W34.csv`
- Historique mis à jour: `data/history/error_history.json`
- Rapport affiché en terminal

### Étape 4️⃣ - Power BI
1. Ouvrir `powerbi/error_aggregation.pbix`
2. **Rafraîchir la source de données** (pointer vers `data/processed/`)
3. Dashboard se met à jour automatiquement ✨

## 📊 KPIs Power BI recommandés

### Niveau 1 - Vue d'ensemble
- **Carte KPI** : Sites affectés cette semaine
- **Carte KPI** : Sites résolus cette semaine
- **Carte KPI** : Nombre de types d'erreurs bloquantes
- **Graphique en ligne** : Tendance sites affectés (par semaine)

### Niveau 2 - Détail des erreurs
- **Tableau** : Top 20 erreurs (scope, ID, message, sites affectés)
- **Graphique barres** : Erreurs par domaine (Patrimoine, Exploitation, etc.)
- **Graphique barres** : Sites les plus affectés

### Niveau 3 - Évolution
- **Tableau** : Historique semaine par semaine
- **Heatmap** : Sites × Erreurs types
- **Graphique combiné** : Erreurs vs sites résolus (par semaine)

## 🎯 Modes opératoires (à configurer)

Chaque type d'erreur doit avoir un **mode opératoire** associé :

```
ERROR_ID | Message | Scope | Procédure | Responsable | Temps moyen
21104    | Le local n'existe pas | Patrimoine | Créer/corriger local | Patrimoine | 15 min
30115    | Fluides incompatibles | Exploitation | Vérifier fluides | Exploitation | 20 min
```

À stocker dans: `docs/procedures/ERROR_PROCEDURES.md`

## 🔐 Sécurité et accès

- **Données sensibles** : Anonymisation possible des sites si besoin
- **Accès Power BI** : Partager le rapport avec collaborateurs et manager
- **Archivage** : Historique JSON gardé pour audit (version control Git)

## 📝 Notes d'implémentation

### Avantages du système
✅ Automatisation complète (script Python)  
✅ Tracking historique (JSON)  
✅ Détection auto des sites résolus  
✅ Power BI professionnel et moderne  
✅ Flexible (support multi-encoding)  
✅ Versioning (Git)  

### Limitations connues
⚠️ Pas de date dans le CSV SSM → utilise semaine courante  
⚠️ Dépendance de la structure TSV du SSM  

### Évolutions futures
🔮 API REST pour intégration directe SSM  
🔮 Alertes Slack/Email sur erreurs critiques  
🔮 Prédiction IA sur résolution temps  
🔮 Export Power BI automatique  

---

**Version**: 1.0  
**Dernière mise à jour**: 2026-08-14  
**Responsable**: [Équipe OCEA Smart Building]
