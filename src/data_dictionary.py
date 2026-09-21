"""
Dictionnaire de données — Solvabilité 2 & Gouvernance QDD.

Livrable ACPR : chaque champ documenté (description, localisation, source, usage,
criticité, propriétaire, domaine, fréquence). Source de vérité pour contrôles
d'exhaustivité, exactitude, intégrité référentielle et pertinence.

Solvabilité 2 : provisions techniques, best estimate, marge de risque, QRT,
triangles de liquidation, ORSA, réassurance (quote-part, excédent de sinistre).

BTP Spécifique (CAM) : RC décennale, dommages-ouvrage → sinistres déclarés sur 10 ans.
"""

from __future__ import annotations

import pandas as pd

DICTIONNAIRE = [
    # --- CLIENTS (Portefeuille) ---
    ("clients", "id_client", "Identifiant client", "clé", True, "CLI + 6 chiffres", "Rattachement portefeuille", "CRITIQUE"),
    ("clients", "raison_sociale", "Raison sociale", "texte", True, "-", "Identification / Reporting ACPR", "MAJEUR"),
    ("clients", "segment", "Segment métier", "catégorie", True, "BTP / Industrie / Commerce", "Segmentation risque S2 (LoB)", "MAJEUR"),
    ("clients", "code_postal", "Code postal", "texte", False, "5 chiffres", "Analyse géographique / concentration", "MINEUR"),
    ("clients", "siret", "SIRET (14 chiffres)", "texte", True, "14 chiffres", "MDM / Identification réglementaire", "MAJEUR"),
    ("clients", "date_creation", "Date de création entreprise", "date", True, ">= 2010-01-01", "Ancienneté portefeuille / risque", "MINEUR"),

    # --- CONTRATS (Primes Émises / Acquises) ---
    ("contrats", "id_contrat", "Identifiant contrat", "clé", True, "CTR + 6 chiffres", "Maille QRT S.05 primes", "CRITIQUE"),
    ("contrats", "id_client", "Client rattaché", "clé étrangère", True, "-> clients.id_client", "Intégrité portefeuille / MDM", "CRITIQUE"),
    ("contrats", "branche", "Branche / LoB (Line of Business)", "catégorie", True, "RC_PRO/DO/MRP/FLOTTE/DECENNALE", "Ventilation S2 formule standard / QRT", "CRITIQUE"),
    ("contrats", "date_effet", "Date d'effet couverture", "date", True, "-", "Reconnaissance prime / PPNA / écritures", "CRITIQUE"),
    ("contrats", "date_echeance", "Date d'échéance contrat", "date", True, "> date_effet", "Durée couverture / périmètre S2", "MAJEUR"),
    ("contrats", "prime_annuelle", "Prime annuelle (€)", "numérique", True, ">= 0", "Primes acquises/émises QRT S.05.01 / best estimate", "CRITIQUE"),
    ("contrats", "capital_assure", "Capital assuré (€)", "numérique", True, ">= 0", "Exposition contrat / input SCR premium risk", "MAJEUR"),
    ("contrats", "statut", "Statut du contrat", "catégorie", True, "EN_COURS/RESILIE/SUSPENDU", "Périmètre inventaire S2 / QRT", "MAJEUR"),

    # --- SINISTRES (Provisions Techniques / Charges) ---
    ("sinistres", "id_sinistre", "Identifiant sinistre", "clé", True, "SIN + 6 chiffres", "Maille QRT S.17 sinistres", "CRITIQUE"),
    ("sinistres", "id_contrat", "Contrat rattaché", "clé étrangère", True, "-> contrats.id_contrat", "Intégrité portefeuille / BE", "CRITIQUE"),
    ("sinistres", "branche", "Branche (LoB)", "catégorie", True, "RC_PRO/DO/MRP/FLOTTE/DECENNALE", "Triangles par LoB / S.17", "CRITIQUE"),
    ("sinistres", "date_survenance", "Date de survenance", "date", True, ">= date_effet contrat", "Cadence / triangles liquidation / BE", "CRITIQUE"),
    ("sinistres", "date_declaration", "Date de déclaration sinistre", "date", True, ">= date_survenance", "IBNR / délai déclaration", "MAJEUR"),
    ("sinistres", "montant_provision", "Provision dossier BE (€)", "numérique", True, ">= 0", "Best Estimate provisions techniques S.17 / ORSA", "CRITIQUE"),
    ("sinistres", "montant_reglement", "Règlement cumulé (€)", "numérique", True, "0 <= x <= provision", "Cadence règlements / triangle / charge", "MAJEUR"),
    ("sinistres", "statut", "Statut sinistre", "catégorie", True, "OUVERT/CLOS/SANS_SUITE", "Périmètre provisionnement / inventaire", "MAJEUR"),

    # --- EXTENSIONS SOLVABILITÉ 2 & RÉASSURANCE ---
    ("sinistres", "montant_recours", "Recours (€)", "numérique", False, ">= 0", "Réduction best estimate / provisions nettes", "MINEUR"),
    ("sinistres", "part_reassurance", "Part réassurance (%)", "numérique", False, "[0, 1]", "Quote-part cédée / recoverables QRT", "MAJEUR"),
    ("sinistres", "annee_survenance", "Année de survenance", "année", True, ">= 2010", "Triangles de liquidation / analyse longue queue", "MAJEUR"),

    # --- METADATA QDD ---
    ("controles_execution", "run_id", "Identifiant exécution contrôle", "clé", True, "UUID", "Piste d'audit / traçabilité ACPR", "CRITIQUE"),
    ("controles_execution", "ctrl_id", "Identifiant du contrôle", "clé étrangère", True, "EXH/EXA/COH/VAL/INT-XX", "Référentiel contrôles", "CRITIQUE"),
    ("controles_execution", "date_arrete", "Date d'arrêté (clôture)", "date", True, "dernier jour mois", "Périmètre QRT / ORSA", "CRITIQUE"),
    ("controles_execution", "nb_anomalies", "Nombre d'anomalies détectées", "numérique", True, ">= 0", "Taux conformité / tableau de bord QDD", "MAJEUR"),
]

COLONNES = [
    "table",
    "champ",
    "libelle",
    "type",
    "obligatoire",
    "domaine_referentiel",
    "usage_solvabilite_2",
    "criticite",
]

GLOSSAIRE_SOLVABILITE2 = {
    "BE": "Best Estimate - estimation de la meilleure prévision de la charge future",
    "Provisions techniques": "BE + Marge de risque",
    "SCR": "Solvency Capital Requirement - capital requis pour absorber chocs 99.5% sur 1 an",
    "MCR": "Minimum Capital Requirement - seuil minimum de solvabilité (limite réglementaire)",
    "QRT": "Quantitative Reporting Template - états quantitatifs prudentiels S2",
    "ORSA": "Own Risk and Solvency Assessment - étude prospective (équivalent EIRS français)",
    "LoB": "Line of Business - portefeuille par branche (RC_PRO, DO, MRP, FLOTTE, DECENNALE)",
    "Triangles de liquidation": "Tableau des sinistres par année de survenance et année de développement",
    "Charge sinistre": "Coût total de sinistres (provisions + règlements)",
    "Sinistralité grave": "Concentration de très gros sinistres (test de sensibilité S2)",
    "Réassurance quote-part": "Partage fixe de chaque sinistre entre assureur et réassureur",
    "Réassurance excédent de sinistre": "Réassureur couvre sinistres au-delà du seuil de rétention",
    "Recoverables": "Montants à récupérer auprès des réassureurs (réduit les provisions nettes)",
    "PPNA": "Primes et prestations non acquises - provision technique pour primes émises non encore acquises",
    "IBNR": "Incurred But Not Reported - sinistres survenus mais non déclarés (provision S.17)",
    "Marge de risque": "Ajout au BE pour couvrir les risques non pris en compte dans BE",
    "Formule standard": "Approche simplifiée de calcul du SCR (vs modèle interne)",
    "RC décennale": "Responsabilité civile décennale BTP - couverture 10 ans post-réception",
    "Dommages-ouvrage": "Garantie des dommages ouvrage BTP - sinistres longs (décennaux)",
}

DIMENSIONS_QDD = {
    "Exhaustivité": "Toutes les données attendues sont présentes (pas de trous, pas de NULL inattendus)",
    "Exactitude": "Les valeurs correspondent à la réalité métier (règles, plages, cohérence)",
    "Pertinence": "Les données sont appropriées au contexte (ne pas inclure d'exclusions inattendues)",
    "Cohérence": "Relations logiques respectées (dates, montants cohérents)",
    "Intégrité": "Relations de clés étrangères respectées (pas d'orphelins)",
    "Unicité": "Pas de doublons inattendus sur les clés (identifiants uniques)",
}


def dictionnaire_df() -> pd.DataFrame:
    return pd.DataFrame(DICTIONNAIRE, columns=COLONNES)


def champs_obligatoires(table: str) -> list[str]:
    df = dictionnaire_df()
    return df[(df["table"] == table) & (df["obligatoire"])]["champ"].tolist()
