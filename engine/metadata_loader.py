"""Chargeur de métadonnées CSV pour le moteur QDD."""

from pathlib import Path
import pandas as pd
import json


class MetadataLoader:
    """Charge les fichiers CSV de métadonnées."""

    def __init__(self, metadata_dir: str = "metadata"):
        self.metadata_dir = Path(metadata_dir)

    def load_control_registry(self) -> pd.DataFrame:
        """Charge le registre des contrôles."""
        df = pd.read_csv(self.metadata_dir / "control_registry.csv")
        # Parser les colonnes JSON
        df["parametres"] = df["parametres"].apply(
            lambda x: json.loads(x) if pd.notna(x) and isinstance(x, str) else {}
        )
        return df

    def load_data_dictionary(self) -> pd.DataFrame:
        """Charge le dictionnaire de données."""
        return pd.read_csv(self.metadata_dir / "data_dictionary.csv")

    def load_lineage(self) -> pd.DataFrame:
        """Charge le lignage des flux."""
        return pd.read_csv(self.metadata_dir / "lineage_edges.csv")

    def load_control_runs(self) -> pd.DataFrame:
        """Charge l'historique des runs (peut être vide)."""
        try:
            df = pd.read_csv(self.metadata_dir / "control_runs.csv")
            return df if len(df) > 0 else pd.DataFrame()
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def load_anomalies(self) -> pd.DataFrame:
        """Charge les anomalies détectées (peut être vide)."""
        try:
            df = pd.read_csv(self.metadata_dir / "anomalies.csv")
            return df if len(df) > 0 else pd.DataFrame()
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def load_pannes_catalogue(self) -> pd.DataFrame:
        """Charge le catalogue des pannes."""
        return pd.read_csv(self.metadata_dir / "pannes_catalogue.csv")
