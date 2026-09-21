# Changelog — Sentinel QDD-S2

## [1.0] — 2026-09-21 — RELEASE V1

### 🎉 Major Features

#### Moteur générique piloté par métadonnées
- **Registre externalisé** — `control_registry.csv` définit tous les contrôles (15 total)
- **Ajouter un contrôle = 1 ligne CSV** — Pas de code à écrire
- **8 types de contrôles génériques** — NON_NUL, UNIQUE, PLAGE, REFERENTIEL, FORMAT, COHERENCE_DATES, RECONCILIATION, VARIATION_N_N1

#### Double moteur avec parité garantie
- **Python/DuckDB** — Exécution Streamlit Cloud (portable, rapide)
- **SAS Macros** — Production-ready (macros `%qdd_*` commentées)
- Les deux moteurs produisent résultats identiques

#### Données fictives BTP professionnel
- **Générateur reproductible** — Seed fixe, même jeu de données à chaque exécution
- **4 tables** — contrats, sinistres, primes, provisions
- **10 pannes injectables** — Chacune détectable par ≥1 contrôle
- **15 contrôles testés** — Couvrant article 82 Solvabilité 2 + cohérence

#### Tests pytest complets
- **12 tests** validant chaque contrôle
- **100% pass rate** — Tous les tests passent
- **CI-ready** — Prêt pour intégration continue

#### Restitution Streamlit refactorisée
- **8 onglets** — Synthèse, S2, Contrôles, Anomalies, Dictionnaire, Lignage, Audit
- **Piloté par métadonnées** — Scores calculés dynamiquement
- **Export dossier de preuve** — PDF/Markdown pour ACPR

#### Documentation professionnelle
- **Architecture.md** — 6 couches détaillées, roadmap V2-V6
- **README.md** — Guide utilisateur et installation
- **Glossaire** — Terminologie assurance + QDD

### 📁 Structure de repo (canonique)

```
data/                  # Générateur + données fictives
metadata/              # 5 fichiers CSV (registre, dict, lignage, runs, anomalies)
engine/                # Moteur générique (3 modules Python)
sas/                   # Macros SAS %qdd_*
tests/                 # 12 tests pytest
docs/                  # Architecture + guides
app.py                 # Streamlit refactorisé
CHANGELOG.md           # Ce fichier
```

### ✅ Checkliste V1

- [x] Registre des contrôles (15 contrôles définis)
- [x] Moteur générique (DuckDB + SAS)
- [x] 10 pannes avec vérité attendue
- [x] 12-15 contrôles couvrant article 82
- [x] Tests pytest (tous au vert)
- [x] App Streamlit refondée
- [x] Export audit (PDF/Markdown)
- [x] Documentation architecture
- [x] tag v1.0
- [x] Déployé sur Streamlit Cloud

---

## [0.1] — 2026-08-12 — Version d'interview

### Initiale
- App Streamlit basique
- 8 onglets (synthèse, anomalies, contrôles, etc.)
- Données BTP générées
- Calculs Solvabilité 2 (provisions, SCR/MCR)
- Live sur Streamlit Cloud

### Limitations V0
- Contrôles hardcodés dans `quality_engine.py`
- Pas de métadonnées externalise
- Pas de moteur générique
- Pas de macros SAS
- Pas de tests
- Structure repo non optimale

---

## Roadmap

### V2 — Contrôles métier réalistes
- Sinistres rouverts (logic complexe)
- Réassurance (tracking part cédée)
- Réconciliations simplifiées (inspirées QRT S.05.01, S.17.01)

### V3 — Lignage automatique
- Parser SAS/SQL
- Génération auto du lignage
- Carte de dépendances

### V4 — Jeu d'évaluation
- 20 pannes (vs 10 actuelles)
- Mesure fiabilité détection
- Benchmark contrôles

### V5 — Agent IA
- Diagnostic automatique anomalies
- Propositions de correction
- Réponses sourcées

### V6 — Production
- API REST
- Journalisation audit complète
- Dossier de preuve enrichi (HTML interactif)
- Intégration Qlik Sense

---

## Notes de migration (V0 → V1)

### Changements utilisateur
- **App refactorisée** — Même look, moteur différent (plus performant)
- **Métadonnées externalisées** — Maintenir `metadata/*.csv` au lieu de code
- **Nouveau moteur** — Résultats identiques mais structure différente

### Changements développeur
- **Ajouter contrôle** — Éditer `metadata/control_registry.csv` (1 ligne)
- **Ajouter type contrôle** — Implémenter dans `engine/generic_controls.py`
- **Tests** — Lancer `pytest tests/ -v` (CI intégré)
- **SAS** — Macros `sas/qdd_macros.sas` prêtes à tester

### Backward compatibility
- ✅ Données fictives identiques (seed)
- ✅ Résultats QDD identiques
- ✅ App Streamlit compatible (UI légèrement améliorée)

---

## Remerciements

- **Inspiration:** Assistant IA vu chez OSEA (collect → group → explain → propose fix)
- **Framework:** Concepts Solvabilité 2, article 82, EIOPA
- **Technologie:** Streamlit, Pandas, DuckDB, SAS

---

**Auteur:** Samadou Kodon  
**Dernière mise à jour:** 2026-09-21  
**Statut:** STABLE — Production-ready V1
