"""
Cartographie & lignage des flux de données.

Décrit le parcours des données depuis les systèmes sources jusqu'aux QRT
Solvabilité 2, en passant par la zone de contrôle QDD. Sert de support à la
gouvernance et à la traçabilité demandée en audit.

Le graphe est renvoyé sous forme de nœuds + arêtes, exploitable par Graphviz.
"""

from __future__ import annotations

# (id, libellé, type de couche)
NOEUDS = [
    ("src_prod", "Système Production\n(contrats)", "source"),
    ("src_sin", "Système Sinistres", "source"),
    ("src_tiers", "Référentiel Tiers\n(clients/SIRET)", "source"),
    ("ext", "Extraction ODBC\n(SAS/SQL)", "ingestion"),
    ("stg_clients", "STG Clients", "staging"),
    ("stg_contrats", "STG Contrats", "staging"),
    ("stg_sinistres", "STG Sinistres", "staging"),
    ("qdd", "Dispositif QDD\n(contrôles qualité)", "controle"),
    ("dict", "Dictionnaire\nde données", "gouvernance"),
    ("fiab", "Traitements de\nfiabilisation", "transformation"),
    ("dm_act", "Datamart Actuariat", "datamart"),
    ("prov", "Provisions techniques\n(Best Estimate)", "calcul"),
    ("qrt", "QRT / Reporting S2\n(ACPR)", "reporting"),
    ("bi", "Restitution BI\n(Qlik Sense)", "restitution"),
]

# (source, cible)
ARETES = [
    ("src_prod", "ext"),
    ("src_sin", "ext"),
    ("src_tiers", "ext"),
    ("ext", "stg_clients"),
    ("ext", "stg_contrats"),
    ("ext", "stg_sinistres"),
    ("stg_clients", "qdd"),
    ("stg_contrats", "qdd"),
    ("stg_sinistres", "qdd"),
    ("dict", "qdd"),
    ("qdd", "fiab"),
    ("fiab", "dm_act"),
    ("dm_act", "prov"),
    ("prov", "qrt"),
    ("dm_act", "bi"),
    ("qdd", "bi"),
]

COULEURS = {
    "source": "#c7d2fe",
    "ingestion": "#bfdbfe",
    "staging": "#a5f3fc",
    "controle": "#fca5a5",
    "gouvernance": "#fcd34d",
    "transformation": "#bbf7d0",
    "datamart": "#86efac",
    "calcul": "#93c5fd",
    "reporting": "#f9a8d4",
    "restitution": "#ddd6fe",
}


def graphe_dot() -> str:
    """Renvoie une description Graphviz DOT du lignage."""
    lignes = [
        "digraph lineage {",
        '  rankdir=LR;',
        '  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10];',
        '  edge [color="#64748b"];',
    ]
    for nid, label, couche in NOEUDS:
        couleur = COULEURS.get(couche, "#e5e7eb")
        lignes.append(f'  {nid} [label="{label}" fillcolor="{couleur}"];')
    for src, dst in ARETES:
        lignes.append(f"  {src} -> {dst};")
    lignes.append("}")
    return "\n".join(lignes)
