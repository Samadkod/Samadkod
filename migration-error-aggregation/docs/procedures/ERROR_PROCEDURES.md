# Modes Opératoires - Erreurs Bloquantes de Migration

## Vue d'ensemble

Ce document documente les procédures de résolution pour chaque type d'erreur bloquante identifiée.

Chaque erreur est indexée par : **[Scope] Error #ID**

---

## 1. [Patrimoine - PDS Eau Froide] Error #21104

**Message** : *Le local n'existe pas.*

### 🔍 Cause
Le local renseigné dans le système source (ancien système) n'existe pas dans la structure cible (Harmonie).

### 📋 Procédure de résolution

**Étape 1 - Vérification**
1. Se connecter à Harmonie
2. Naviguer vers: Gestion Patrimoniale → Locaux
3. Vérifier si le local existe
4. Si absent → créer le local selon standard OCEA

**Étape 2 - Correction**
1. Créer le local manquant avec les informations correctes
2. Lier le local au PDS (Point De Soutirage) Eau Froide
3. Vérifier la nature du local (intérieur/extérieur, étage, etc.)

**Étape 3 - Validation**
1. Re-exporter les erreurs SSM
2. Vérifier que l'erreur a disparu pour ce site

### ⏱️ Temps moyen de résolution
15-30 minutes par site

### 👥 Responsable
Équipe Patrimoine

### 📞 Contacts
- Responsable Patrimoine: [À définir]
- Support technique: patrimoine-support@ocea.fr

---

## 2. [Exploitation - Période consommation] Error #30115

**Message** : *Seuls les fluides eau froide, eau chaude et CET peuvent faire partie d'une même PCC.*

### 🔍 Cause
Plusieurs fluides incompatibles ont été regroupés dans une Période de Consommation Client (PCC).

### 📋 Procédure de résolution

**Étape 1 - Analyse**
1. Accéder au site en erreur dans SSM
2. Consulter la PCC problématique
3. Identifier les fluides déclarés (devrait être EF, EC, CET uniquement)

**Étape 2 - Correction**
- **Option A** : Supprimer la PCC et la recréer avec les bonnes combinaisons
- **Option B** : Séparer les fluides incompatibles en plusieurs PCC
- **Option C** : Corriger la classification des fluides

**Étape 3 - Validation**
1. Vérifier les indices de facturation (si EF/EC/CET cumulés)
2. S'assurer que la PCC respecte les règles de facturation
3. Re-tester la migration

### ⏱️ Temps moyen de résolution
20-45 minutes par site

### 👥 Responsable
Équipe Exploitation

---

## 3. [Valorisation - Répartition Ligne Frais] Error #40810

**Message** : *Le montant doit être renseigné.*

### 🔍 Cause
Un montant de frais de répartition n'a pas été saisi ou est vide dans le système source.

### 📋 Procédure de résolution

**Étape 1 - Localisation**
1. Consulter le site et la période problématique
2. Identifier la ligne de frais sans montant
3. Vérifier si la ligne était présente dans l'ancien système

**Étape 2 - Correction**
1. Saisir le montant correctionnel:
   - Soit reprendre le montant du système source
   - Soit calculer selon la base de répartition (m², nombre d'occupants, etc.)
2. Valider que le montant n'est pas une erreur de saisie

**Étape 3 - Validation**
1. Refaire le calcul de la facture
2. Vérifier la cohérence avec les années précédentes
3. Re-exporter et vérifier disparition erreur

### ⏱️ Temps moyen de résolution
10-20 minutes par site

### 👥 Responsable
Équipe Valorisation / Facturation

---

## 4. [Patrimoine - PDS Accessoire] Error #21303

**Message** : *Le compteur n'existe pas.*

### 🔍 Cause
Un compteur d'accès (eau, gaz, électricité) n'existe pas dans la base patrimoniale.

### 📋 Procédure de résolution

**Étape 1 - Vérification**
1. Accéder au PDS Accessoire du site
2. Vérifier le numéro de compteur
3. Consulter la liste des compteurs disponibles en Harmonie

**Étape 2 - Correction**
- **Cas 1** : Compteur existe mais numéro mal saisi → corriger le numéro
- **Cas 2** : Compteur n'existe pas → créer le compteur dans Harmonie
- **Cas 3** : Compteur retiré → mettre fin au PDS

**Étape 3 - Validation**
1. Verifier les relevés (doivent exister pour le compteur)
2. Valider les index initiaux et finaux
3. Re-valider la migration

### ⏱️ Temps moyen de résolution
15-30 minutes par site

### 👥 Responsable
Équipe Patrimoine (Accessoires)

---

## 5. [Valorisation - Répartition] Error #40722

**Message** : *Le type de Gestion de Mutation ECS et Eau Chaude doivent être identiques.*

### 🔍 Cause
Les paramètres de gestion de mutation pour ECS (Eau Chaude Sanitaire) et EC (Eau Chaude) sont incohérents.

### 📋 Procédure de résolution

**Étape 1 - Analyse**
1. Consulter les paramètres de gestion de mutation du site
2. Vérifier les types déclarés pour ECS et EC
3. Identifier la source de la divergence

**Étape 2 - Correction**
1. Aligner les modes de gestion:
   - Gestion au m² → appliquer à ECS et EC
   - Gestion à l'occupant → appliquer à ECS et EC
   - Gestion forfaitaire → même code forfait

**Étape 3 - Validation**
1. Vérifier impact sur la facturation
2. Recalculer les répartitions
3. Obtenir validation métier si changement important

### ⏱️ Temps moyen de résolution
30-60 minutes par site

### 👥 Responsable
Équipe Valorisation

---

## 📊 Récapitulatif des erreurs

| Error ID | Scope | Message (court) | Sites | Temps | Responsable |
|----------|-------|-----------------|-------|-------|-------------|
| 21104 | Patrimoine - PDS EF | Local inexistant | 22 | 15-30 min | Patrimoine |
| 30115 | Exploitation - PCC | Fluides incompatibles | 27 | 20-45 min | Exploitation |
| 40810 | Valorisation - Frais | Montant manquant | 27 | 10-20 min | Valorisation |
| 21303 | Patrimoine - Accessoire | Compteur inexistant | 23 | 15-30 min | Patrimoine |
| 40722 | Valorisation - Répart | Gestion mutation incohérente | 9 | 30-60 min | Valorisation |
| 21405 | Patrimoine - Échec Maint. | PDS inexistant | 12 | 15-30 min | Patrimoine |
| 21129 | Patrimoine - PDS EF | Modèle appareil incompatible | 8 | 20-40 min | Patrimoine |
| 40017 | Exploitation - PCC | Traitement manquant | 7 | 25-35 min | Exploitation |
| 40019 | Valorisation - Traitement | Périodes chauffe chevauche | 7 | 20-30 min | Valorisation |
| 20902 | Patrimoine - Pose RFC | Pas de radiateur | 7 | 15-25 min | Patrimoine |

---

## 🔄 Workflow de correction

```
Erreur identifiée
        ↓
Consulter procédure (ce doc)
        ↓
Identifier responsable
        ↓
Correction dans système source
        ↓
Re-export SSM
        ↓
Vérification dans Power BI
        ↓
Erreur disparue ✓
```

---

## 📞 Escalade et support

### Niveau 1 - Auto-assistance
Utiliser ce document pour résoudre l'erreur

### Niveau 2 - Support métier
Contacter le responsable du domaine concerné

### Niveau 3 - Support technique
Si problème système: support-migration@ocea.fr

### Niveau 4 - Équipe OCEA Digital
Pour erreurs bloquantes complexes: digital-support@ocea.fr

---

## 📝 Notes

- **Fréquence de mise à jour** : Hebdomadaire après export SSM
- **Format** : À adapter selon évolution des erreurs
- **Version** : 1.0
- **Dernière mise à jour** : 2026-08-14

---

*Document confidentiel OCEA Smart Building - À destination du personnel autorisé uniquement*
