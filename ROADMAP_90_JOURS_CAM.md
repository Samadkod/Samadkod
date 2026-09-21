# Roadmap 90 Jours — CAM QDD Industrialisation
## Phase Opérationnelle : Du Prototype à la Production

**Dates:** J1 = Lundi (date de démarrage)  
**Responsable:** Samadu Codon, Data Analyst QDD  
**Objectif Final:** Dispositif QDD complet en production, conforme ACPR, prêt audit CAC

---

## Synthèse Exécutive

```
Semaines 1-2  │ Inventory & Écoute → Baseline données
Semaines 3-4  │ Validation & Contexte → Ajustements métier
Semaines 5-6  │ Pilotage V1 Interne → Dashboard fonctionnel
Semaines 7-8  │ Corrections & Tuning → Top anomalies résolues
Semaines 9-12 │ Industrialisation SAS → Production + parity tests
Semaines 13   │ Go-Live & Documentation → Handoff ACPR
```

---

## PHASE 1: Jours 1-30 — ÉCOUTE & INVENTORY

### Semaine 1 (J1-J5): Immersion Donnée

**🎯 Objectif :** Comprendre structure données, systèmes source, volume baseline

**À faire :**
- [ ] Meeting kickoff avec :
  - Director Data & Analytics
  - Actuariat (responsable provisions S.17 & BE)
  - Primes (responsable PPNA, prime acquise)
  - Sinistres (responsable réassurance, recoverables)
  - IT Data Engineering

- [ ] Audit données existantes :
  - Inventaire tables actuelles (clients, contrats, sinistres)
  - Volumétrie: nb clients, contrats, sinistres par année
  - Format: CSV, DB, SAS tables?
  - Qualité baseline: % NULL, doublons connus, écarts connus

- [ ] Mapping systèmes source :
  - PAS (Primes/Polices) → contrats.* ?
  - SINISTRE → sinistres.* ?
  - COMPTA → provisions.* ?
  - MDM / Master Clients → clients.id_client, SIRET?

- [ ] Documentation initiale :
  - SQL data profiling de chaque table source
  - Glossaire metier local (termes CAM spécifiques)
  - Schéma relationnel actuel

**Livrables :**
- Report: `Inventory_CAM_DataQuality_Baseline.xlsx`
  - Tab 1: Volume stats by table
  - Tab 2: Quality metrics (% NULL, distinct counts)
  - Tab 3: Known issues
  - Tab 4: Data lineage sketch

---

### Semaine 2 (J8-J12): Validation Registre Métier

**🎯 Objectif :** Aligner registre contrôles avec réalité métier CAM

**À faire :**
- [ ] Review registre contrôles avec actuariat :
  - EXACT_05 (règlement <= provision) — valide pour dossier?
  - RECO_01 (variation N/N-1 15%) — seuil OK ou ajuster?
  - ANOMALIE_01 (P99 * 2) — threshold adapté à CAM?
  - Ajouter contrôles CAM-spécifiques manquants?

- [ ] Validation référentiels domaines :
  - Branches: [RC_PRO, DO, MRP, FLOTTE, DECENNALE] ← complet?
  - Segments: [BTP, Industrie, Commerce] ← complet?
  - LoB S2: [M1_BTP_CONST, M2_FLOTTE, M3_DECENNALE] ← mapping OK?
  - Statuts contrat: [EN_COURS, RESILIE, SUSPENDU] ← autres?
  - Statuts sinistre: [OUVERT, CLOS, REOUVERT, SANS_SUITE] ← autres?

- [ ] Identifier exceptions & cas spéciaux :
  - Produits spécialisés (assurance construction, décennale 10Y)
  - Contrats avec garantie additionnelle
  - Sinistres multi-contrats
  - Réassurance quota vs XS (gestion bilatérale)

- [ ] Première execution moteur sur données **test/anonymisées** :
  - Lancer control_engine sur sample 100 contrats + 50 sinistres
  - Observer comportement (faux positifs, anomalies attendues?)
  - Ajuster seuils si nécessaire

**Livrables :**
- `Control_Registry_CAM_Adjusted.csv` (version validée métier)
- `Referentiels_Domaines_CAM.xlsx` (liste maître des domaines)
- Report: `First_Engine_Run_Analysis.md` (anomalies détectées, seuils ajustements)

---

### Semaine 3-4 (J15-J30): Formation Équipe & Documentation

**🎯 Objectif :** Capacity-building interne, documentation de base

**À faire :**
- [ ] Formation équipe sur QDD :
  - Workshop 1 (2h): Dimensions QDD (exhaustivité, exactitude, cohérence...)
  - Workshop 2 (2h): Solvabilité 2 pour data analysts (BE, SCR, QRT, LoB)
  - Workshop 3 (1.5h): Registre contrôles & utilisation
  - Hands-on: Tracer une anomalie du dashboard au code

- [ ] Documentation data stewardship :
  - Guide: "Comment corriger une anomalie détectée"
  - Guide: "Comment ajouter un contrôle sans développeur"
  - SLA anomalies par criticité
  - Escalade process (qui corriger? IT? Métier?)

- [ ] Setup **staging environment** (test) :
  - Clone production données (anonymisées)
  - Moteur Python opérationnel sur staging
  - Dashboard Streamlit fonctionnel (URL interne)

**Livrables :**
- `Formation_QDD_CAM_Slides.pdf` (3 presentations)
- `Data_Stewardship_Manual.md` (procédures de correction)
- Staging environment live (https://streamlit.internal-cam/.../app_v1)

---

## PHASE 2: Jours 31-60 — PREMIÈRE VISIBILITÉ & TUNING

### Semaine 5 (J31-J35): Go-Live Dashboard Interne

**🎯 Objectif :** Dashboard Streamlit visible métier, premiers insights anomalies

**À faire :**
- [ ] Déploiement dashboard **interne** :
  - URL: https://streamlit.internal-cam/...
  - Audience: Actuariat, Primes, Sinistres, IT
  - Données: 100% production (mensuelle, date_arrete = fin mois précédent)

- [ ] Customisation dashboard pour CAM :
  - Ajouter logo CAM
  - Ajouter KPIs metrics (taux conformité par domaine)
  - Ajouter drill-down par branche (RC_DECENNALE anomalies spécifiques)
  - Export anomalies → Excel (pour corrections)

- [ ] Premier report anomalies :
  - Top 5 contrôles KO
  - Top 10 anomalies par table
  - Hypothèses root-cause (données source? Seuils?)

**Livrables :**
- Dashboard Streamlit live + URL de staging
- Report: `Week1_Anomaly_Summary.xlsx` (top anomalies, patterns)
- Escalade priorités (critical vs. nice-to-have)

---

### Semaine 6 (J36-J40): Root Cause Analysis (Top 5)

**🎯 Objectif :** Investiguer & corriger top 5 anomalies

**Anomalies probables :**
1. **EXHAUS_02 (champs obligatoires contrats)** → Données source incomplètes?
2. **EXACT_03/04 (montants négatifs)** → Erreur ETL?
3. **COHER_02 (sinistre après effet)** → Délai source?
4. **INT_01 (FK sinistre→contrat)** → Orphelins temporaires?
5. **RECO_01 (variation N/N-1)** → Affaires nouvelles masquées?

**À faire :**
- [ ] Pour chaque anomalie :
  - 1. Tracer dans données source (SQL query, SAS PROC PRINT)
  - 2. Identifier root-cause (code source, data quality, seuil trop strict)
  - 3. Décider: Corriger donnée? Ajuster seuil? Accepter comme exception?
  - 4. Implémenter correction & re-test

- [ ] Correction data vs. métadonnées :
  - Data issues → IT ETL owner (fix script)
  - Metadata (seuil) → Ajuster control_registry.csv + re-run

- [ ] Validation correction :
  - Re-run moteur complet
  - Vérifier anomalie disparue ou réduite
  - Vérifier aucune régression sur autres contrôles

**Livrables :**
- `Top5_RootCause_Analysis.md` (pour chaque anomalie: cause, action)
- Updated `control_registry.csv` (seuils ajustés si nécessaire)
- Report: `Week2_Corrections_Impact.xlsx` (before/after metrics)

---

### Semaine 7 (J41-J45): Réconciliation Métier

**🎯 Objectif :** Aligner anomalies détectées avec attentes métier

**À faire :**
- [ ] Workshop réconciliation avec :
  - Actuariat: Provisions OK? BE calculée correctement?
  - Primes: Prime acquise = prime émise - PPNA? PPNA calculation OK?
  - Sinistres: Triangles liquidation cohérents? Recoverables correct?

- [ ] QA controls :
  - Total primes Streamlit == Total primes compta?
  - Total provisions BE == Total réserves comptables?
  - Reinsurance ceded tracing to recoverables net?

- [ ] Ajuster tolérances si nécessaire :
  - RECO_02 (5% écart BE) — trop strict?
  - RECO_01 (15% variation volume) — adapté à CAM business?

**Livrables :**
- `Reconciliation_Actuariat_Sign-off.pdf` (validation business)
- Updated tolerances in control_registry.csv
- Métier-approved `Final_Control_Registry_CAM_v1.csv`

---

### Semaine 8 (J46-J50): Stabilisation & Performance

**🎯 Objectif :** Dashboard stable, exécution moteur optimisée

**À faire :**
- [ ] Performance tuning :
  - Temps exécution moteur < 5 min (sur 10M lignes contrats/sinistres)
  - Dashboard load time < 10 sec
  - DuckDB indexes créés sur clés étrangères

- [ ] Stabilité dashboard :
  - Bug fixes (UI crashes, missing columns)
  - Error handling (données manquantes, null checks)
  - Cache results (éviter re-compute à chaque page reload)

- [ ] Préparation transition production :
  - Préparer SQL scripts (for SAS macro version)
  - Documenter assumptions & edge cases
  - Backup plan: rollback process

**Livrables :**
- Performance report (execution times)
- Dashboard stable & tested
- `Transition_To_Production_Checklist.md`

---

## PHASE 3: Jours 51-90 — INDUSTRIALISATION & PRODUCTION

### Semaine 9-10 (J51-J65): SAS Macro Développement

**🎯 Objectif :** Implémenter control engine en SAS (moteur production CAM)

**À faire :**
- [ ] Développer SAS macro version :
  - %CHECK_STRUCTURE (EXHAUS_*)
  - %CHECK_COHERENCE (COHER_*)
  - %CHECK_VALIDITY (VALID_*)
  - %CHECK_INTEGRITY (INT_*)
  - %CHECK_RECONCILIATION (RECO_*)
  - %CHECK_ANOMALY (ANOMALIE_*)

- [ ] Architecture SAS :
  - Lire metadata (control_registry.csv) via PROC IMPORT
  - CALL EXECUTE pour exécution dynamique
  - Output: control_runs + anomalies tables (compatibles Python output)

- [ ] Testing :
  - Unit tests (chaque macro)
  - Integration tests (all together)
  - Parity tests vs. Python engine (byte-for-byte match)

**Livrables :**
- `QDD_Toolkit_SAS_CAM.sas` (complete implementation)
- Test results document (unit + integration + parity)
- `SAS_vs_Python_Parity_Report.xlsx` (100% match validation)

---

### Semaine 11-12 (J66-J80): Intégration Production & CI/CD

**🎯 Objectif :** QDD dispositif en production, automatisé, monitored

**À faire :**
- [ ] Production deployment :
  - SAS batch exécution monthly (28-30 chaque mois, après 24h ETL)
  - Output: control_runs + anomalies to PROD DB
  - Alerting: Email to data stewards si KO > threshold

- [ ] Intégration GitHub Actions :
  - Trigger: data load complete
  - Step 1: SAS macro execution
  - Step 2: Python parity validation
  - Step 3: Dashboard refresh
  - Step 4: Reports generation

- [ ] Documentation production :
  - Runbook: "Exécution mensuelle QDD"
  - Troubleshooting guide
  - Escalade contacts

- [ ] Training production team :
  - SAS macro workshop (2h)
  - Dashboard interpretation (1h)
  - Anomaly correction process (1h)

**Livrables :**
- `QDD_Production_Runbook.md`
- CI/CD pipeline (GitHub Actions YAML)
- Team training completed + sign-off

---

### Semaine 13 (J81-J90): Audit-Readiness & Go-Live

**🎯 Objectif :** Prêt ACPR audit, documentation complète, handoff effectué

**À faire :**
- [ ] Audit preparation :
  - Documentation review (spec, dictionary, lineage, controls)
  - Métadonnées alignment ACPR notice
  - Piste d'audit samples (3 months data)
  - Root cause resolution documentation

- [ ] Final UAT :
  - Métier sign-off: "Contrôles OK"
  - IT sign-off: "Production-ready"
  - Finance/Actuariat: "Reconciliation validated"

- [ ] Go-Live activities :
  - Switch: Python staging → Production SAS
  - Monitoring setup (alerts, dashboards)
  - First production run + validation
  - Métier notification (new process live)

- [ ] Documentation handoff :
  - Training materials prepared
  - Runbooks for escalations
  - Contact list for support
  - Roadmap for Phase 2 enhancements

**Livrables :**
- `ACPR_Audit_Readiness_Package.pdf` (all 6 livrables compiled)
- Production runbooks & troubleshooting
- Team training certification
- Executive summary: "Phase 1 Complete"

---

## Success Criteria (End of 90 Days)

✅ **Dashboard operational** — 7 tabs, real-time metrics, exportable anomalies  
✅ **25+ contrôles exécutés** — automatisé, métier-validated, SAS-implemented  
✅ **ACPR 6 livrables** — document cadre, dictionary, lineage, controls, tableau de bord, spec  
✅ **Parity SAS/Python** — byte-for-byte identical results  
✅ **Métier buy-in** — Actuariat, Primes, Sinistres trained & sign-off  
✅ **Production-ready** — monthly batch automation, alerts, monitoring  
✅ **Audit-proof** — piste d'audit, root cause resolution, full traceability  

---

## Post-90 Days: Phase 2 Roadmap (Optional)

- [ ] LoB-specific anomaly scoring (RC_DECENNALE tail risk alerts)
- [ ] ORSA scenario testing integration (10Y tail risk simulations)
- [ ] Advanced analytics (anomaly trending, correlation analysis)
- [ ] MDM integration (SIRET master data validation)
- [ ] Qlik Sense dashboard (executive reporting layer)

---

## Contacts & Escalations

| Role | Owner | Ext. | Availability |
|------|-------|------|---|
| Data Analyst QDD | Samadu Codon | ext.XXX | Mon-Fri 8am-6pm |
| Director Data | [Name] | ext.XXX | By appointment |
| Actuariat Lead | [Name] | ext.XXX | Mon-Fri 9am-5pm |
| IT Data Owner | [Name] | ext.XXX | Mon-Fri 8am-5pm |
| ACPR Compliance | [Name] | ext.XXX | On demand |

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-21  
**Next Review:** End of Week 4
