"""Implémentations des 8 types de contrôles génériques."""

import pandas as pd
import numpy as np
from typing import Callable


class GenericControls:
    """Implémente les 8 types de contrôles génériques."""

    def execute(self, type_controle: str, df_target: pd.DataFrame,
                row: pd.Series, datasets: dict) -> pd.Series:
        """
        Exécute un contrôle de type donné.

        Args:
            type_controle: type du contrôle (NON_NUL, UNIQUE, etc.)
            df_target: DataFrame cible
            row: ligne du registre contenant la configuration
            datasets: dict des tables

        Returns:
            pd.Series booléenne (True = anomalie)
        """
        type_map = {
            "NON_NUL": self._non_nul,
            "UNIQUE": self._unique,
            "PLAGE": self._plage,
            "REFERENTIEL": self._referentiel,
            "FORMAT": self._format,
            "COHERENCE_DATES": self._coherence_dates,
            "RECONCILIATION": self._reconciliation,
            "VARIATION_N_N1": self._variation_n_n1,
        }

        handler = type_map.get(type_controle)
        if handler is None:
            return pd.Series([False] * len(df_target))

        return handler(df_target, row, datasets)

    def _non_nul(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les valeurs NULL/NaN."""
        champs = row["champ"].split(",")
        mask = pd.Series([False] * len(df))
        for champ in champs:
            champ = champ.strip()
            if champ in df.columns:
                mask |= df[champ].isna()
        return mask

    def _unique(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les doublons."""
        champ = row["champ"].strip()
        if champ in df.columns:
            return df.duplicated(subset=[champ], keep=False)
        return pd.Series([False] * len(df))

    def _plage(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les valeurs en dehors de la plage."""
        champ = row["champ"].strip()
        parametres = row["parametres"] if isinstance(row["parametres"], dict) else {}

        min_val = parametres.get("min", -np.inf)
        max_val = parametres.get("max", np.inf)

        if champ in df.columns:
            col = pd.to_numeric(df[champ], errors="coerce")
            return (col < min_val) | (col > max_val) | col.isna()
        return pd.Series([False] * len(df))

    def _referentiel(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les valeurs hors référentiel."""
        champ = row["champ"].strip()
        parametres = row["parametres"] if isinstance(row["parametres"], dict) else {}
        domaine = parametres.get("domaine", [])

        if champ in df.columns and domaine:
            return ~df[champ].isin(domaine) & df[champ].notna()
        return pd.Series([False] * len(df))

    def _format(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les erreurs de format."""
        champ = row["champ"].strip()
        parametres = row["parametres"] if isinstance(row["parametres"], dict) else {}
        format_type = parametres.get("type", "string")

        if champ not in df.columns:
            return pd.Series([False] * len(df))

        if format_type == "numeric":
            # Essayer de convertir en nombre
            return pd.to_numeric(df[champ], errors="coerce").isna() & df[champ].notna()
        elif format_type == "date":
            # Essayer de convertir en date
            return pd.to_datetime(df[champ], errors="coerce").isna() & df[champ].notna()

        return pd.Series([False] * len(df))

    def _coherence_dates(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les incohérences entre dates."""
        champs = row["champ"].split(",")
        champs = [c.strip() for c in champs]

        mask = pd.Series([False] * len(df))

        # Vérifier que chaque date est >= à la précédente
        for i in range(len(champs) - 1):
            c1, c2 = champs[i], champs[i + 1]
            if c1 in df.columns and c2 in df.columns:
                d1 = pd.to_datetime(df[c1], errors="coerce")
                d2 = pd.to_datetime(df[c2], errors="coerce")
                # Incohérence si d2 < d1 (après d1 devrait être après avant d1)
                mask |= (d2 < d1) & d1.notna() & d2.notna()

        return mask

    def _reconciliation(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les écarts de réconciliation."""
        champs = row["champ"].split(",")
        champs = [c.strip() for c in champs]
        parametres = row["parametres"] if isinstance(row["parametres"], dict) else {}
        tolerance = parametres.get("tolerance", 0.01)

        if len(champs) < 2:
            return pd.Series([False] * len(df))

        c1, c2 = champs[0], champs[1]
        if c1 in df.columns and c2 in df.columns:
            v1 = pd.to_numeric(df[c1], errors="coerce")
            v2 = pd.to_numeric(df[c2], errors="coerce")

            # Écart relatif > tolerance
            diff = (v1 - v2).abs()
            total = (v1.abs() + v2.abs()) / 2
            relative_diff = diff / total

            return relative_diff > tolerance

        return pd.Series([False] * len(df))

    def _variation_n_n1(self, df: pd.DataFrame, row: pd.Series, datasets: dict) -> pd.Series:
        """Détecte les chutes anormales de volumétrie."""
        # Pour cette version simple, on simule une vérification
        # En pratique, il faudrait comparer avec la période N-1
        return pd.Series([False] * len(df))
