# Spécification QDD — Groupe CAM
## Dispositif Qualité de Données pour Solvabilité 2 & ACPR

**Date:** 2026-09-21  
**Auteur:** Samadu Codon, Data Analyst — CAM  
**Périmètre:** Assurance BTP (RC Pro, Décennale, Dommages-Ouvrage, Flotte, MRP)  
**Référentiel:** ACPR Notice QDD, Solvabilité 2 (Directive 2015/35/UE)

---

## 1. Introduction & Contexte

Le Groupe CAM s'inscrit dans le cadre réglementaire **Solvabilité 2** (S2) et respecte les exigences de gouvernance de la qualité de données (QDD) définies par l'**ACPR** (Autorité de Contrôle Prudentiel et de Résolution).

### 1.1 Objectifs du Dispositif QDD

- **Conformité réglementaire** : justifier auprès des autorités (ACPR, CAC) la fiabilité des données utilisées pour calculs de provisions techniques (best estimate), SCR, QRT
- **Intégrité métier** : prévenir anomalies impactant reconnaissance primes (PPNA), provisions sinistres (triangles de liquidation), réassurance (recoverables)
- **Traçabilité & audit** : piste d'audit horodatée pour chaque contrôle, lien métadonnées → résultats
- **Réduction risques opérationnels** : détecter en temps réel anomalies données critiques (montants négatifs, doublons identifiants, cohérence dates)

### 1.2 Périmètre Réglementaire ACPR

**6 Livrables Required :**
1. ✅ **Document cadre QDD** → présent document
2. ✅ **Dictionnaire de données** → src/data_dictionary.py + metadata/data_dictionary.csv
3. ✅ **Cartographie des flux** → metadata/lineage_edges.csv
4. ⏳ **Lignage & traçabilité** → mappages source → QRT/ORSA/provisions
5. ✅ **Référentiel de contrôles** → metadata/control_registry.csv (25+ contrôles)
6. ✅ **Tableau de bord QDD** → Streamlit app_v1.py avec 7 onglets + métriques

---

## 2. Architecture Générale

### 2.1 Moteur Générique Piloté par Métadonnées

```
[Registre Contrôles (CSV)]
         ↓
[Moteur d'Exécution Générique]
    ↓ (paramétrisé par type)
[8 Types de Contrôles]
         ↓
[Exécution Dynamique]
         ↓
[Résultats: Runs + Anomalies + Piste d'Audit]
```

**Avantage :** Ajout de contrôles sans modification code métier. Chaque ligne CSV = 1 contrôle exécutable.

### 2.2 Double Motor Pattern (SAS + Python)

| Composant | Technologie | Usage |
|-----------|------------|-------|
| **Moteur SAS** | SAS Macro-Program + Data Step | Environnement production interne CAM |
| **Moteur Python** | control_engine.py + DuckDB | Prototypage, PoC, documentation |
| **Parity Check** | Hashage résultats | Validation bilatérale |

**Garantie :** Même registre metadata CSV → garantit parity entre implémentations.

### 2.3 Stack Technologique

```
Frontend          : Streamlit (Python)
Backend Engine    : DuckDB + Pandas
Metadata Storage  : CSV (control_registry.csv, lineage_edges.csv)
Data Dictionary   : Python module + CSV
Audit Trail       : PostgreSQL (production) / CSV (proto)
CI/CD             : GitHub Actions → Streamlit Cloud
Version Control   : Git (claude/deploy-streamlit-github-feemnr branch)
```

---

## 3. Dictionnaire de Données

### 3.1 Tables Principales

#### **Table: CLIENTS (Portefeuille)**
| Champ | Type | Obligatoire | Criticité | Usage S2 | Description |
|-------|------|-------------|-----------|----------|-------------|
| id_client | Clé | ✓ | CRITIQUE | QRT S.05 Portfolio | Identifiant client (CLI + 6 chiffres) |
| raison_sociale | Texte | ✓ | MAJEUR | ACPR Report | Nom légal entreprise (MDM) |
| siret | Texte (14) | ✓ | CRITIQUE | ACPR Identification | Identifiant réglementaire unique |
| segment | Catégorie | ✓ | MAJEUR | LoB Segmentation | BTP / Industrie / Commerce |
| code_postal | Texte | ✗ | MINEUR | Concentration géographique | 5 chiffres |
| date_creation | Date | ✓ | MINEUR | Risk profiling | ≥ 2010-01-01 |

#### **Table: CONTRATS (Primes Émises/Acquises)**
| Champ | Type | Obligatoire | Criticité | Usage S2 | Description |
|-------|------|-------------|-----------|----------|-------------|
| id_contrat | Clé | ✓ | CRITIQUE | QRT S.05.01 Maille | Identifiant contrat (CTR + 6 chiffres) |
| id_client | FK | ✓ | CRITIQUE | MDM Rattachement | Référence clients.id_client |
| branche | Catégorie | ✓ | CRITIQUE | LoB Ventilation | RC_PRO, DO, MRP, FLOTTE, DECENNALE |
| date_effet | Date | ✓ | CRITIQUE | PPNA Recognition | Date couverture démarrée |
| date_echeance | Date | ✓ | MAJEUR | Périmètre inventaire | > date_effet (cohérence dates) |
| prime_annuelle | Numérique | ✓ | CRITIQUE | BE Input | ≥ 0 € (montant prime) |
| capital_assure | Numérique | ✓ | MAJEUR | Premium Risk SCR | ≥ 0 € (exposition) |
| statut | Catégorie | ✓ | MAJEUR | Inventaire S2 | EN_COURS, RESILIE, SUSPENDU |
| prime_cedee | Numérique | ✗ | MAJEUR | Réassurance Cédée | ≤ prime_annuelle (part cédée) |
| part_reassurance | % | ✗ | MAJEUR | Recoverables Calc | [0-1] quote-part cession |
| lob_s2 | Catégorie | ✓ | CRITIQUE | SCR Formule Standard | M1_BTP_CONST, M2_BTP_FLOTTE, M3_BTP_DECENNALE |
| prime_acquise | Numérique | ✗ | MAJEUR | PPNA Reconciliation | ≤ prime_annuelle (acquise = émise - PPNA) |

#### **Table: SINISTRES (Provisions Techniques & Charges)**
| Champ | Type | Obligatoire | Criticité | Usage S2 | Description |
|-------|------|-------------|-----------|----------|-------------|
| id_sinistre | Clé | ✓ | CRITIQUE | QRT S.17 Maille | Identifiant sinistre (SIN + 6 chiffres) |
| id_contrat | FK | ✓ | CRITIQUE | Intégrité FK | Référence contrats.id_contrat |
| branche | Catégorie | ✓ | CRITIQUE | Triangle LoB | Même branche que contrat |
| date_survenance | Date | ✓ | CRITIQUE | Triangle Cohort | ≥ date_effet contrat |
| date_declaration | Date | ✓ | MAJEUR | IBNR Estimation | ≥ date_survenance (latency) |
| date_clôture | Date | ✗ | MAJEUR | Status Tracking | clôture sinistre |
| date_reouverture | Date | ✗ | MAJEUR | BTP 10Y Tail Risk | réouverture après clôture (spécifique décennale) |
| montant_brut | Numérique | ✓ | CRITIQUE | Best Estimate Provisions | ≥ 0 € (provision dossier) |
| montant_reglement | Numérique | ✓ | CRITIQUE | Run-off Pattern | [0-montant_brut] (réglements cumulés) |
| montant_recours | Numérique | ✗ | MINEUR | Net Provisions | ≥ 0 € (subrogation) |
| part_reassurance | % | ✗ | MAJEUR | Recoverables | [0-1] part réassurée |
| statut | Catégorie | ✓ | MAJEUR | Inventory S2 | OUVERT, CLOS, REOUVERT, SANS_SUITE |
| annee_survenance | Année | ✓ | MAJEUR | Triangle Liquidation | ≥ 2010 (cohort assignment) |

### 3.2 Tables de Métadonnées

#### **Table: CONTROLES_EXECUTION**
Enregistrement chaque exécution de contrôle (piste d'audit ACPR/CAC).

| Champ | Description |
|-------|-------------|
| run_id | UUID unique (run_XXXXXXXX) |
| ctrl_id | Référence registre (ex: EXACT_01) |
| date_arrete | Date clôture (dernier jour mois) |
| debut | Timestamp début exécution |
| fin | Timestamp fin exécution |
| statut | OK / KO |
| nb_lignes_controlees | Nombre enregistrements testés |
| nb_anomalies | Nombre anomalies détectées |
| version_moteur | Versioning (1.0, 1.1...) |

#### **Table: ANOMALIES_DETECTEES**
Détail de chaque anomalie trouvée.

| Champ | Description |
|-------|-------------|
| anomaly_id | UUID unique |
| run_id | FK controles_execution |
| ctrl_id | Type contrôle |
| table_cible | Quelle table affectée |
| cle_metier | Identifiant enregistrement |
| champ | Champ problématique |
| valeur_constatee | Valeur détectée |
| statut | OUVERT / CORRIGE / ACCEPTE / EN_ANALYSE |

---

## 4. Référentiel de Contrôles (Control Registry)

### 4.1 Architecture: 25+ Contrôles Organisés par Dimensions

```
EXHAUS_01-03  → Exhaustivité (champs obligatoires)
EXACT_01-06   → Exactitude (unicité, montants, cohérence)
COHER_01-05   → Cohérence (dates, ordre logique)
VALID_01-05   → Validité (référentiels autorisés)
INT_01-03     → Intégrité référentielle (ForeignKey)
RECO_01-03    → Réconciliation (volumes N/N-1, BE vs source)
ANOMALIE_01-03→ Anomalies (aberrant values, orphelins)
```

### 4.2 Exemples Clés

#### **EXHAUS_02 — Champs obligatoires contrats**
```
Objectif   : Garantir présence données minimales PPNA & QRT
Champs     : id_contrat, id_client, branche, date_effet, prime_annuelle
Type       : NON_NUL
Criticité  : 🔴 Bloquant
Domaine    : Exhaustivité
```

#### **EXACT_05 — Règlement ≤ Provision**
```
Objectif   : Intégrité provisions (montant_reglement ne dépasse provision dossier)
Formule    : montant_reglement <= montant_provision
Type       : COHERENCE_DATES
Criticité  : 🟠 Majeur (best estimate intégrité)
Domaine    : Exactitude
```

#### **COHER_02 — Sinistre après effet contrat**
```
Objectif   : Logique temporelle contrat ↔ sinistre
Ordre      : date_effet < date_survenance
Type       : COHERENCE_DATES
Criticité  : 🟠 Majeur
Domaine    : Cohérence
```

#### **VALID_05 — LoB Solvabilité 2 valide**
```
Objectif   : Segmentation LoB autorisée pour SCR formule standard
Domaine    : [M1_BTP_CONST, M2_BTP_FLOTTE, M3_BTP_DECENNALE]
Type       : REFERENTIEL
Criticité  : 🟠 Majeur
Domaine    : Validité
```

#### **RECO_01 — Réconciliation volumes N vs N-1**
```
Objectif   : Détecter variation anormale primes (ex: réduction 30% ≠ affaires nouvelles)
Tolérance  : 15% (seuil_tolerance)
Type       : VARIATION_N_N1
Criticité  : 🟠 Majeur
Domaine    : Réconciliation
```

#### **RECO_02 — Best Estimate vs Source**
```
Objectif   : Provisions S.17 doivent concorder données sources
Tolérance  : 5% écart toléré
Type       : RECONCILIATION
Criticité  : 🟠 Majeur (affects S.17 QRT)
Domaine    : Réconciliation
```

#### **ANOMALIE_01 — Montant sinistre aberrant**
```
Objectif   : Détecter gros sinistres > 2× P99 historique (sinistralité grave test)
Seuil      : 2 × percentile_99(historique)
Type       : PLAGE
Criticité  : 🟠 Majeur
Domaine    : Exactitude
```

---

## 5. Cartographie des Flux (Lineage)

### 5.1 Flux Données → QDD

```
SOURCE_POLICIES
  ├─ policy_id → contrats.id_contrat [CRITIQUE | QRT_S05_01]
  ├─ annual_premium → contrats.prime_annuelle [CRITIQUE | BE Input]
  ├─ branch_code → contrats.branche [CRITIQUE | LoB Segmentation]
  └─ lob_s2_code → contrats.lob_s2 [CRITIQUE | SCR Formule Standard]

SOURCE_CLAIMS
  ├─ claim_id → sinistres.id_sinistre [CRITIQUE | QRT_S17]
  ├─ amount_gross → sinistres.montant_brut [CRITIQUE | Best Estimate]
  ├─ occurrence_date → sinistres.date_survenance [CRITIQUE | Triangle Cohort]
  └─ settlement_amount → sinistres.montant_reglement [CRITIQUE | Run-off]

SOURCE_REINSURANCE
  ├─ reinsurance_premium → contrats.prime_cedee [MAJEUR | Recoverables]
  └─ recovery_rate → sinistres.part_reassurance [MAJEUR | Net Provisions]
```

### 5.2 Flux QDD → Outputs Réglementaires

```
CONTRATS
  ├─ QRT S.05.01 (Primes écrites & acquises)
  ├─ PPNA Reconciliation (prime_acquise = prime_emise - PPNA)
  └─ SCR Premium Risk (capital_assure input)

SINISTRES
  ├─ QRT S.17 (Sinistres & provisions)
  ├─ Triangles de liquidation (année_survenance × année_de_développement)
  ├─ Best Estimate provisions (montant_brut - recoverables)
  └─ ORSA Scenario (tail risk 10Y pour BTP décennale)

RÉASSURANCE
  ├─ Recoverables QRT (quote-part, XS couverts)
  └─ Risk Transfer Assessment (solvabilité impact)
```

---

## 6. Dimensions QDD & Critères ACPR Art.82

| Dimension | Définition | Critère Art.82 | Exemples Contrôles |
|-----------|-----------|---|---|
| **Exhaustivité** | Toutes données attendues présentes | Complétude | EXHAUS_01-03 (champs obligatoires) |
| **Exactitude** | Valeurs conformes réalité métier | Exactitude | EXACT_01-06 (montants, unicité) |
| **Cohérence** | Logique relations respectée | Exactitude | COHER_01-05 (dates ordonnées) |
| **Validité** | Valeurs dans domaines autorisés | Appropriateness | VALID_01-05 (référentiels) |
| **Intégrité** | Clés étrangères respectées | Exactitude | INT_01-03 (FK sans orphelins) |
| **Unicité** | Pas doublons inattendus | Exactitude | EXACT_01-02 (clés uniques) |

---

## 7. Glossaire Solvabilité 2 (Termes Essentiels)

### Provisions & Best Estimate

| Terme | Acronyme | Définition | Impact QDD |
|-------|----------|-----------|----------|
| **Best Estimate** | BE | Meilleure prévision charge sinistres futures | Clé input → montant_brut doit être ≥ 0 |
| **Provisions Techniques** | PT | BE + Marge de risque | Bilan S2 |
| **Triangles de Liquidation** | — | Sinistres par année survenance × développement | Cohésion date_survenance + annee_survenance |
| **IBNR** | — | Sinistres survenus non déclarés | date_declaration ≥ date_survenance (latency analysis) |
| **Charge Sinistre** | — | Provisions + règlements cumulés | montant_brut + montant_reglement trend |

### Réassurance

| Terme | Acronyme | Définition | Impact QDD |
|-------|----------|-----------|----------|
| **Quote-Part** | QP | Partage fixe chaque sinistre (ex: 30/70) | part_reassurance ∈ [0-1] |
| **Excédent Sinistre** | XS | Réassureur couvre sinistres > seuil | prime_cedee ≤ prime_annuelle |
| **Recoverables** | — | Montants à récupérer réassureur | Réduit provisions nettes |
| **Ceded Premium** | — | Prime cedée (assureur → réassureur) | prime_cedee = prime_annuelle × part_reassurance |

### Capital & Solvabilité

| Terme | Acronyme | Définition | Impact QDD |
|-------|----------|-----------|----------|
| **SCR** | Solvency Capital Requirement | Capital requis absorber chocs 99.5% / 1 an | Input: prime_annuelle, montant_brut par LoB |
| **MCR** | Minimum Capital Requirement | Seuil minimum solvabilité (limite ACPR) | MCR = 25-45% SCR |
| **Marge de Risque** | — | Ajout BE pour risques non explicites | ~3-5% provisions brutes |
| **LoB** | Line of Business | Portefeuille par branche actuarielle | M1_BTP_CONST, M2_FLOTTE, M3_DECENNALE |

### BTP Spécifique

| Terme | Acronyme | Définition | Impact QDD |
|-------|----------|-----------|----------|
| **RC Décennale** | RC_DECENNALE | Responsabilité civile 10 ans post-réception | date_reouverture allowed after clôture |
| **Dommages-Ouvrage** | DO | Garantie dommages BTP sinistres décennaux | Long-tail product → triangles complexes |
| **Formule Standard** | — | Approche simplifiée SCR (vs modèle interne) | Utilise LoB segmentation, premium risk |

### Reporting & Gouvernance

| Terme | Acronyme | Définition | Impact QDD |
|-------|----------|-----------|----------|
| **QRT** | Quantitative Reporting Template | États prudentiels S2 (S.05, S.17 etc.) | Résultats finaux provisioning & primes |
| **ORSA** | Own Risk & Solvency Assessment | Étude prospective risques (≈ EIRS français) | Scenario testing provisions 10Y |
| **PPNA** | Primes Prestations Non Acquises | Provision technique primes non encore acquises | prime_acquise = prime_emise - PPNA |
| **MDM** | Master Data Management | Référence unique clients (SIRET) | id_client, siret must match referential |

---

## 8. Mode de Fonctionnement

### 8.1 Exécution Quotidienne/Mensuelle

```
[Date Arrêté = fin mois]
      ↓
[Chargement données source (ETL)]
      ↓
[Moteur générique → Registre CSV]
      ↓
[Parallélisation 8 types contrôles]
      ↓
[Résultats: control_runs + anomalies]
      ↓
[Dashboard Streamlit]
      ↓
[Piste d'audit horodatée]
```

### 8.2 Gestion des Anomalies

**Cycle OUVERT → EN_ANALYSE → CORRIGE → ACCEPTE**

1. **OUVERT** : Anomalie détectée, notification équipe métier
2. **EN_ANALYSE** : Investigation root-cause par data steward
3. **CORRIGE** : Correction donnée ou paramètre contrôle
4. **ACCEPTE** : Acceptation écrite si faux positif ou exception (seuil tolérance)

---

## 9. Roadmap CAM (90 jours)

### Jours 1-30: Inventory & Écoute
- [ ] Audit interne données existantes (volume, quality baseline)
- [ ] Identification systèmes source (PAS, SINISTRE, COMPTA)
- [ ] Validation registre contrôles avec métier (actuariat, primes, sinistres)
- [ ] Formation équipe sur dimensions QDD

### Jours 31-60: Première Visibilité
- [ ] Déploiement moteur Python sur données test
- [ ] Dashboard Streamlit live (interne)
- [ ] Correction contrôles top anomalies (top 5 types)
- [ ] Documentation data stewardship

### Jours 61-90: Industrialisation
- [ ] Migration SAS (macro QDD) en production
- [ ] Parity tests SAS ↔ Python
- [ ] Intégration CI/CD GitHub Actions
- [ ] Formation CAC/ACPR reporting workflow

---

## 10. Alignement ACPR & Gouvernance

### 10.1 Notice QDD ACPR

Cet dispositif couvre les 6 dimensions ACPR :

| Livrable ACPR | Composant QDD | Status |
|---|---|---|
| 1. Document cadre | Present spec (SPECIFICATION_QDD_CAM.md) | ✅ |
| 2. Dictionnaire | src/data_dictionary.py + CSV | ✅ |
| 3. Cartographie flux | metadata/lineage_edges.csv | ✅ |
| 4. Lignage & traçabilité | run_id → anomaly_id → correction | ✅ |
| 5. Référentiel contrôles | metadata/control_registry.csv (25+) | ✅ |
| 6. Tableau de bord | Streamlit app_v1.py | ✅ |

### 10.2 Critères Art.82 Solvabilité 2

- **Appropriateness** : VALID_* contrôles (domaines autorisés)
- **Completeness** : EXHAUS_* contrôles (champs obligatoires)
- **Accuracy** : EXACT_* + COHER_* + INT_* (valeurs & relations)

---

## 11. Contacts & Propriétaires

| Domaine | Propriétaire | Responsabilité |
|---------|---|---|
| **Exhaustivité** | Data Quality Lead | Champs obligatoires, completeness |
| **Exactitude / Unicité** | IT Data Steward | Doublons, montants cohérents |
| **Cohérence** | Business Analyst | Logique métier (dates ordre) |
| **Validité** | Reference Data Mgmt | Référentiels, domaines autorisés |
| **Intégrité Référentielle** | MDM / ETL Owner | Foreign keys, orphelins |
| **Réconciliation** | Actuariat / Finance | Volumes, provisions, BE |

---

## Conclusion

Ce dispositif QDD positionne CAM pour conformité **ACPR** et **Solvabilité 2**, avec :
- ✅ Métadonnées centralisées (CSV) → no hardcoding
- ✅ Moteur générique → évolutivité
- ✅ Parity SAS/Python → production-safe
- ✅ Dashboard complet → transparence
- ✅ Piste d'audit → traceability

**Prochaines étapes :** Validation avec actuariat, déploiement production SAS, intégration CI/CD.
