"""Tests du moteur de contrôles QDD."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from engine.control_engine import ControlEngine


@pytest.fixture
def control_engine():
    """Crée une instance du moteur."""
    return ControlEngine()


@pytest.fixture
def sample_datasets():
    """Crée des datasets d'exemple pour les tests."""
    contrats = pd.DataFrame({
        "police": ["P001", "P002", "P003", "P001"],  # P001 dupliquée
        "assure": ["Entreprise A", "Entreprise B", None, "Entreprise D"],  # P003 assure = None
        "date_effet": ["2024-01-01", "2024-01-15", "2024-02-01", "2024-01-01"],
        "date_resiliation": ["2025-01-01", "2025-01-15", None, "2025-01-01"],
        "branche": ["RC_DECENNALE", "RC_PRO", "BRANCHE_INVALIDE", "RC_DECENNALE"],  # P003 branche invalide
        "prime_emise": [5000.0, 3000.0, -1000.0, 5000.0],  # P003 montant négatif
        "taux_reassurance": [0.15, 0.2, 1.5, 0.1],  # P003 taux > 1
        "lob_s2": ["M1_BTP_DMG", "M2_BTP_RC", "LOB_INVALIDE", "M1_BTP_DMG"],
        "segment": ["BTP", "BTP", "SEGMENT_INVALIDE", "BTP"],
        "prime_cedee": [750.0, 600.0, None, 500.0],
    })

    sinistres = pd.DataFrame({
        "sinistre_id": ["S001", "S002", "S003", "S004", "S005"],
        "police": ["P001", "P002", "P003", "P001", "P002"],
        "date_survenance": ["2023-06-01", "2023-07-15", None, "2024-03-01", "2024-01-15"],
        "date_declaration": ["2023-06-05", "2023-07-10", "2024-02-01", "2024-03-05", "2024-01-10"],  # S002 décl < surv
        "date_clôture": ["2023-12-01", "2024-01-15", "2024-06-01", None, "2024-05-01"],
        "date_reouverture": [None, None, "2024-05-15", None, "2024-06-01"],  # S005 reouve > clôture
        "montant_brut": [50000.0, 75000.0, -5000.0, 100000.0, 30000.0],  # S003 montant négatif
        "montant_net": [40000.0, 60000.0, 0.0, 80000.0, 25000.0],
        "statut": ["RESOLU", "RESOLU", "OUVERT", "OUVERT", "REOUVERT"],
        "montant_resolution": [40000.0, 60000.0, 0.0, 0.0, 25000.0],
    })

    primes = pd.DataFrame({
        "police": ["P001", "P001", "P002", "P002", "P003"],
        "montant_emis": [5000.0, 5000.0, 3000.0, 3000.0, 2000.0],
        "montant_acquis": [4500.0, 5000.0, 2700.0, 3000.0, 1800.0],
        "exercice": [2023, 2024, 2023, 2024, 2024],
    })

    provisions = pd.DataFrame({
        "police": ["P001", "P002", "P003"],
        "montant_provision": [10000.0, 15000.0, 5000.0],
        "date_arrete": ["2024-12-31", "2024-12-31", "2024-12-31"],
    })

    return {
        "contrats": contrats,
        "sinistres": sinistres,
        "primes": primes,
        "provisions": provisions,
    }


class TestControlEngine:
    """Tests du moteur de contrôles."""

    def test_control_engine_initialization(self, control_engine):
        """Vérifie l'initialisation du moteur."""
        assert control_engine is not None
        assert len(control_engine.registry) > 0

    def test_non_nul_detection(self, control_engine, sample_datasets):
        """Teste la détection des valeurs NULL."""
        runs, anomalies = control_engine.run(sample_datasets)

        # Vérifier que le contrôle EXHAUS_01 a trouvé des anomalies
        exhaus_runs = runs[runs["ctrl_id"] == "EXHAUS_01"]
        assert len(exhaus_runs) > 0
        assert exhaus_runs.iloc[0]["nb_anomalies"] >= 2  # Au moins P003 (assure=NULL) et d'autres

    def test_unique_detection(self, control_engine, sample_datasets):
        """Teste la détection des doublons."""
        runs, anomalies = control_engine.run(sample_datasets)

        # Vérifier que le contrôle EXACT_01 a trouvé les doublons
        unique_runs = runs[runs["ctrl_id"] == "EXACT_01"]
        assert len(unique_runs) > 0
        assert unique_runs.iloc[0]["nb_anomalies"] >= 2  # P001 dupliquée

    def test_plage_detection(self, control_engine, sample_datasets):
        """Teste la détection des valeurs hors plage."""
        runs, anomalies = control_engine.run(sample_datasets)

        # Vérifier que le contrôle EXACT_02 (montants négatifs) a trouvé des anomalies
        plage_runs = runs[runs["ctrl_id"] == "EXACT_02"]
        assert len(plage_runs) > 0
        assert plage_runs.iloc[0]["nb_anomalies"] >= 1  # P003 prime_emise négative

    def test_referentiel_detection(self, control_engine, sample_datasets):
        """Teste la détection des valeurs hors référentiel."""
        runs, anomalies = control_engine.run(sample_datasets)

        # Vérifier que le contrôle VALID_01 (branches) a trouvé des anomalies
        ref_runs = runs[runs["ctrl_id"] == "VALID_01"]
        assert len(ref_runs) > 0
        assert ref_runs.iloc[0]["nb_anomalies"] >= 1  # P003 branche invalide

    def test_coherence_dates_detection(self, control_engine, sample_datasets):
        """Teste la détection des incohérences de dates."""
        runs, anomalies = control_engine.run(sample_datasets)

        # Vérifier que le contrôle COHER_01 a trouvé les incohérences
        coher_runs = runs[runs["ctrl_id"] == "COHER_01"]
        assert len(coher_runs) > 0
        assert coher_runs.iloc[0]["nb_anomalies"] >= 1  # S002 declaration < survenance

    def test_reconciliation_detection(self, control_engine, sample_datasets):
        """Teste la détection des écarts de réconciliation."""
        runs, anomalies = control_engine.run(sample_datasets)

        # Vérifier que le contrôle COHER_06 (réconciliation primes) a été exécuté
        recon_runs = runs[runs["ctrl_id"] == "COHER_06"]
        assert len(recon_runs) > 0

    def test_run_output_structure(self, control_engine, sample_datasets):
        """Vérifie la structure des outputs (runs et anomalies)."""
        runs, anomalies = control_engine.run(sample_datasets)

        # Vérifier que runs a les bonnes colonnes
        assert "run_id" in runs.columns
        assert "ctrl_id" in runs.columns
        assert "date_arrete" in runs.columns
        assert "statut" in runs.columns
        assert "nb_anomalies" in runs.columns

        # Vérifier que anomalies a les bonnes colonnes
        if len(anomalies) > 0:
            assert "anomaly_id" in anomalies.columns
            assert "run_id" in anomalies.columns
            assert "cle_metier" in anomalies.columns

    def test_multiple_runs(self, control_engine, sample_datasets):
        """Teste que le moteur peut exécuter plusieurs fois."""
        runs1, anom1 = control_engine.run(sample_datasets, "2024-12-31")
        runs2, anom2 = control_engine.run(sample_datasets, "2025-01-31")

        # Vérifier que les deux runs ont produit des résultats
        assert len(runs1) > 0
        assert len(runs2) > 0

        # Vérifier que les dates d'arrêté sont différentes
        assert runs1.iloc[0]["date_arrete"] != runs2.iloc[0]["date_arrete"]
