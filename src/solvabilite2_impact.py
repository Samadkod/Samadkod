"""
Calculs d'impact Solvabilité 2 — Provisions techniques et SCR/MCR.

Module pour simuler l'impact des anomalies détectées sur :
- Les provisions techniques (Best Estimate)
- Le SCR (Solvency Capital Requirement)
- Le MCR (Minimum Capital Requirement)
- Les rapports QRT et l'ACPR
"""

from __future__ import annotations

import pandas as pd


def calculer_provisions_techniques(datasets: dict, resultats: list) -> dict:
    """
    Simule le calcul des provisions techniques (Best Estimate) en présence d'anomalies.

    En réalité, le Best Estimate = valeur attendue des flux futurs.
    Ici, on simule un calcul simplifié basé sur :
    - Montants sinistrés historiques
    - Taux de sinistralité par contrat
    - Facteur d'incertitude lié à la qualité des données

    Returns:
        dict avec best_estimate (sans anomalies), best_estimate_degrade (avec anomalies)
    """
    sinistres = datasets["sinistres"]
    contrats = datasets["contrats"]

    # Montant total exposé (somme des valeurs assurées)
    if "montant_assure" in contrats.columns:
        exposition_totale = contrats["montant_assure"].sum()
    else:
        exposition_totale = len(contrats) * 100_000  # par défaut

    # Montant sinistré
    if "montant_reserve" in sinistres.columns:
        montant_sinistre_total = sinistres["montant_reserve"].sum()
    else:
        montant_sinistre_total = len(sinistres) * 5_000

    # Taux sinistralité
    taux_sinistralite = montant_sinistre_total / max(exposition_totale, 1)

    # Best Estimate = provisions pour sinistres futurs
    # Simplifié: Best Estimate = Taux sinistralité × Exposition totale × Facteur prudentiel
    best_estimate_theorique = exposition_totale * taux_sinistralite * 1.15  # +15% facteur prud

    # Détection du nombre d'anomalies par type
    anomalies_bloquantes = sum(1 for r in resultats if r.controle.criticite == "Bloquant" and r.nb_anomalies > 0)
    anomalies_majeures = sum(1 for r in resultats if r.controle.criticite == "Majeur" and r.nb_anomalies > 0)

    # Facteur de dégradation: plus d'anomalies = moins fiable
    # Hypothèse: chaque anomalie bloquante = -5%, chaque majeure = -2%
    facteur_degradation = 1.0 - (anomalies_bloquantes * 0.05 + anomalies_majeures * 0.02)
    facteur_degradation = max(facteur_degradation, 0.5)  # Minimum 50%

    best_estimate_degrade = best_estimate_theorique * facteur_degradation

    # Écart estimé = impact financier de la mauvaise qualité
    impact_financier = best_estimate_theorique - best_estimate_degrade

    return {
        "best_estimate_ideal": best_estimate_theorique,
        "best_estimate_degrade": best_estimate_degrade,
        "impact_financier": impact_financier,
        "ratio_fiabilite": facteur_degradation * 100,
        "exposition_totale": exposition_totale,
        "montant_sinistre": montant_sinistre_total,
        "taux_sinistralite": taux_sinistralite * 100,
    }


def calculer_scr_mcr(provisions: dict) -> dict:
    """
    Simule le calcul du SCR et MCR basés sur les provisions.

    Solvabilité 2 impose :
    - SCR = capital requis pour survivre à une crise majeure (99.5% confiance)
    - MCR = seuil minimum absolu (très strict)

    Simplifié:
    - SCR ≈ Best Estimate × 20% (exemple)
    - MCR ≈ SCR × 25%
    """
    best_estimate = provisions["best_estimate_degrade"]

    # SCR : capital de solvabilité requis
    # Hypothèse simplifiée: 20% du Best Estimate (en vrai, c'est bcp plus complexe)
    scr = best_estimate * 0.20

    # MCR : capital minimum requis
    # Hypothèse: 25% du SCR
    mcr = scr * 0.25

    # Simulation des fonds propres disponibles
    # Hypothèse: fonds propres = 30% de l'exposition
    fonds_propres = provisions["exposition_totale"] * 0.30

    # Ratios de solvabilité
    ratio_scr = (fonds_propres / scr) * 100 if scr > 0 else 100
    ratio_mcr = (fonds_propres / mcr) * 100 if mcr > 0 else 100

    # Zones de conformité
    conformite_scr = "✅ Conforme" if ratio_scr >= 100 else "⚠️ Attention"
    conformite_mcr = "✅ Conforme" if ratio_mcr >= 100 else "🚫 Non conforme"

    return {
        "scr": scr,
        "mcr": mcr,
        "fonds_propres": fonds_propres,
        "ratio_scr": ratio_scr,
        "ratio_mcr": ratio_mcr,
        "conformite_scr": conformite_scr,
        "conformite_mcr": conformite_mcr,
        "statut_s2": "✅ Solvable" if ratio_mcr >= 100 else "🚫 Insolvable",
    }


def generer_rapport_s2(datasets: dict, resultats: list, rapport: pd.DataFrame) -> dict:
    """
    Génère un rapport synthétique Solvabilité 2 montrant :
    - Impact des anomalies détectées sur les provisions
    - Conformité réglementaire (SCR, MCR)
    - Recommandations
    """
    provisions = calculer_provisions_techniques(datasets, resultats)
    solvabilite = calculer_scr_mcr(provisions)

    # Évaluation du risque QDD
    nb_anomalies_bloquantes = sum(1 for r in resultats if r.controle.criticite == "Bloquant" and r.nb_anomalies > 0)
    nb_anomalies_total = sum(r.nb_anomalies for r in resultats)

    risque_qdd = "🟢 Faible" if nb_anomalies_bloquantes == 0 and nb_anomalies_total < 10 else \
                 "🟡 Modéré" if nb_anomalies_bloquantes == 0 else \
                 "🔴 Élevé"

    return {
        "provisions": provisions,
        "solvabilite": solvabilite,
        "nb_anomalies_bloquantes": nb_anomalies_bloquantes,
        "nb_anomalies_total": nb_anomalies_total,
        "risque_qdd": risque_qdd,
        "recommandations": generer_recommandations(resultats, nb_anomalies_bloquantes),
    }


def generer_recommandations(resultats: list, nb_anomalies_bloquantes: int) -> list:
    """Génère des recommandations basées sur l'état des contrôles."""
    recs = []

    if nb_anomalies_bloquantes > 0:
        recs.append({
            "severite": "🚫 Critique",
            "action": "Résoudre immédiatement les anomalies bloquantes",
            "detail": f"{nb_anomalies_bloquantes} contrôle(s) bloquant(s) détecté(s). Les données ne sont pas éligibles aux calculs S2."
        })

    # Détection par type
    anomalies_par_dim = {}
    for r in resultats:
        if r.nb_anomalies > 0:
            dim = r.controle.dimension
            anomalies_par_dim[dim] = anomalies_par_dim.get(dim, 0) + r.nb_anomalies

    if "Unicité" in anomalies_par_dim:
        recs.append({
            "severite": "⚠️ Important",
            "action": "Déduplication — Implémenter un référentiel tiers",
            "detail": f"{anomalies_par_dim['Unicité']} doublon(s) détecté(s). Impact: provisions surestimées."
        })

    if "Exactitude" in anomalies_par_dim:
        recs.append({
            "severite": "⚠️ Important",
            "action": "Audit des montants — Évaluation des règles métier",
            "detail": f"{anomalies_par_dim['Exactitude']} erreur(s) d'exactitude. Impact: Best Estimate inexact."
        })

    if "Exhaustivité" in anomalies_par_dim:
        recs.append({
            "severite": "📋 Mineur",
            "action": "Complétude — Enrichir les données manquantes",
            "detail": f"{anomalies_par_dim['Exhaustivité']} champ(s) manquant(s). Impact: reporting ACPR incomplet."
        })

    if not recs:
        recs.append({
            "severite": "✅ Excellent",
            "action": "Aucune action requise",
            "detail": "Toutes les anomalies sont mineures ou maîtrisées. Données éligibles S2."
        })

    return recs


def formatter_montant(montant: float) -> str:
    """Formate un montant en euros de manière lisible."""
    if montant >= 1_000_000:
        return f"€ {montant / 1_000_000:.1f}M"
    elif montant >= 1_000:
        return f"€ {montant / 1_000:.0f}k"
    else:
        return f"€ {montant:.0f}"
