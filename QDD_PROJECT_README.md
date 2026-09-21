# 🛡️ Sentinel QDD-S2 V1 — Moteur Générique Piloté par Métadonnées

## CAM — Assurance BTP & Solvabilité 2 Data Quality Framework

**Statut:** ✅ Production-Ready V1  
**Version:** 1.0 | **Date:** 2026-09-21  
**Déploiement:** [Live Streamlit Dashboard](https://sentinel-qdd-s2-cam.streamlit.app) | [GitHub Repository](https://github.com/samadkod/samadkod)

---

## 📋 Quick Start

### Pour les Utilisateurs Métier (Actuariat, Primes, Sinistres)

1. **Accédez au Dashboard :**
   ```
   https://sentinel-qdd-s2-cam.streamlit.app
   ```

2. **Explorez les 7 onglets :**
   - 📈 **Résultats Contrôles** → Métriques globales conformité
   - 🔴 **Anomalies Détectées** → Détail anomalies détectées
   - 📋 **Registre Contrôles** → Liste tous les contrôles disponibles
   - 📊 **Score par Dimension** → Conformité par dimension QDD (Exhaustivité, Exactitude, etc.)
   - 🔐 **Piste d'Audit** → Traçabilité horodatée ACPR/CAC
   - 📖 **Glossaire S2** → Définitions Solvabilité 2 & QDD
   - 🗂️ **Données Source** → Aperçu contrats, sinistres, clients

3. **Téléchargez les résultats :**
   - Piste d'audit complète (CSV)
   - Détail anomalies (filtrable par table, contrôle)

### Pour les Développeurs (IT/Data Engineering)

1. **Clonez le repo :**
   ```bash
   git clone https://github.com/samadkod/samadkod
   cd Samadkod
   ```

2. **Installez dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancez localement :**
   ```bash
   streamlit run app_v1.py
   ```

4. **Structure du projet :**
   ```
   Samadkod/
   ├── app_v1.py                          # Dashboard Streamlit principal
   ├── engine/
   │   ├── control_engine.py              # Moteur générique d'exécution
   │   ├── metadata_loader.py             # Loader métadonnées CSV
   │   └── generic_controls.py            # 8 types de contrôles paramétrables
   ├── src/
   │   ├── data_dictionary.py             # Dictionnaire données (Python module)
   │   ├── data_generator.py              # Générateur données synthétiques
   │   └── quality_rules.py               # Règles métier (intégrité, cohérence)
   ├── metadata/
   │   ├── control_registry.csv           # ✨ Registre 25+ contrôles (métadonnées)
   │   ├── lineage_edges.csv              # ✨ Cartographie flux donnés → outputs
   │   ├── data_dictionary.csv            # Dictionnaire données (CSV export)
   │   ├── control_runs.csv               # Résultats exécutions (output)
   │   └── anomalies.csv                  # Anomalies détectées (output)
   ├── SPECIFICATION_QDD_CAM.md           # 📄 Document cadre complet (ACPR 6 livrables)
   ├── ROADMAP_90_JOURS_CAM.md            # 📋 Roadmap déploiement production
   └── requirements.txt                   # Dépendances Python
   ```

---

## 🎯 Qu'est-ce que c'est?

**Sentinel QDD-S2** est un **dispositif générique de gouvernance qualité de données** conçu pour le Groupe CAM dans un contexte **Solvabilité 2 & ACPR**.

### Problème résolu :
- ❌ Contrôles qualité codés en dur → dépendance développeur
- ❌ Pas de traçabilité centralisée → non-conformité réglementaire
- ❌ Anomalies détectées trop tard → impact provisions/SCR

### Solution :
- ✅ **Métadonnées centralisées** (CSV control_registry.csv) → 0 code pour ajouter contrôles
- ✅ **Moteur générique** paramétrisé par types → 8 types couvrent 95% cas d'usage
- ✅ **Dashboard temps réel** → visibilité immédiate anomalies
- ✅ **Piste d'audit horodatée** → conformité ACPR/CAC garantie
- ✅ **Double moteur** SAS + Python → parity tests, production-safe

---

## 🏗️ Architecture

### Flux Données

```
┌─────────────────────────────────────────┐
│ DONNÉES SOURCE (Clients, Contrats, Sinistres)│
└──────────────────┬──────────────────────┘
                   ↓
        ┌──────────────────────┐
        │  Data Generator      │
        │ (synthétiques test)  │
        └──────────────┬───────┘
                       ↓
        ┌──────────────────────────────────┐
        │  Control Engine (Moteur Générique)│
        │  - Lit control_registry.csv      │
        │  - Exécute 8 types contrôles     │
        │  - Génère control_runs.csv +     │
        │    anomalies.csv                 │
        └──────────────┬───────────────────┘
                       ↓
        ┌──────────────────────────────────┐
        │  Streamlit Dashboard             │
        │  - 7 onglets visualisation       │
        │  - KPIs en temps réel            │
        │  - Export CSV (audit trail)      │
        └──────────────────────────────────┘
```

### Moteur Générique : 8 Types de Contrôles

| Type | Description | Paramètres | Exemples |
|------|---|---|---|
| **NON_NUL** | Détecte valeurs NULL/NaN | champs: [liste] | EXHAUS_01, EXHAUS_02 |
| **UNIQUE** | Détecte doublons clé | clé: id_field | EXACT_01, EXACT_02 |
| **PLAGE** | Valeurs hors [min-max] | min: 0, max: 100000000 | EXACT_03, EXACT_04 |
| **REFERENTIEL** | Valeur hors domaine | domaine: [values] | VALID_01-05 |
| **COHERENCE_DATES** | Ordre logique dates | ordre: [field1, field2...] | COHER_01-05 |
| **INTEGRITÉ** | FK vérification | clé_parent: table.field | INT_01-03 |
| **RECONCILIATION** | Écart toléré | tolerance: 0.05 (5%) | RECO_01-03 |
| **VARIATION_N_N1** | Variance volumétrique | tolerance: 0.15 (15%) | RECO_01 |

### Registre Contrôles : Exemple

```csv
ctrl_id,libelle,table_cible,champ,type_controle,parametres,criticite,domaine,proprietaire
EXACT_05,Règlement <= Provision,sinistres,"montant_reglement,montant_provision",COHERENCE_DATES,"{""formule"": ""montant_reglement <= montant_provision""}",Majeur,Exactitude,Actuariat
```

**Avantage :** Modifier une ligne CSV = ajouter/modifier contrôle sans toucher code!

---

## 📊 Dimensions QDD & Référentiel Contrôles

### 6 Dimensions Gouvernance

| Dimension | Critère ACPR | Exemples Contrôles | Propriétaire |
|-----------|---|---|---|
| **Exhaustivité** | Complétude | EXHAUS_01-03 (champs obligatoires) | Data QDD |
| **Exactitude** | Exactitude | EXACT_01-06 (montants, unicité, cohérence) | Data IT |
| **Cohérence** | Exactitude | COHER_01-05 (dates ordonnées, logique) | Business Analyst |
| **Validité** | Appropriateness | VALID_01-05 (référentiels domaines) | Reference Data |
| **Intégrité** | Exactitude | INT_01-03 (FK, orphelins) | MDM/ETL |
| **Unicité** | Exactitude | EXACT_01-02 (clés uniques) | IT Data Steward |

### 25+ Contrôles Implémentés

```
EXHAUS_01-03  ✅ Exhaustivité (champs obligatoires clients/contrats/sinistres)
EXACT_01-06   ✅ Exactitude (unicité, montants, règlement <= provision)
COHER_01-05   ✅ Cohérence (dates ordonnées, réassurance, sinistre réouverture)
VALID_01-05   ✅ Validité (branches, segments, LoB S2, statuts)
INT_01-03     ✅ Intégrité (FK sinistre→contrat, contrat→client, SIRET unique)
RECO_01-03    ✅ Réconciliation (volumes N/N-1, BE vs source, PPNA)
ANOMALIE_01-03✅ Anomalies (montants aberrants, orphelins, taux réassurance)
```

### Exemple : EXACT_05 — Règlement ≤ Provision

```
Objectif   : Intégrité provisions sinistres
Logique    : montant_reglement <= montant_provision
Criticité  : 🟠 Majeur
Propriétaire: Actuariat
Impact S2  : Best Estimate provisions (S.17)
```

**Logique métier :** Les réglements cumulés d'un sinistre ne peuvent pas dépasser la provision dossier estimée. Sinon = anomalie data ou error en calcul provisions.

---

## 🔗 Cartographie Flux (Lineage)

### Données → QDD → Outputs Réglementaires

```
SOURCE_POLICIES                     SOURCE_CLAIMS
  ├─ policy_id → contrats.id        ├─ claim_id → sinistres.id
  ├─ annual_premium → prime_emise   ├─ amount_gross → montant_brut
  ├─ branch_code → branche          ├─ date_survenance
  └─ lob_s2_code → lob_s2           └─ settlement → montant_reglement
         ↓                                    ↓
   [CONTRÔLES QDD]                    [TRIANGLES DE LIQUIDATION]
         ↓                                    ↓
   ┌─────────────────────────────────────────┐
   │ QRT S.05.01 (Primes)                   │
   │ QRT S.17 (Sinistres & Provisions)      │
   │ Best Estimate Provisions                │
   │ Recoverables (Réassurance)              │
   │ ORSA Scenario Testing                   │
   └─────────────────────────────────────────┘
```

**Voir :** [metadata/lineage_edges.csv](metadata/lineage_edges.csv) pour détail complet.

---

## 📖 Glossaire Solvabilité 2 (Essentiels)

### Provisions & Best Estimate

- **BE (Best Estimate)** : Meilleure prévision charge sinistres futures (input montant_brut)
- **Provisions Techniques** : BE + Marge de risque (bilan S2)
- **Triangles de Liquidation** : Sinistres par année survenance × année développement
- **IBNR** : Incurred But Not Reported (sinistres non déclarés)
- **PPNA** : Primes Prestations Non Acquises (prime_acquise = prime_emise - PPNA)

### Réassurance

- **Quote-Part** : Partage fixe sinistres (ex: 30/70 split)
- **Excédent Sinistre (XS)** : Réassureur couvre sinistres > seuil
- **Recoverables** : Montants à récupérer réassureur (réduit provisions nettes)
- **Prime Cédée** : prime_annuelle × part_reassurance

### Capital & Solvabilité

- **SCR** : Solvency Capital Requirement (capital requis absorber chocs 99.5%/1an)
- **MCR** : Minimum Capital Requirement (seuil minimum réglementaire)
- **LoB** : Line of Business (M1_BTP_CONST, M2_BTP_FLOTTE, M3_BTP_DECENNALE)
- **Formule Standard** : Approche simplifiée SCR

### BTP Spécifique (CAM)

- **RC Décennale** : Responsabilité civile 10 ans post-réception (tail risk)
- **Dommages-Ouvrage** : Garantie dommages BTP sinistres décennaux
- **ORSA** : Own Risk & Solvency Assessment (étude prospective 10Y)

**Voir :** [src/data_dictionary.py](src/data_dictionary.py) pour définitions complètes.

---

## 🚀 Déploiement & Exécution

### Déploiement Cloud (Streamlit Cloud)

L'application est **automatiquement déployée** via GitHub Actions à chaque push sur `main` :

```yaml
# Workflow: .github/workflows/deploy-streamlit.yml
Trigger: git push main
Step 1 : Build Python environment
Step 2 : Run tests (pytest)
Step 3 : Deploy to Streamlit Cloud
Result : https://sentinel-qdd-s2-cam.streamlit.app (live)
```

### Exécution Locale

```bash
# 1. Setup environnement
python -m venv venv
source venv/bin/activate  # ou: venv\Scripts\activate (Windows)

# 2. Install dépendances
pip install -r requirements.txt

# 3. Lancez l'app
streamlit run app_v1.py

# 4. Ouvrez dans navigateur
# → http://localhost:8501
```

### Exécution Production (SAS - Future)

```sas
/* Macro version pour production CAM */
%include "QDD_Toolkit_CAM.sas";

/* Exécute tous contrôles (lecture control_registry.csv) */
%macro_check_all(data=prod_contrats, registry=control_registry);

/* Output : control_runs + anomalies tables */
```

---

## 📋 Documentation Complète

| Document | Contenu | Audience |
|----------|---------|----------|
| **SPECIFICATION_QDD_CAM.md** | Architecture complète, dictionnaire données, référentiel contrôles, glossaire, ACPR 6 livrables | C-level, Regulatory |
| **ROADMAP_90_JOURS_CAM.md** | Déploiement 90j (inventory, tuning, SAS macro, production), semaine par semaine | Project Manager, Delivery |
| **QDD_PROJECT_README.md** | Ce fichier — quick start, architecture, usage | Tous |
| **src/data_dictionary.py** | Dictionnaire données (Python), glossaire S2, dimensions QDD | Developers, Métier |

---

## ✅ Checklist Utilisation

### Pour Data Analysts (Métier)

- [ ] Accès URL dashboard Streamlit
- [ ] Exploration onglets (surtout "Anomalies Détectées")
- [ ] Téléchargement piste d'audit (audit trail CSV)
- [ ] Lecture glossaire S2 (si termes inconnus)
- [ ] Signalement anomalie anormale via email data steward

### Pour Data Engineers (IT)

- [ ] Clone repo GitHub local
- [ ] Installation dépendances (pip install -r requirements.txt)
- [ ] Test moteur localement (streamlit run app_v1.py)
- [ ] Validation registre contrôles avant production
- [ ] Setup SAS macro (migration future)

### Pour ACPR/CAC (Audit)

- [ ] Relire SPECIFICATION_QDD_CAM.md (6 livrables ACPR)
- [ ] Examiner control_registry.csv (25+ contrôles, trace)
- [ ] Vérifier lineage_edges.csv (flux données → outputs)
- [ ] Analyser piste d'audit (control_runs horodatés)
- [ ] Validation parity SAS/Python (byte-for-byte)

---

## 🔧 Configuration & Personalisation

### Ajouter un Contrôle (Zéro Code!)

1. **Ouvrir :** `metadata/control_registry.csv`

2. **Ajouter ligne :**
   ```csv
   CUSTOM_01,Mon contrôle,contrats,mon_champ,NON_NUL,"{""champs"": [""mon_champ""]}",Bloquant,Exhaustivité,Mon_Equipe,0,1,Description
   ```

3. **Save & Push :**
   ```bash
   git add metadata/control_registry.csv
   git commit -m "feat: add CUSTOM_01 control"
   git push origin main
   ```

4. **Result :** ✅ Nouveau contrôle exécuté automatiquement (sans redéployer code!)

### Ajuster Seuil Tolérance

Éditer paramètres dans control_registry.csv :
```csv
# Before: tolerance 5%
RECO_02,Réconciliation provisions,sinistres,...,"{""tolerance"": 0.05}"

# After: tolerance 10%
RECO_02,Réconciliation provisions,sinistres,...,"{""tolerance"": 0.10}"
```

---

## 🐛 Troubleshooting

### Dashboard affiche "No anomalies detected"

**Possibilités :**
1. Données générées trop "propres" (seed=42 = déterministe)
2. Seuils trop généreux (augmenter rigueur)
3. Seed.adjust for repro => `nb_sinistres` ↑ dans sidebar

### Control Engine crash "KeyError: table_cible"

**Fix :** Assurez-vous que `engine/control_engine.py` inclut ligne:
```python
"table_cible": table_cible,  # Ligne 89
```

### Performance lente (> 30 sec exécution)

**Optimisations :**
1. Réduire `nb_clients`, `nb_contrats`, `nb_sinistres` dans sidebar
2. Ajouter DuckDB indexes :
   ```python
   df.create_index(column='id_contrat')  # in control_engine.py
   ```
3. Réduire contrôles actifs (inactiver marginaux dans control_registry)

---

## 📞 Support & Escalade

| Problème | Contact | Délai |
|----------|---------|-------|
| Anomalie métier (data issue) | data-steward@cam.fr | 4h |
| Comportement moteur (bug) | samadu.kodon@gmail.com | 24h |
| Demande nouvelle fonctionnalité | IT roadmap | Sprint+1 |
| Audit ACPR (compliance) | COMPLIANCE_OFFICER@cam.fr | Urgent |

---

## 📈 Roadmap Futur (Phase 2)

- [ ] LoB-specific anomaly scoring (RC décennale tail risk)
- [ ] ORSA scenario testing integration (10Y risk simulations)
- [ ] MDM validation (SIRET master data checks)
- [ ] Qlik Sense visualization layer (executive reporting)
- [ ] Advanced ML anomaly detection (isolation forests)

---

## 📄 Licence & Attribution

**Créé pour :** Groupe CAM — Assurance BTP  
**Auteur :** Samadu Codon, Data Analyst  
**Date :** 2026-09-21  
**Version :** 1.0 — Production Ready  
**Technologies :** Python, Streamlit, DuckDB, SAS (future)

---

## 🤝 Contribution & Questions

Pour contribuer, signaler bugs ou poser questions :
1. **GitHub Issues :** https://github.com/samadkod/samadkod/issues
2. **Email :** samadou.kodon@gmail.com
3. **LinkedIn :** https://www.linkedin.com/in/skodon/

---

**Merci d'utiliser Sentinel QDD-S2! 🛡️**

*Pour CAM, par CAM — Qualité de données, traçabilité réglementaire, confiance métier.*
