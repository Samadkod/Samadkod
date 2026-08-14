# 📊 Power BI Dashboard - Configuration professionnelle

## 🎯 Objectif

Créer un dashboard **professionnel et intuitif** pour le suivi des erreurs de migration.

---

## 📐 Architecture du rapport

### Page 1️⃣ : Vue d'ensemble (Executive Summary)

**Layout**: Top KPIs + Graphiques tendance

#### KPI Cards (haut)
```
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Sites         │  │   Erreurs        │  │   Sites résolus  │
│   Affectés      │  │   Bloquantes      │  │   Cette semaine  │
│                 │  │                  │  │                  │
│      187        │  │        61        │  │        12        │
│  (↓ 8 vs sem.)  │  │  (→ stable)      │  │   (+2 vs sem.)   │
└─────────────────┘  └──────────────────┘  └──────────────────┘
```

**Graphiques (bas)**

1. **Ligne** : Tendance sites affectés par semaine (6 dernières semaines)
   - Axe Y: Nombre de sites
   - Axe X: Semaines
   - Couleur: Gradient vert→orange→rouge (pire)

2. **Barres horizontales** : Top 5 domaines (Patrimoine, Exploitation, etc.)
   - Trie par nombre de sites affectés
   - Code couleur par domaine

3. **Jauge** : % sites migrés sans erreur
   - Target: 90%
   - Couleur: Rouge (< 70%), Orange (70-85%), Vert (> 85%)

---

### Page 2️⃣ : Détail des erreurs (Error Analysis)

**Layout**: Tableau + Visualisations détail

#### Tableau - Top erreurs
```
Rang | Scope | Error ID | Message | Sites | Occurr. | Procédure
───────────────────────────────────────────────────────────────
 1   | Expl  |  30115   | Fluides  |  27   |   29    | [Lien]
 2   | Valo  |  40810   | Montant  |  27   |   46    | [Lien]
 3   | Patr  |  21303   | Compteur |  23   |   24    | [Lien]
```

**Colonnes**:
- `Scope` : Filtrable
- `ErrorID` : Unique identifier
- `Message` : Tooltip au hover pour texte long
- `Sites` : Nombre de sites touchés (sortable)
- `Occurrences` : Nombre d'occurrences totales
- `Procédure` : Lien vers docs/procedures/

#### Slicers (filtres)
- 📊 Semaine (dropdown)
- 🏢 Domaine/Scope (multi-select)
- 📈 Sévérité (Information/Error) - optionnel

#### Graphique - Erreurs par domaine
- Barres empilées 100%
- Chaque domaine en couleur différente
- Permet voir proportion erreurs par domaine

---

### Page 3️⃣ : Historique & Progression (Trend Analysis)

**Layout**: Timeline + Comparatifs

#### Tableau Historique
```
Semaine  | Sites Aff. | Err. Types | Sites Résolus | Progression
─────────────────────────────────────────────────────────────────
2024-W30 |    245     |     68     |       0       |    -
2024-W31 |    212     |     65     |      33       |   +13%
2024-W32 |    195     |     62     |      17       |   +8%
2024-W33 |    187     |     61     |       8       |   +4%
```

#### Graphique Combiné
- **Colonnes** : Sites affectés (par semaine)
- **Ligne** : Sites résolus cumulatifs (progression)
- Permet voir si courbe descend (bon signal!)

#### Heatmap - Sites × Erreurs
```
        E-30115  E-40810  E-21303  E-21405
Site-1    ⚫
Site-2           ⚫        ⚫
Site-3    ⚫               ⚫        ⚫
```
- Chaque cellule = couleur selon criticité
- Permet identifier sites/erreurs "problématiques"

---

## 🎨 Charte visuelle professionnelle

### Palette de couleurs

**Domaines** (une couleur par domaine):
```
Patrimoine      : Bleu (#2E75B6)
Exploitation    : Vert (#70AD47)
Valorisation    : Orange (#F79645)
Contrat         : Violet (#9E480E)
```

**Sévérité**:
```
Bloquant (Error)    : Rouge (#E74C3C)
Information         : Gris (#95A5A6)
Résolu             : Vert (#27AE60)
Trend positif      : Vert clair
Trend négatif      : Orange/Rouge
```

### Typographie
```
Titre page    : 28pt, Bold, #1F4E78
Titre card    : 18pt, Bold, #2E75B6
Valeur KPI    : 48pt, Bold, Numérique
Sous-titre    : 14pt, Regular, #7F8C8D
Données       : 11pt, Regular, #34495E
```

### Espacement & Layout
```
Marges : 20px
Padding : 15px
Largeur : Responsive (1920px optimal)
Ratio   : 16:9
```

---

## 📊 Détails des visualisations

### 1. Carte KPI - Sites Affectés

```powerbi
Visual Type: Card (multi-row)
Source: Power Query résumé
Valeur principale: DISTINCTCOUNT(CodeSite)
Sous-titre: Comparaison semaine précédente
Format: "187 sites (-8 vs sem.)"
Couleur: Gradient (vert > orange > rouge)
```

### 2. Graphique ligne - Tendance

```powerbi
Visual Type: Line Chart
Données: Week | NumSites
Série: Ligne lisse
Axe X: Semaines (dernier 6 mois)
Axe Y: Nombre de sites (0-300)
Données: Min/Max/Moyenne visible
Couleur: Gradient semaine (ancien→nouveau)
```

### 3. Tableau - Top erreurs

```powerbi
Visual Type: Table
Colonnes: 
  - Scope (texte, filtrable)
  - ErrorID (texte, trie numériquement)
  - Message (texte long)
  - NumSites (nombre, desc. sort)
  - TotalOccurrences (nombre)
  - Procédure (lien hypertexte)
Conditionnel: 
  - NumSites: Barre de données (vert→rouge)
  - TotalOccurrences: Format nombre
Paginé: 20 rows/page
```

### 4. Heatmap - Sites × Erreurs

```powerbi
Visual Type: Matrix visual
Lignes: CodeSite (trie par nb erreurs desc)
Colonnes: ErrorID (trie par impact desc)
Valeur: COUNTROWS() - couleur intensité
Format: Petit multiple avec valeur en centre
```

---

## 🔗 Interactivité & Filtres

### Slicers principaux

1. **Semaine** (Date Slicer)
   - Liste déroulante derniers 12 mois
   - Défaut: Semaine courante
   - Filtre partagé pour toutes pages

2. **Domaine/Scope** (Multi-select)
   - Checkboxes: Patrimoine, Exploitation, Valorisation, Contrat
   - Défaut: Tous sélectionnés
   - Filtre croisé pages 2 & 3

3. **Sévérité** (Buttons)
   - Boutons radio: "Tous" | "Bloquants" | "Info"
   - Défaut: Bloquants uniquement
   - Affecte tableau et graphiques

### Interactions croisées
- Clic sur barre (domaine) → filtre tableau errors
- Clic sur ligne graphique (semaine) → affiche détails
- Clic sur ligne tableau → highlighte sites affectés dans heatmap

---

## 💾 Sources de données

### Fichier CSV
```
Chemin: migration-error-aggregation/data/processed/errors_YYYY-Www.csv
Refresh: Hebdomadaire (manuel)
Format: UTF-8
```

### Transformation Power Query
```powerbi
1. Import CSV
2. Déterminer types colonnes
3. Créer colonne "Week" (date extraction)
4. Split "AffectedSites" (;-separated) → table Sites
5. Créer table lookups (Scope, ErrorID)
6. Relation: Errors → Sites
```

---

## 📈 Recommandations Power BI

### Performance
- Limiter à données 12 derniers mois (archive anciennes)
- Utiliser aggregations pour gros volumes
- Indexer colonnes importantes (Week, ErrorID)

### Maintenance
- Documenter formules DAX
- Versionner rapport (.pbix git)
- Archiver exports mensuels

### Partage
- Publier sur Power BI Service
- Configurer RLS (Row Level Security) si besoin
- Planifier refresh hebdomadaire

### Export
- Ajouter bouton Export Excel (top errors)
- Ajouter bouton Export PDF (pour management)

---

## 📋 Checklist de création

- [ ] Importer données CSV
- [ ] Créer colonnes calculées (Week, etc.)
- [ ] Concevoir page 1 (KPIs)
- [ ] Concevoir page 2 (détail errors)
- [ ] Concevoir page 3 (tendances)
- [ ] Ajouter slicers & filtres
- [ ] Configurer drill-through
- [ ] Tester interactions croisées
- [ ] Optimiser performance
- [ ] Appliquer branding OCEA
- [ ] Tester exports (PDF, Excel)
- [ ] Documenter (formules, refs)
- [ ] Publier sur Power BI Service
- [ ] Configurer auto-refresh

---

## 🎬 Scénarios d'utilisation

### Lors de la présentation au management
1. Montrer Page 1 (vue d'ensemble) - 2 min
2. Mettre en évidence KPI "Sites résolus" - montrer tendance positive
3. Zoomer Page 3 (historique) - montrer courbe baisse
4. Poser question: "Quels domaines demandent le plus d'effort?"
5. Filtrer par domaine le plus problématique
6. Montrer Page 2 (top errors domaine)

### Réunion opérationnelle (équipes métier)
1. Montrer leurs erreurs (filtrer par scope)
2. Mettre en avant top 3 par domaine
3. Rappeler procédure (lien docs)
4. Donner deadline de résolution
5. Fixer follow-up

### Suivi semaine
1. Comparer W(n) vs W(n-1)
2. Identifier erreurs augmentées
3. Valider sites "résolus"
4. Alerte si tendance négatif

---

## 📞 Support Power BI

**Questions création?**
- Microsoft Power BI Docs: https://docs.microsoft.com/power-bi/

**Questions données?**
- Voir: migration-error-aggregation/docs/ARCHITECTURE.md

---

**Version**: 1.0  
**Dernière mise à jour**: 2026-08-14  
**Propriétaire**: OCEA Smart Building
