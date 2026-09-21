# 🛡️ Sentinel QDD-S2 — Dispositif Qualité des Données Solvabilité 2

Prototype démonstrateur d'un **dispositif de Qualité des Données (QDD)** alimentant
les calculs et reportings **Solvabilité 2**. Il matérialise, en Python / Streamlit,
les livrables de gouvernance attendus sur le poste :

- 📖 **Dictionnaire de données** (source de vérité, pilote les contrôles)
- 🗺️ **Cartographie & lignage des flux** (source → QDD → QRT)
- ✅ **Moteur de contrôles qualité** structuré sur les dimensions réglementaires
  EIOPA (Exhaustivité · Exactitude · Cohérence · Validité · Unicité · Intégrité)
- 📊 **Reporting de qualité** (scorecard par dimension, score global pondéré par criticité)
- 🧾 **Piste d'audit** horodatée et exportable (ACPR / commissaires aux comptes)

> Données 100 % synthétiques. Aucune donnée réelle. Le socle est transposable
> en production sur SAS / SQL / Qlik Sense.

---

## 🚀 Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```
L'application s'ouvre sur http://localhost:8501

## ☁️ Déployer sur Streamlit Community Cloud (gratuit, ~3 min)

1. Créer un dépôt GitHub public et y pousser ce dossier :
   ```bash
   git init && git add . && git commit -m "Sentinel QDD-S2"
   git branch -M main
   git remote add origin https://github.com/<votre-compte>/sentinel-qdd.git
   git push -u origin main
   ```
2. Aller sur https://share.streamlit.io → **New app**
3. Sélectionner le dépôt, la branche `main`, fichier principal `app.py`
4. **Deploy** → l'URL publique est générée automatiquement, à partager en entretien.

Aucune variable d'environnement ni secret n'est nécessaire.

## 🗂️ Structure

```
sentinel-qdd/
├── app.py                  # Application Streamlit (6 onglets)
├── src/
│   ├── data_generator.py   # Données assurantielles synthétiques + anomalies injectées
│   ├── data_dictionary.py  # Dictionnaire de données (gouvernance)
│   ├── quality_engine.py   # Moteur de contrôles + scorecard + piste d'audit
│   └── lineage.py          # Graphe de cartographie / lignage
├── requirements.txt
├── .streamlit/config.toml  # Thème
└── README.md
```

## 🧩 Comment ça marche

1. `data_generator` produit trois tables reliées (Clients, Contrats, Sinistres)
   imitant un flux amont S2, avec des **anomalies injectées volontairement**
   (valeurs manquantes, doublons, dates incohérentes, montants négatifs,
   règlements > provisions, orphelins référentiels, valeurs hors référentiel).
2. `quality_engine` exécute 14 contrôles déclaratifs, chacun rattaché à une
   **dimension réglementaire** et à une **criticité** (Bloquant / Majeur / Mineur).
3. L'app restitue un **score QDD global pondéré**, un **scorecard par dimension**,
   le détail des anomalies, le dictionnaire, la cartographie et la piste d'audit —
   le tout **exportable** (CSV + dossier Excel multi-onglets).

## 🔧 Étendre le dispositif

Ajouter un contrôle = une entrée dans la liste `CONTROLES` de `quality_engine.py` :

```python
Controle("EXA-03", EXACTITUDE, "contrats",
         "Capital assuré cohérent avec la branche", MAJEUR, ma_fonction_masque)
```
Le contrôle est automatiquement intégré au rapport, au scorecard et à la piste d'audit.
