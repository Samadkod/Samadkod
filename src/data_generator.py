"""
Générateur de données assurantielles synthétiques.

Produit trois tables reliées (Clients, Contrats, Sinistres) qui imitent
un flux amont alimentant les calculs Solvabilité 2 (provisions techniques,
primes, QRT). Des anomalies sont injectées volontairement pour démontrer
la détection par le moteur de contrôles QDD.

Aucune donnée réelle : tout est simulé.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Référentiels métier (branches / produits assurance professionnelle - cohérent GROUPE CAM : BTP, industrie, commerce)
BRANCHES = {
    "RC_PRO": "Responsabilité Civile Professionnelle",
    "DO": "Dommages Ouvrage",
    "MRP": "Multirisque Professionnelle",
    "FLOTTE": "Flotte Automobile",
    "DECENNALE": "Garantie Décennale",
}
SEGMENTS = ["BTP", "Industrie", "Commerce"]
STATUTS_CONTRAT = ["EN_COURS", "RESILIE", "SUSPENDU"]
STATUTS_SINISTRE = ["OUVERT", "CLOS", "SANS_SUITE"]


def _rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def generer_clients(n: int, rng: np.random.Generator) -> pd.DataFrame:
    ids = [f"CLI{100000 + i}" for i in range(n)]
    df = pd.DataFrame(
        {
            "id_client": ids,
            "raison_sociale": [f"Entreprise {i:04d}" for i in range(n)],
            "segment": rng.choice(SEGMENTS, n, p=[0.45, 0.30, 0.25]),
            "code_postal": rng.integers(1000, 96000, n).astype(str),
            "siret": [str(rng.integers(10**13, 10**14)) for _ in range(n)],
            "date_creation": pd.to_datetime("2015-01-01")
            + pd.to_timedelta(rng.integers(0, 3650, n), unit="D"),
        }
    )
    return df


def generer_contrats(
    n: int, clients: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    ids = [f"CTR{500000 + i}" for i in range(n)]
    branches = rng.choice(list(BRANCHES.keys()), n)
    date_effet = pd.to_datetime("2020-01-01") + pd.to_timedelta(
        rng.integers(0, 1825, n), unit="D"
    )
    duree = rng.integers(365, 365 * 5, n)
    df = pd.DataFrame(
        {
            "id_contrat": ids,
            "id_client": rng.choice(clients["id_client"], n),
            "branche": branches,
            "date_effet": date_effet,
            "date_echeance": date_effet + pd.to_timedelta(duree, unit="D"),
            "prime_annuelle": np.round(rng.gamma(3.0, 800, n), 2),
            "capital_assure": np.round(rng.gamma(2.0, 150000, n), 2),
            "statut": rng.choice(STATUTS_CONTRAT, n, p=[0.75, 0.20, 0.05]),
        }
    )
    return df


def generer_sinistres(
    n: int, contrats: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    ids = [f"SIN{900000 + i}" for i in range(n)]
    ctr = contrats.sample(n, replace=True, random_state=1).reset_index(drop=True)
    # survenance après effet du contrat
    lag = rng.integers(1, 900, n)
    date_survenance = ctr["date_effet"] + pd.to_timedelta(lag, unit="D")
    delai_decla = rng.integers(0, 120, n)
    provision = np.round(rng.gamma(2.0, 4000, n), 2)
    reglement = np.round(provision * rng.uniform(0.0, 0.9, n), 2)
    df = pd.DataFrame(
        {
            "id_sinistre": ids,
            "id_contrat": ctr["id_contrat"].values,
            "branche": ctr["branche"].values,
            "date_survenance": date_survenance.values,
            "date_declaration": (date_survenance + pd.to_timedelta(delai_decla, unit="D")).values,
            "montant_provision": provision,
            "montant_reglement": reglement,
            "statut": rng.choice(STATUTS_SINISTRE, n, p=[0.55, 0.40, 0.05]),
        }
    )
    return df


def _injecter_anomalies(
    clients: pd.DataFrame,
    contrats: pd.DataFrame,
    sinistres: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Injecte des anomalies réalistes que le dispositif QDD doit détecter."""

    # 1. Valeurs manquantes sur champ obligatoire (exhaustivité)
    idx = rng.choice(contrats.index, size=max(3, len(contrats) // 40), replace=False)
    contrats.loc[idx, "prime_annuelle"] = np.nan

    idx = rng.choice(clients.index, size=max(2, len(clients) // 50), replace=False)
    clients.loc[idx, "segment"] = None

    # 2. Doublons de clé primaire (unicité)
    dup = contrats.sample(max(2, len(contrats) // 100), random_state=7)
    contrats = pd.concat([contrats, dup], ignore_index=True)

    # 3. Incohérences de dates (cohérence) : échéance avant effet
    idx = rng.choice(contrats.index, size=max(3, len(contrats) // 60), replace=False)
    contrats.loc[idx, "date_echeance"] = contrats.loc[idx, "date_effet"] - pd.Timedelta(days=30)

    # 4. Montants négatifs / invalides (exactitude - règle métier)
    idx = rng.choice(contrats.index, size=max(2, len(contrats) // 80), replace=False)
    contrats.loc[idx, "prime_annuelle"] = -contrats.loc[idx, "prime_annuelle"].abs()

    idx = rng.choice(sinistres.index, size=max(2, len(sinistres) // 60), replace=False)
    sinistres.loc[idx, "montant_provision"] = -1

    # 5. Règlement > provision (cohérence métier provisions techniques)
    idx = rng.choice(sinistres.index, size=max(2, len(sinistres) // 50), replace=False)
    sinistres.loc[idx, "montant_reglement"] = sinistres.loc[idx, "montant_provision"].abs() * 1.5

    # 6. Intégrité référentielle rompue : sinistres orphelins
    idx = rng.choice(sinistres.index, size=max(2, len(sinistres) // 70), replace=False)
    sinistres.loc[idx, "id_contrat"] = "CTR000000"

    # 7. Valeur hors référentiel (validité domaine)
    idx = rng.choice(contrats.index, size=max(2, len(contrats) // 90), replace=False)
    contrats.loc[idx, "branche"] = "INCONNU"

    # 8. Déclaration antérieure à la survenance (cohérence temporelle)
    idx = rng.choice(sinistres.index, size=max(2, len(sinistres) // 80), replace=False)
    sinistres.loc[idx, "date_declaration"] = sinistres.loc[idx, "date_survenance"] - pd.Timedelta(days=10)

    return clients, contrats, sinistres


def generer_jeu_donnees(
    n_clients: int = 800,
    n_contrats: int = 2000,
    n_sinistres: int = 900,
    seed: int = 42,
    avec_anomalies: bool = True,
) -> dict[str, pd.DataFrame]:
    """Point d'entrée : renvoie un dict {nom_table: DataFrame}."""
    rng = _rng(seed)
    clients = generer_clients(n_clients, rng)
    contrats = generer_contrats(n_contrats, clients, rng)
    sinistres = generer_sinistres(n_sinistres, contrats, rng)

    if avec_anomalies:
        clients, contrats, sinistres = _injecter_anomalies(
            clients, contrats, sinistres, rng
        )

    return {"clients": clients, "contrats": contrats, "sinistres": sinistres}
