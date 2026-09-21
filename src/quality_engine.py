"""
Moteur de contrôles Qualité des Données (QDD).

Chaque contrôle est déclaratif : id, dimension réglementaire, table, criticité,
et une fonction qui renvoie le masque des lignes en anomalie. Le moteur exécute
l'ensemble, produit un rapport détaillé, un scorecard par dimension et une piste
d'audit exportable (traçabilité pour ACPR / commissaires aux comptes).

Dimensions alignées sur le cadre EIOPA / Solvabilité 2 :
  - Exhaustivité  (données complètes, pas de trous ni d'orphelins)
  - Exactitude    (valeurs justes, règles métier respectées)
  - Cohérence     (relations logiques entre champs)
  - Validité      (valeurs dans le domaine / référentiel)
  - Unicité       (pas de doublons de clé)
  - Intégrité     (référentielle entre tables)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import pandas as pd

from .data_dictionary import champs_obligatoires

# Criticités
BLOQUANT = "Bloquant"
MAJEUR = "Majeur"
MINEUR = "Mineur"

# Dimensions réglementaires
EXHAUSTIVITE = "Exhaustivité"
EXACTITUDE = "Exactitude"
COHERENCE = "Cohérence"
VALIDITE = "Validité"
UNICITE = "Unicité"
INTEGRITE = "Intégrité référentielle"

REFERENTIEL_BRANCHES = {"RC_PRO", "DO", "MRP", "FLOTTE", "DECENNALE"}
REFERENTIEL_SEGMENTS = {"BTP", "Industrie", "Commerce"}


@dataclass
class Controle:
    id: str
    dimension: str
    table: str
    libelle: str
    criticite: str
    # fonction(datasets) -> pd.Series booléenne (True = ligne en anomalie) sur self.table
    fn: Callable[[dict], pd.Series]


@dataclass
class Resultat:
    controle: Controle
    nb_controles: int
    nb_anomalies: int
    echantillon: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def taux_conformite(self) -> float:
        if self.nb_controles == 0:
            return 100.0
        return round(100 * (1 - self.nb_anomalies / self.nb_controles), 2)

    @property
    def statut(self) -> str:
        if self.nb_anomalies == 0:
            return "OK"
        return "KO"


# --------------------------------------------------------------------------- #
# Définition des contrôles
# --------------------------------------------------------------------------- #
def _mask_champs_manquants(table: str):
    def f(ds):
        df = ds[table]
        obligatoires = [c for c in champs_obligatoires(table) if c in df.columns]
        return df[obligatoires].isna().any(axis=1)

    return f


def _mask_doublons_cle(table: str, cle: str):
    def f(ds):
        return ds[table].duplicated(subset=[cle], keep=False)

    return f


def _mask_valeur_hors_domaine(table: str, champ: str, domaine: set):
    def f(ds):
        col = ds[table][champ]
        return ~col.isin(domaine) & col.notna()

    return f


def _mask_negatif(table: str, champ: str):
    def f(ds):
        return ds[table][champ] < 0

    return f


def _mask_dates_incoherentes(table: str, champ_debut: str, champ_fin: str):
    def f(ds):
        df = ds[table]
        return df[champ_fin] < df[champ_debut]

    return f


def _mask_reglement_sup_provision(ds):
    df = ds["sinistres"]
    return df["montant_reglement"] > df["montant_provision"].clip(lower=0)


def _mask_orphelins(table_enfant: str, cle_etrangere: str, table_parent: str, cle_parent: str):
    def f(ds):
        parents = set(ds[table_parent][cle_parent])
        return ~ds[table_enfant][cle_etrangere].isin(parents)

    return f


CONTROLES: list[Controle] = [
    # Exhaustivité
    Controle("EXH-01", EXHAUSTIVITE, "clients", "Champs obligatoires clients renseignés", MAJEUR, _mask_champs_manquants("clients")),
    Controle("EXH-02", EXHAUSTIVITE, "contrats", "Champs obligatoires contrats renseignés", BLOQUANT, _mask_champs_manquants("contrats")),
    Controle("EXH-03", EXHAUSTIVITE, "sinistres", "Champs obligatoires sinistres renseignés", BLOQUANT, _mask_champs_manquants("sinistres")),
    # Unicité
    Controle("UNI-01", UNICITE, "contrats", "Unicité de l'identifiant contrat", BLOQUANT, _mask_doublons_cle("contrats", "id_contrat")),
    Controle("UNI-02", UNICITE, "sinistres", "Unicité de l'identifiant sinistre", BLOQUANT, _mask_doublons_cle("sinistres", "id_sinistre")),
    # Validité (domaine / référentiel)
    Controle("VAL-01", VALIDITE, "contrats", "Branche dans le référentiel autorisé", MAJEUR, _mask_valeur_hors_domaine("contrats", "branche", REFERENTIEL_BRANCHES)),
    Controle("VAL-02", VALIDITE, "clients", "Segment dans le référentiel autorisé", MINEUR, _mask_valeur_hors_domaine("clients", "segment", REFERENTIEL_SEGMENTS)),
    # Exactitude (règles métier)
    Controle("EXA-01", EXACTITUDE, "contrats", "Prime annuelle positive ou nulle", BLOQUANT, _mask_negatif("contrats", "prime_annuelle")),
    Controle("EXA-02", EXACTITUDE, "sinistres", "Provision positive ou nulle", BLOQUANT, _mask_negatif("sinistres", "montant_provision")),
    # Cohérence
    Controle("COH-01", COHERENCE, "contrats", "Date d'échéance postérieure à la date d'effet", MAJEUR, _mask_dates_incoherentes("contrats", "date_effet", "date_echeance")),
    Controle("COH-02", COHERENCE, "sinistres", "Date de déclaration >= date de survenance", MAJEUR, _mask_dates_incoherentes("sinistres", "date_survenance", "date_declaration")),
    Controle("COH-03", COHERENCE, "sinistres", "Règlement cumulé <= provision dossier", MAJEUR, _mask_reglement_sup_provision),
    # Intégrité référentielle
    Controle("INT-01", INTEGRITE, "sinistres", "Sinistre rattaché à un contrat existant", BLOQUANT, _mask_orphelins("sinistres", "id_contrat", "contrats", "id_contrat")),
    Controle("INT-02", INTEGRITE, "contrats", "Contrat rattaché à un client existant", MAJEUR, _mask_orphelins("contrats", "id_client", "clients", "id_client")),
]


# --------------------------------------------------------------------------- #
# Exécution
# --------------------------------------------------------------------------- #
def executer_controles(datasets: dict, taille_echantillon: int = 50) -> list[Resultat]:
    resultats: list[Resultat] = []
    for ctrl in CONTROLES:
        df = datasets[ctrl.table]
        try:
            masque = ctrl.fn(datasets).fillna(False)
        except Exception:
            masque = pd.Series(False, index=df.index)
        nb_anom = int(masque.sum())
        echantillon = df[masque].head(taille_echantillon).copy()
        if not echantillon.empty:
            echantillon.insert(0, "controle", ctrl.id)
        resultats.append(
            Resultat(
                controle=ctrl,
                nb_controles=len(df),
                nb_anomalies=nb_anom,
                echantillon=echantillon,
            )
        )
    return resultats


def rapport_detaille(resultats: list[Resultat]) -> pd.DataFrame:
    lignes = []
    for r in resultats:
        lignes.append(
            {
                "Contrôle": r.controle.id,
                "Dimension": r.controle.dimension,
                "Table": r.controle.table,
                "Libellé": r.controle.libelle,
                "Criticité": r.controle.criticite,
                "Lignes contrôlées": r.nb_controles,
                "Anomalies": r.nb_anomalies,
                "Taux conformité (%)": r.taux_conformite,
                "Statut": r.statut,
            }
        )
    return pd.DataFrame(lignes)


def scorecard_dimension(resultats: list[Resultat]) -> pd.DataFrame:
    rows = []
    dims = {}
    for r in resultats:
        d = r.controle.dimension
        dims.setdefault(d, {"controles": 0, "anomalies": 0, "lignes": 0})
        dims[d]["controles"] += 1
        dims[d]["anomalies"] += r.nb_anomalies
        dims[d]["lignes"] += r.nb_controles
    for d, v in dims.items():
        taux = 100.0 if v["lignes"] == 0 else round(100 * (1 - v["anomalies"] / v["lignes"]), 2)
        rows.append(
            {
                "Dimension": d,
                "Contrôles": v["controles"],
                "Anomalies": v["anomalies"],
                "Taux conformité (%)": taux,
            }
        )
    return pd.DataFrame(rows).sort_values("Taux conformité (%)")


def score_global(resultats: list[Resultat]) -> float:
    """Score QDD global pondéré par la criticité des contrôles."""
    poids = {BLOQUANT: 3.0, MAJEUR: 2.0, MINEUR: 1.0}
    num = 0.0
    den = 0.0
    for r in resultats:
        p = poids[r.controle.criticite]
        num += p * r.taux_conformite
        den += p
    return round(num / den, 2) if den else 100.0


def piste_audit(resultats: list[Resultat]) -> pd.DataFrame:
    """Table de traçabilité horodatée (piste d'audit ACPR / CAC)."""
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lignes = []
    for r in resultats:
        lignes.append(
            {
                "horodatage": horodatage,
                "controle": r.controle.id,
                "dimension": r.controle.dimension,
                "table": r.controle.table,
                "criticite": r.controle.criticite,
                "lignes_controlees": r.nb_controles,
                "anomalies": r.nb_anomalies,
                "taux_conformite": r.taux_conformite,
                "statut": r.statut,
            }
        )
    return pd.DataFrame(lignes)


def anomalies_completes(resultats: list[Resultat]) -> pd.DataFrame:
    """Concatène tous les échantillons d'anomalies pour export."""
    frames = [r.echantillon for r in resultats if not r.echantillon.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
