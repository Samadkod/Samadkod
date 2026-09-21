"""Moteur générique d'exécution des contrôles QDD."""

from datetime import datetime
from uuid import uuid4
import pandas as pd
import duckdb
from .metadata_loader import MetadataLoader
from .generic_controls import GenericControls


class ControlEngine:
    """Moteur générique qui exécute les contrôles piloté par le registre."""

    def __init__(self, metadata_dir: str = "metadata"):
        self.loader = MetadataLoader(metadata_dir)
        self.controls = GenericControls()
        self.registry = self.loader.load_control_registry()
        self.run_timestamp = datetime.now().isoformat()

    def run(self, datasets: dict, date_arrete: str = None) -> tuple:
        """
        Exécute tous les contrôles du registre.

        Args:
            datasets: dict des DataFrames {table_name -> pd.DataFrame}
            date_arrete: date de référence (default: aujourd'hui)

        Returns:
            (control_runs_df, anomalies_df)
        """
        if date_arrete is None:
            date_arrete = datetime.now().strftime("%Y-%m-%d")

        runs = []
        anomalies = []

        # Itérer sur chaque contrôle du registre
        for _, row in self.registry.iterrows():
            if not row["actif"]:  # Sauter les contrôles inactifs
                continue

            ctrl_id = row["ctrl_id"]
            table_cible = row["table_cible"]
            type_controle = row["type_controle"]
            parametres = row["parametres"]

            try:
                # Récupérer la table cible
                if table_cible not in datasets:
                    continue

                df_target = datasets[table_cible]
                nb_lignes = len(df_target)

                # Exécuter le contrôle approprié
                mask_anomalies = self.controls.execute(
                    type_controle, df_target, row, datasets
                )

                nb_anomalies = mask_anomalies.sum()
                montant_anomalies = 0  # À calculer selon le contexte

                # Enregistrer le run
                run_id = f"run_{uuid4().hex[:8]}"
                runs.append({
                    "run_id": run_id,
                    "ctrl_id": ctrl_id,
                    "date_arrete": date_arrete,
                    "debut": self.run_timestamp,
                    "fin": datetime.now().isoformat(),
                    "statut": "OK" if nb_anomalies == 0 else "KO",
                    "nb_lignes_controlees": nb_lignes,
                    "nb_anomalies": nb_anomalies,
                    "montant_anomalies": montant_anomalies,
                    "version_moteur": "1.0"
                })

                # Enregistrer les anomalies
                if nb_anomalies > 0:
                    anomaly_rows = df_target[mask_anomalies]
                    for idx, anomaly_row in anomaly_rows.iterrows():
                        anomaly_id = f"anom_{uuid4().hex[:8]}"
                        cle_metier = str(anomaly_row.iloc[0])  # Première colonne comme clé

                        anomalies.append({
                            "anomaly_id": anomaly_id,
                            "run_id": run_id,
                            "ctrl_id": ctrl_id,
                            "table_cible": table_cible,
                            "cle_metier": cle_metier,
                            "champ": row["champ"],
                            "valeur_attendue": "",
                            "valeur_constatee": str(anomaly_row[row["champ"]]),
                            "ecart": "",
                            "statut": "OUVERT",
                            "famille_cause": type_controle,
                            "commentaire": f"Anomalie détectée par {ctrl_id}"
                        })

            except Exception as e:
                print(f"Erreur lors de l'exécution du contrôle {ctrl_id}: {e}")
                continue

        return pd.DataFrame(runs), pd.DataFrame(anomalies)
