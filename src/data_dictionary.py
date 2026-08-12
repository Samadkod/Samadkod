"""
Dictionnaire de données.

Livrable de gouvernance : décrit chaque champ (type, obligation, domaine,
usage aval Solvabilité 2). C'est la source de vérité qui pilote une partie
des contrôles d'exhaustivité et de validité.
"""

from __future__ import annotations

import pandas as pd

# Chaque entrée : table, champ, libellé, type, obligatoire, référentiel/domaine, usage S2
DICTIONNAIRE = [
    # --- CLIENTS ---
    ("clients", "id_client", "Identifiant client", "clé", True, "CLI + 6 chiffres", "Rattachement portefeuille"),
    ("clients", "raison_sociale", "Raison sociale", "texte", True, "-", "Reporting / audit"),
    ("clients", "segment", "Segment métier", "catégorie", True, "BTP / Industrie / Commerce", "Segmentation risque S2"),
    ("clients", "code_postal", "Code postal", "texte", False, "5 chiffres", "Analyse géographique"),
    ("clients", "siret", "SIRET", "texte", True, "14 chiffres", "Identification tierce"),
    ("clients", "date_creation", "Date de création", "date", True, ">= 2010-01-01", "Ancienneté portefeuille"),
    # --- CONTRATS ---
    ("contrats", "id_contrat", "Identifiant contrat", "clé", True, "CTR + 6 chiffres", "Maille QRT primes"),
    ("contrats", "id_client", "Client rattaché", "clé étrangère", True, "-> clients.id_client", "Intégrité portefeuille"),
    ("contrats", "branche", "Branche / produit", "catégorie", True, "RC_PRO/DO/MRP/FLOTTE/DECENNALE", "Ventilation LoB S2"),
    ("contrats", "date_effet", "Date d'effet", "date", True, "-", "Reconnaissance prime / PPNA"),
    ("contrats", "date_echeance", "Date d'échéance", "date", True, "> date_effet", "Durée couverture"),
    ("contrats", "prime_annuelle", "Prime annuelle (€)", "numérique", True, ">= 0", "Primes acquises / émises QRT"),
    ("contrats", "capital_assure", "Capital assuré (€)", "numérique", True, ">= 0", "Exposition / SCR"),
    ("contrats", "statut", "Statut du contrat", "catégorie", True, "EN_COURS/RESILIE/SUSPENDU", "Périmètre inventaire"),
    # --- SINISTRES ---
    ("sinistres", "id_sinistre", "Identifiant sinistre", "clé", True, "SIN + 6 chiffres", "Maille QRT sinistres"),
    ("sinistres", "id_contrat", "Contrat rattaché", "clé étrangère", True, "-> contrats.id_contrat", "Intégrité sinistres/primes"),
    ("sinistres", "branche", "Branche", "catégorie", True, "RC_PRO/DO/MRP/FLOTTE/DECENNALE", "Triangles par LoB"),
    ("sinistres", "date_survenance", "Date de survenance", "date", True, ">= date_effet contrat", "Cadence / triangles"),
    ("sinistres", "date_declaration", "Date de déclaration", "date", True, ">= date_survenance", "Délai déclaration / IBNR"),
    ("sinistres", "montant_provision", "Provision dossier (€)", "numérique", True, ">= 0", "Provisions techniques BE"),
    ("sinistres", "montant_reglement", "Règlement cumulé (€)", "numérique", True, "0 <= x <= provision", "Cadence règlements"),
    ("sinistres", "statut", "Statut du sinistre", "catégorie", True, "OUVERT/CLOS/SANS_SUITE", "Périmètre provisionnement"),
]

COLONNES = [
    "table",
    "champ",
    "libelle",
    "type",
    "obligatoire",
    "domaine_referentiel",
    "usage_solvabilite_2",
]


def dictionnaire_df() -> pd.DataFrame:
    return pd.DataFrame(DICTIONNAIRE, columns=COLONNES)


def champs_obligatoires(table: str) -> list[str]:
    df = dictionnaire_df()
    return df[(df["table"] == table) & (df["obligatoire"])]["champ"].tolist()
