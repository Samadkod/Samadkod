# 🚀 Migration Error Aggregation System

**Système d'agrégation et de suivi des erreurs bloquantes de migration OCEA Smart Building**

## 📌 Vue d'ensemble

Cet outil centralise les erreurs de validation de migration provenant du **Self-Service Migration (SSM)** et les agrège **par type d'erreur** et **par semaine**.

### ✨ Fonctionnalités principales

✅ **Agrégation automatique** des erreurs bloquantes par type  
✅ **Suivi hebdomadaire** des sites affectés  
✅ **Détection intelligente** des sites résolus  
✅ **Dashboard Power BI professionnel** pour la visualisation  
✅ **Modes opératoires** documentés pour chaque erreur  
✅ **Historique complet** en JSON (audit trail)  

---

## 🎯 Cas d'usage

**Avant** ❌ :
- Erreurs dispersées ligne par ligne dans SSM
- Difficult d'avoir vue globale
- Pas de tracking de progression
- Clics répétitifs pour chaque site

**Après** ✅ :
- Vue consolidée de toutes les erreurs bloquantes
- Identification rapide des priorités (erreurs au plus d'impact)
- Tracking automatique semaine par semaine
- Dashboard Power BI pour présentation management

---

## 📋 Démarrage rapide

### 1️⃣ Installation

```bash
# Clone repo (déjà fait)
cd /home/user/Samadkod/migration-error-aggregation

# Installer dépendances (Python 3.8+)
pip install -r requirements.txt
```

### 2️⃣ Préparer les données

```bash
# Déposer le fichier CSV/TSV du SSM dans:
# data/raw/erreursvalidation_YYYY-Www.txt

# Structure attendue:
# Groupe | CodeSite | Scope | Id | Message | Criticite | NbOccurrence
```

### 3️⃣ Lancer l'agrégation

```bash
python3 scripts/aggregate_errors.py
```

**Résultat** 📊 :
```
✅ Found 250 blocking error records
✅ Aggregated into 61 error types
✅ Sites affected: 187
💾 Saved to: data/processed/errors_2024-W33.csv
```

### 4️⃣ Ouvrir Power BI

```
powerbi/error_aggregation.pbix
↓
Rafraîchir source (pointer vers data/processed/)
↓
Dashboard automatiquement à jour ✨
```

---

## 📂 Structure du projet

```
migration-error-aggregation/
├── 📊 data/
│   ├── raw/                    # Fichiers export SSM (input)
│   ├── processed/              # CSVs pour Power BI (output)
│   └── history/                # Historique JSON (audit trail)
├── 🐍 scripts/
│   └── aggregate_errors.py     # Script principal
├── 📈 powerbi/
│   └── error_aggregation.pbix  # Dashboard professionnel
├── 📚 docs/
│   ├── ARCHITECTURE.md         # Architecture technique
│   └── procedures/             # Modes opératoires par erreur
└── README.md                   # Ce fichier
```

---

## 🔄 Processus hebdomadaire

### Chaque semaine:

1. **Lundi (ou jour fixe)**
   - Exporter erreurs depuis SSM: `erreursvalidation_2024-W34.txt`
   - Placer dans: `data/raw/`

2. **Exécuter le script**
   ```bash
   python3 scripts/aggregate_errors.py
   ```

3. **Vérifier les résultats**
   - Fichier généré: `data/processed/errors_2024-W34.csv`
   - Historique mis à jour: `data/history/error_history.json`
   - Rapport affiché

4. **Mettre à jour Power BI**
   - Ouvrir: `powerbi/error_aggregation.pbix`
   - Rafraîchir les données
   - Exporter pour partage

5. **Communiquer les résultats**
   - Partager le rapport Power BI avec équipes
   - Assigner les corrections selon modes opératoires
   - Tracker la progression

---

## 📊 Métriques trackées

### Par semaine:
- **Nombre d'erreurs bloquantes** trouvées
- **Nombre de types d'erreurs** uniques
- **Nombre de sites affectés**
- **Nombre de sites résolus** (par rapport semaine précédente)

### Par erreur type:
- **Scope** (Patrimoine, Exploitation, Valorisation, etc.)
- **Error ID** et **Message**
- **Liste des sites affectés**
- **Nombre total d'occurrences**

### Tendances:
- Évolution semaine par semaine
- Erreurs en baisse / hausse
- Sites résolus cumulatifs

---

## 💡 Modes opératoires

Chaque type d'erreur a sa procédure documentée:

**📖 Consulter** : `docs/procedures/ERROR_PROCEDURES.md`

Contient pour chaque erreur:
- 🔍 Cause racine
- 📋 Étapes de résolution
- ⏱️ Temps estimé
- 👥 Responsable

---

## 🎨 Power BI - Recommandations visuelles

### Dashboard proposé:

**Page 1 - Vue d'ensemble**
- KPI Cards: Sites affectés, Sites résolus, Erreurs types
- Graphique ligne: Tendance sites affectés (par semaine)
- Graphique barres: Erreurs par domaine

**Page 2 - Détail des erreurs**
- Tableau: Top 20 erreurs (tri par sites affectés)
- Graphique barres: Sites les plus affectés
- Filtre par Scope / Error ID

**Page 3 - Historique**
- Tableau: Evolution semaine par semaine
- Graphique combiné: Erreurs vs sites résolus
- Heatmap: Sites × Erreurs types

---

## 🔧 Configuration technique

### Encoding
Le script supporte automatiquement:
- UTF-16 (format SSM par défaut)
- UTF-8 avec BOM
- UTF-8
- Latin-1
- CP1252

### Format d'entrée
TSV (Tab-Separated Values) avec colonnes:
```
Groupe | CodeSite | Scope | Id | Message | Criticite | Resolution | NbOccurrence
```

### Format de sortie

**JSON (history)**
```json
{
  "2024-W33": {
    "week": "2024-W33",
    "affected_sites": ["AF796", "AI362", ...],
    "num_affected_sites": 187,
    "resolved_sites": [],
    "aggregated_errors": { ... }
  }
}
```

**CSV (Power BI)**
```csv
Week,ErrorType,Scope,ErrorID,Message,AffectedSites,NumSites,TotalOccurrences
2024-W33,21104_Le local...,Patrimoine - PDS Eau Froide,21104,...,22,92
```

---

## 📊 Exemple de résultat

```
TOP 10 BLOCKING ERRORS BY AFFECTED SITES:

1. [Exploitation - Période consommation] Error 30115
   Message: Seuls les fluides eau froide, eau chaude et CET peuvent faire partie d'une même PCC.
   Affected sites: 27
   Total occurrences: 29

2. [Valorisation - Répartition Ligne Frais] Error 40810
   Message: Le montant doit être renseigné.
   Affected sites: 27
   Total occurrences: 46

3. [Patrimoine - PDS Accessoire] Error 21303
   Message: Le compteur n'existe pas.
   Affected sites: 23
   Total occurrences: 24
```

---

## 🔐 Sécurité

- ✅ Données en local (pas de cloud)
- ✅ Versioning Git (historique)
- ✅ Pas de credentials dans le code
- ✅ Fichiers données exclus via .gitignore (option)

---

## 🚀 Évolutions futures

- 🔮 API REST pour intégration directe SSM
- 🔮 Alertes Slack/Email sur erreurs critiques
- 🔮 Automatisation complète (scheduler cron)
- 🔮 Prédiction résolution temps
- 🔮 Export Power BI automatique (via Power BI REST API)

---

## 📞 Support

**Questions technique?**
- Consulter: `docs/ARCHITECTURE.md`

**Procédure d'erreur?**
- Consulter: `docs/procedures/ERROR_PROCEDURES.md`

**Bug ou amélioration?**
- Ouvrir une issue GitHub
- Ou contacter: [Responsable]

---

## 📝 Notes

- **Python**: 3.8+
- **Format date**: ISO 8601
- **Timezone**: UTC
- **Encoding**: UTF-16 by default (SSM)

---

## 📄 License

OCEA Smart Building - 2026

---

## Version

**v1.0** - Initial release  
**Date**: 2026-08-14  
**Responsable**: [À définir]

---

**Prêt à utiliser! 🚀**

```bash
python3 scripts/aggregate_errors.py
```
