#!/usr/bin/env python3
"""
Migration Error Aggregation Dashboard - Simplified Version
"""

import streamlit as st
import pandas as pd
from io import StringIO

# Page config (MUST be first)
st.set_page_config(page_title="Migration Errors", page_icon="🚀", layout="wide")

st.title("🚀 Migration Error Aggregation")
st.markdown("OCEA Smart Building - Suivi des erreurs de validation")
st.markdown("---")

# Demo data - SIMPLE CSV
DEMO_DATA = """Week,Scope,ErrorID,Message,NumSites,TotalOccurrences
2024-W33,Patrimoine - PDS Eau Froide,21104,Le local n'existe pas.,22,92
2024-W33,Valorisation - Répartition Ligne Frais,40810,Le montant doit être renseigné.,27,46
2024-W33,Exploitation - Période consommation,30115,Seuls les fluides eau froide eau chaude et CET peuvent faire partie d'une même PCC.,27,29
2024-W33,Patrimoine - PDS Accessoire,21303,Le compteur n'existe pas.,23,24
2024-W33,Valorisation - Répartition,40722,Le type de Gestion de Mutation ECS et Eau Chaude doivent être identiques.,9,23
2024-W33,Patrimoine - Echec Maintenance,21405,Le pds n'existe pas.,12,12
2024-W33,Patrimoine - PDS Eau Froide,21129,Le modèle de l'appareil renseigné est pour le fluide EC qui ne correspond pas au fluide du PDS (EF).,8,10
2024-W33,Exploitation - Période consommation,40017,Le traitement correspondant à la période de consommation est manquant.,7,7
2024-W33,Valorisation - Traitement,40019,Les périodes de chauffe ne doivent pas se chevaucher ou être contigüe.,7,12
2024-W33,Patrimoine - Pose RFC,20902,Impossible de réaliser une pose sur un pds sans radiateur déclaré.,7,9"""

# Load demo data
df = pd.read_csv(StringIO(DEMO_DATA))

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📍 Sites Affectés", "187", "-8 vs sem.")
with col2:
    st.metric("⚠️ Types d'Erreurs", "61", "stable")
with col3:
    st.metric("✅ Résolus", "12", "+2 vs sem.")

st.markdown("---")

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "📋 Détail", "📈 Historique"])

with tab1:
    st.subheader("Top erreurs par nombre de sites")
    df_sorted = df.sort_values('NumSites', ascending=False)

    # Chart
    st.bar_chart(df_sorted.set_index('Message')[['NumSites']])

    st.subheader("Erreurs par domaine")
    domain_count = df.groupby('Scope').size()
    st.bar_chart(domain_count)

with tab2:
    st.subheader("Tableau complet des erreurs")
    st.dataframe(df_sorted, use_container_width=True)

    # Export
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name="errors.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("Historique semaine par semaine")
    st.info("Données historiques: Retour en ligne après exécution du script complet")

    history_data = pd.DataFrame({
        'Semaine': ['2024-W30', '2024-W31', '2024-W32', '2024-W33'],
        'Sites Affectés': [245, 212, 195, 187],
        'Résolus': [0, 33, 17, 8]
    })
    st.dataframe(history_data, use_container_width=True)

    # Trend chart
    st.line_chart(history_data.set_index('Semaine')[['Sites Affectés']])

st.markdown("---")
st.markdown("✨ **Version démo** - Pour données réelles, exécuter: `python3 scripts/aggregate_errors.py`")
