# 📱 SCRIPT DE DÉMONSTRATION DÉTAILLÉ

## Avant de lancer l'app (30 secondes)

> "Avant de montrer l'app, je vais expliquer rapidement ce qu'on va voir.
>
> C'est un prototype d'un dispositif QDD pour une assurance. Il y a 7 onglets. On va en regarder 4 pour que vous compreniez la structure.
>
> L'idée générale: on a des données (clients, contrats, sinistres). On les contrôle avec une série de règles (pas de doublons, montants cohérents, etc.). On détecte les anomalies. Et on montre l'impact sur la solvabilité.
>
> D'accord? Je lance?"

---

## ONGLET 1: SYNTHÈSE QUALITÉ (2-3 minutes)

**Cliquez sur:** "Synthèse qualité" (premier onglet)

> "Voilà le dashboard. En haut, cinq métriques:
>
> - **Score QDD global** (ici 85%) — c'est la santé générale des données. Moyenne pondérée par criticité. Plus c'est élevé, mieux c'est.
>
> - **Contrôles exécutés** (ici 14) — le nombre de règles qu'on a mises en place. Chaque règle teste un aspect de la qualité.
>
> - **Contrôles en échec** — combien de règles ne passent pas. Ici c'est [X]. Si c'est 0, c'est parfait.
>
> - **Anomalies détectées** (ici 287 par exemple) — le nombre de lignes dans les données qui ne respectent pas les règles. Ça peut être un doublon, une donnée manquante, etc.
>
> - **Anomalies bloquantes** — les plus graves. Si y'en a, les données ne sont PAS éligibles aux calculs Solvabilité 2. Vous devez les fixer en urgence.
>
> En bas, trois graphiques:
>
> - **Graphique 1 — Conformité par dimension:** Vous voyez les 6 dimensions EIOPA. L'Exactitude à 95%, Exhaustivité à 88%, etc. C'est la décomposition de la qualité. Ça montre où c'est faible.
>
> - **Graphique 2 — Anomalies par criticité:** Les anomalies bloquantes en rouge, majeures en orange, mineures en bleu. La taille de chaque zone montre son importance.
>
> - **Tableau 3 — Volumétrie:** Combien de lignes dans chaque table. Clients, Contrats, Sinistres. Ça montre le périmètre qu'on contrôle.
>
> En résumé: ce dashboard répond à la question 'comment vont mes données?' en une seconde."

---

## ONGLET 2: SOLVABILITÉ 2 — IMPACT (3-4 minutes) ⭐ CRUCIAL

**Cliquez sur:** "Solvabilité 2 — Impact" (deuxième onglet)

> "Et voilà LE crucial pour vous, à GROUPE CAM.
>
> Ici, on connecte QDD à Solvabilité 2. On montre: les anomalies détectées = impact FINANCIER DIRECT.
>
> **En haut, quatre métriques:**
>
> - **Best Estimate:** c'est le montant des provisions. Ici 3.4 millions. C'est l'argent que vous devez mettre de côté pour les sinistres futurs.
>
> - **Impact qualité:** c'est le coût des anomalies. Ici -1.8M. Ça veut dire: si vos données étaient sans anomalies, vos provisions seraient 1.8M plus élevées. Les anomalies vous font sous-estimer vos provisions.
>
> - **Ratio SCR (Solvency Capital Requirement):** doit être ≥ 100%. Ici c'est 130% — vous êtes conforme. Ça veut dire: pour chaque euro de capital requis, vous en avez 1.30. Vous êtes en bonne santé.
>
> - **Ratio MCR (Minimum Capital Requirement):** seuil critique. Aussi ≥ 100%. Ici c'est conforme aussi.
>
> **Les trois gauges:**
>
> - **Gauche — SCR:** montre votre position vs le capital requis. 130% = largement conforme.
>
> - **Milieu — MCR:** seuil minimum. 145% = conforme. Si c'était < 100%, l'ACPR aurait action immédiate.
>
> - **Droite — Fonds propres vs besoins:** comparaison visuelle. La barre bleue = fonds propres. Les autres = ce que vous devez avoir.
>
> **Ce qu'on montre ici:**
>
> Les anomalies QDD ne sont pas juste un problème informatique. C'est un problème RÉGLEMENTAIRE.
>
> Si vous aviez pas ce contrôle, vous feriez des provisions fausses. Vous rapporteriez des QRT fausses à l'ACPR. Vous seriez en danger de non-conformité.
>
> C'est ça, le lien QDD-S2."

---

## ONGLET 3: CONTRÔLES (1-2 minutes)

**Cliquez sur:** "Contrôles" (troisième onglet)

> "Ici, le registre des contrôles. Chaque ligne = une règle qu'on applique.
>
> Vous voyez:
>
> - **ID du contrôle** — identifiant unique
> - **Dimension** — EIOPA (Exhaustivité, Exactitude, Cohérence, Validité, Unicité, Intégrité)
> - **Table** — Clients? Contrats? Sinistres?
> - **Libellé** — description de la règle ('Pas de doublon', 'Montants positifs', etc.)
> - **Criticité** — Bloquant, Majeur, ou Mineur
> - **Statut** — OK ou KO
> - **Taux conformité** — pourcentage de lignes qui passent la règle
>
> Exemple: 'Pas de doublon client' — table Clients, dimension Unicité, bloquant. Taux 98% — il y a 2% de doublons. À fixer en urgence.
>
> Chez GROUPE CAM, vous en auriez peut-être 30-50, spécialisés pour vos branches (RC, décennale, flotte).
>
> Mais la structure c'est ça: définir, exécuter, tracer."

---

## ONGLET 4: PISTE D'AUDIT (1 minute)

**Cliquez sur:** "Piste d'audit" (septième onglet)

> "Et là, l'audit trail. C'est CAPITAL pour l'ACPR.
>
> Chaque contrôle exécuté est enregistré avec:
> - La date/heure d'exécution
> - Le résultat (OK/KO)
> - Le nombre d'anomalies
>
> Quand l'ACPR vient vous auditer et demande 'prouvez-moi que vous avez bien contrôlé avant de faire vos QRT', vous sortez ce document.
>
> 'Voilà. Chaque jour, ces contrôles sont exécutés. Voilà les résultats. Voilà les anomalies qu'on a trouvées et corrigées.'
>
> C'est votre protection. C'est ce que les commissaires aux comptes regardent aussi.
>
> Vous pouvez l'exporter en Excel pour vos dossiers de gouvernance."

---

## CONCLUSION DE LA DÉMO (30 secondes)

> "Voilà. En 15 minutes, je vous ai montré:
>
> 1. **Comment mesurer la qualité** — score global, par dimension, par criticité
> 2. **Comment ça impacte Solvabilité 2** — Best Estimate, SCR, MCR, en euros
> 3. **Comment on le contrôle** — 14 contrôles (chez vous 30-50)
> 4. **Comment on le prouve** — piste d'audit
>
> C'est le triangle d'or: mesure + impact + contrôle + traçabilité.
>
> Des questions sur la démo?"

---

## TIMING CHECK-IN

- **Intro (30 sec)** ✓
- **Onglet 1 (2-3 min)** ✓
- **Onglet 2 (3-4 min)** ✓ CRUCIAL
- **Onglet 3 (1-2 min)** ✓
- **Onglet 4 (1 min)** ✓
- **Conclusion (30 sec)** ✓
- **Total: 8-11 min** (OK, dans les 15 min)

---

## QUESTIONS POSSIBLES PENDANT LA DÉMO

**"Pourquoi Python et pas SAS?"**
> "Bonne question. C'est un prototype pour montrer la démarche rapidement. En production chez vous, ce serait SAS/SQL bien sûr. L'important c'est la logique."

**"D'où vient cet impact de 1.8M?"**
> "C'est simulé pour la démo. Mais l'idée est vraie: si vous avez 10% de doublons clients, ça fausse votre Best Estimate de X%. Les anomalies causent une perte de fiabilité, donc une réduction des provisions."

**"Vous avez 14 contrôles. Chez nous on en a combien?"**
> "Excellente question — c'est exactement ce que j'aimerais savoir! Vous avez combien de contrôles en production?"

**"Ça prend combien de temps à mettre en place?"**
> "Dépend de votre stack. Si SAS/SQL c'est déjà votre plateforme, je dirais 2-3 mois pour structurer et déployer 30-40 contrôles. Beaucoup dépend de votre infrastructure."

---

## SI L'APP NE CHARGE PAS

1. Vérifiez la WiFi
2. Dites: "Ça arrive, les applis cloud. Un instant, je rafraîchis."
3. Si ça ne marche pas: "Pas de souci. Laissez-moi vous montrer les captures écran" (imprimer quelques captures d'écran d'avance!)
4. Continuez avec le pitch verbal + les imprimés

---

## VARIANTE: SLIDES PRÉIMPRIMÉES

Si vous voulez réduire le risque téchnique, imprimez 4 pages:
1. Screenshot Synthèse
2. Screenshot S2 Impact
3. Screenshot Contrôles
4. Screenshot Piste d'audit

Et dites: "Voilà comment ça vient s'afficher" tout en montrant les imprimés.

---

✅ **Vous êtes couvert!**
