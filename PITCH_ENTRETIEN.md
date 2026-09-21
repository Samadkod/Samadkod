# 🎯 Fiche entretien — comment présenter Sentinel QDD-S2

## Le pitch en 30 secondes
> « Pour bien comprendre votre mission, j'ai construit un prototype de dispositif QDD
> orienté Solvabilité 2. Il reprend exactement vos livrables de gouvernance —
> dictionnaire de données, cartographie/lignage, contrôles qualité, reporting et piste
> d'audit — sur un jeu de données assurantielles simulé. L'idée n'est pas l'outil
> (vous êtes sur SAS/SQL/Qlik), mais de montrer que je maîtrise la démarche QDD
> de bout en bout et le cadre réglementaire EIOPA. »

## Correspondance mission → projet (à avoir en tête)

| Attendu de l'offre | Ce que le projet démontre |
|---|---|
| Piloter le dispositif de qualité des données | Moteur de 14 contrôles + score global pondéré par criticité |
| Dictionnaire des données | Onglet dédié, source de vérité qui pilote les contrôles |
| Cartographie et lignage des flux | Graphe source → staging → QDD → datamart → QRT |
| Contrôles et reporting de qualité | Scorecard par dimension EIOPA, statut Bloquant/Majeur/Mineur |
| Automatiser la fiabilisation | Contrôles déclaratifs, extensibles en une ligne |
| Audits ACPR / commissaires aux comptes | Piste d'audit horodatée, export Excel du dossier QDD |
| QRT / Solvabilité 2 | Chaque champ documenté avec son usage aval S2 |

## Les 3 dimensions réglementaires (à citer — ça fait mouche)
Le cadre **EIOPA / Solvabilité 2** évalue la qualité des données sur :
- **Exhaustivité** (completeness) — données complètes, pas d'orphelins
- **Exactitude** (accuracy) — valeurs justes, règles métier respectées
- **Pertinence / Appropriateness** — adaptées à l'usage actuariel

J'ai ajouté les dimensions opérationnelles Cohérence, Validité, Unicité, Intégrité.

## Exemples de contrôles concrets (montrer que c'est du métier assurance)
- Règlement cumulé ≤ provision dossier (cohérence provisions techniques)
- Date de déclaration ≥ date de survenance (délai / IBNR)
- Sinistre rattaché à un contrat existant (intégrité sinistres ↔ primes)
- Branche dans le référentiel des LoB (ventilation QRT)

## Questions probables & réponses
- **« Pourquoi Python et pas SAS ? »** → « Le prototype va vite en Python, mais la
  logique — contrôles déclaratifs, dimensions, criticités — se transpose directement
  en macros SAS et requêtes SQL. C'est la démarche qui compte, pas le langage. »
- **« Comment industrialiser ? »** → planification des extractions ODBC, historisation
  des exécutions (la piste d'audit), seuils d'alerte par criticité, restitution Qlik.
- **« Comment gérer une anomalie ? »** → tri par criticité, blocage de l'alimentation
  S2 si contrôle bloquant KO, boucle de résolution avec les métiers, re-contrôle tracé.

## Points d'honnêteté (à assumer)
- Les données sont **synthétiques** — dit clairement, c'est un démonstrateur.
- Je ne prétends pas connaître SAS au niveau attendu si ce n'est pas le cas : je montre
  la **compréhension du dispositif** et ma capacité à monter vite en compétence.

## À faire avant l'appel
1. Déployer sur Streamlit Cloud et avoir l'URL sous la main.
2. Ouvrir l'onglet **Cartographie** et **Synthèse** — les plus parlants à décrire à l'oral.
3. Relire les 3 dimensions EIOPA et 2-3 contrôles métier pour les citer de mémoire.
