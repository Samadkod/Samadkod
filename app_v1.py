"""
Sentinel QDD-S2 V1 — Moteur Générique Piloté par Métadonnées
=============================================================

Version 1 refactorisée utilisant le moteur générique d'exécution des contrôles
piloté entièrement par le registre des contrôles (métadonnées).

Lancement local :  streamlit run app_v1.py
"""

from __future__ import annotations

from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engine.control_engine import ControlEngine
from src.data_generator import generer_jeu_donnees

st.set_page_config(
    page_title="Sentinel QDD-S2 V1",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS pour tabs colorées
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 25px;
    border: 2px solid #1f77b4;
}

.stTabs [data-baseweb="tab"] {
    background-color: #ffffff;
    border: 2px solid #1f77b4;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    font-weight: 700;
    color: #1f77b4;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] [data-baseweb="tab"] {
    background-color: #1f77b4;
    color: white;
    border: 2px solid #0f3d7f;
    box-shadow: 0 6px 12px rgba(31, 119, 180, 0.35);
}
</style>
""", unsafe_allow_html=True)

# ========= SIDEBAR CONTROLS =========
st.sidebar.markdown("## ⚙️ Configuration")
date_arrete = st.sidebar.date_input(
    "Date d'arrêté",
    value=pd.Timestamp.now(),
    help="Date de référence pour l'exécution des contrôles"
)
date_arrete_str = date_arrete.strftime("%Y-%m-%d")

nb_clients = st.sidebar.slider(
    "Nombre de clients",
    min_value=10,
    max_value=500,
    value=100,
    step=10
)

nb_contrats = st.sidebar.slider(
    "Nombre de contrats",
    min_value=20,
    max_value=2000,
    value=500,
    step=50
)

nb_sinistres = st.sidebar.slider(
    "Nombre de sinistres",
    min_value=5,
    max_value=1000,
    value=200,
    step=20
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Seed Reproductibilité")
seed = st.sidebar.number_input(
    "Seed (pour reproductibilité)",
    min_value=1,
    max_value=10000,
    value=42
)

# ========= HEADER =========
st.markdown("# 🛡️ Sentinel QDD-S2 V1")
st.markdown("""
**Moteur générique piloté par métadonnées** — Contrôles d'assurance Solvabilité 2
configurables sans code. Les contrôles sont définis dans le registre CSV (metadata/control_registry.csv)
et exécutés dynamiquement selon leur type et paramètres.
""")

# ========= EXÉCUTION MOTEUR =========
st.markdown("---")
st.markdown("## 🚀 Exécution du Moteur")

with st.spinner("⏳ Génération des données synthétiques..."):
    rng = __import__("numpy").random.default_rng(seed)
    datasets = generer_jeu_donnees(
        nb_clients=nb_clients,
        nb_contrats=nb_contrats,
        nb_sinistres=nb_sinistres,
        seed=seed
    )

st.success("✅ Données générées avec succès")

with st.spinner("⏳ Exécution des contrôles..."):
    engine = ControlEngine(metadata_dir="metadata")
    control_runs_df, anomalies_df = engine.run(datasets, date_arrete=date_arrete_str)

st.success("✅ Contrôles exécutés avec succès")

# ========= TABS =========
tab_resultats, tab_anomalies, tab_registre, tab_dimensions, tab_piste_audit, tab_donnees = st.tabs([
    "📈 Résultats Contrôles",
    "🔴 Anomalies Détectées",
    "📋 Registre Contrôles",
    "📊 Score par Dimension",
    "🔐 Piste d'Audit",
    "🗂️ Données Source"
])

# ========= TAB 1: Résultats Contrôles =========
with tab_resultats:
    st.markdown("### Résumé d'Exécution des Contrôles")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_controles = len(control_runs_df)
        st.metric("📋 Contrôles Exécutés", total_controles)

    with col2:
        controles_ok = len(control_runs_df[control_runs_df["statut"] == "OK"])
        st.metric("✅ Contrôles OK", controles_ok)

    with col3:
        controles_ko = len(control_runs_df[control_runs_df["statut"] == "KO"])
        st.metric("❌ Contrôles KO", controles_ko)

    with col4:
        taux_conformite = 100 * controles_ok / total_controles if total_controles > 0 else 0
        st.metric("✔️ Taux Conformité", f"{taux_conformite:.1f}%")

    st.markdown("---")
    st.markdown("### Détail des Contrôles")
    st.dataframe(
        control_runs_df[["ctrl_id", "statut", "nb_lignes_controlees", "nb_anomalies"]],
        use_container_width=True,
        hide_index=True
    )

    # Graphique statuts
    statut_counts = control_runs_df["statut"].value_counts()
    fig = px.bar(
        x=statut_counts.index,
        y=statut_counts.values,
        labels={"x": "Statut", "y": "Nombre"},
        title="Distribution des Statuts",
        color=statut_counts.index,
        color_discrete_map={"OK": "#00cc96", "KO": "#ff5151"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ========= TAB 2: Anomalies Détectées =========
with tab_anomalies:
    st.markdown("### Anomalies Identifiées par Contrôle")

    if len(anomalies_df) == 0:
        st.success("✅ Aucune anomalie détectée — Qualité des données optimale!")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🔴 Total Anomalies", len(anomalies_df))

        with col2:
            st.metric("📊 Tables Affectées", anomalies_df["table_cible"].nunique())

        with col3:
            st.metric("🏷️ Contrôles Touchés", anomalies_df["ctrl_id"].nunique())

        st.markdown("---")
        st.dataframe(anomalies_df, use_container_width=True, hide_index=True)

        # Graphique anomalies par contrôle
        anom_by_ctrl = anomalies_df["ctrl_id"].value_counts()
        fig = px.bar(
            x=anom_by_ctrl.index,
            y=anom_by_ctrl.values,
            labels={"x": "Contrôle", "y": "Nombre d'Anomalies"},
            title="Anomalies par Contrôle",
            color_discrete_sequence=["#ff5151"]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ========= TAB 3: Registre Contrôles =========
with tab_registre:
    st.markdown("### Registre des Contrôles (Métadonnées)")
    st.markdown("""
    Le registre définit tous les contrôles exécutables. Chaque ligne = 1 contrôle.
    Pour ajouter un contrôle : éditez le CSV `metadata/control_registry.csv` (aucun code requis).
    """)

    registry = engine.registry[["ctrl_id", "libelle", "table_cible", "type_controle", "criticite", "actif"]]
    st.dataframe(registry, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Types de Contrôles Supportés:")
    control_types = {
        "non_nul": "Détecte valeurs NULL/NaN",
        "unique": "Détecte doublons de clé",
        "plage": "Valeurs hors plage min/max",
        "referentiel": "Valeur hors domaine autorisé",
        "format": "Erreur de type/format",
        "coherence_dates": "Ordre logique de dates",
        "reconciliation": "Écart relatif toléré",
        "variation_n_n1": "Variation volumétrique"
    }
    for ctype, desc in control_types.items():
        st.write(f"- **{ctype}**: {desc}")

# ========= TAB 4: Score par Dimension =========
with tab_dimensions:
    st.markdown("### Score de Conformité par Dimension")

    # Regrouper par dimension extraite du ctrl_id
    control_runs_df["dimension"] = control_runs_df["ctrl_id"].str.split("_").str[0]

    dimension_stats = []
    for dim in control_runs_df["dimension"].unique():
        dim_controls = control_runs_df[control_runs_df["dimension"] == dim]
        total = len(dim_controls)
        ok = len(dim_controls[dim_controls["statut"] == "OK"])
        ratio = 100 * ok / total if total > 0 else 0
        dimension_stats.append({
            "Dimension": dim,
            "Contrôles": total,
            "Conformes": ok,
            "Taux (%)": ratio
        })

    dim_df = pd.DataFrame(dimension_stats).sort_values("Taux (%)")
    st.dataframe(dim_df, use_container_width=True, hide_index=True)

    # Graphique
    fig = px.bar(
        dim_df,
        x="Dimension",
        y="Taux (%)",
        labels={"Taux (%)": "Taux Conformité (%)"},
        title="Conformité par Dimension Réglementaire",
        color="Taux (%)",
        color_continuous_scale=["#ff5151", "#ffa500", "#00cc96"]
    )
    st.plotly_chart(fig, use_container_width=True)

# ========= TAB 5: Piste d'Audit =========
with tab_piste_audit:
    st.markdown("### Piste d'Audit (Traçabilité ACPR/CAC)")
    st.markdown("""
    Enregistrement horodaté complet pour justification auprès du régulateur.
    """)

    audit_trail = control_runs_df[[
        "run_id", "ctrl_id", "date_arrete", "statut",
        "nb_lignes_controlees", "nb_anomalies", "version_moteur"
    ]].copy()

    st.dataframe(audit_trail, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Télécharger la piste d'audit")
    csv = audit_trail.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name=f"piste_audit_{date_arrete_str}.csv",
        mime="text/csv"
    )

# ========= TAB 6: Données Source =========
with tab_donnees:
    st.markdown("### Aperçu des Données Source")

    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["👥 Clients", "📄 Contrats", "🚨 Sinistres"])

    with sub_tab1:
        st.write(f"**{len(datasets['clients'])} clients générés**")
        st.dataframe(datasets["clients"].head(20), use_container_width=True, hide_index=True)

    with sub_tab2:
        st.write(f"**{len(datasets['contrats'])} contrats générés**")
        st.dataframe(datasets["contrats"].head(20), use_container_width=True, hide_index=True)

    with sub_tab3:
        st.write(f"**{len(datasets['sinistres'])} sinistres générés**")
        st.dataframe(datasets["sinistres"].head(20), use_container_width=True, hide_index=True)

# ========= FOOTER =========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Sentinel QDD-S2 V1</strong> | Moteur Générique Piloté par Métadonnées</p>
    <p>Données 100% fictives | BTP Assurance | Solvabilité 2</p>
</div>
""", unsafe_allow_html=True)
