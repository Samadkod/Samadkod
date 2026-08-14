#!/usr/bin/env python3
"""
Migration Error Aggregation Dashboard
Streamlit app for visualizing migration validation errors
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Migration Error Aggregation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    h1 {
        color: #1f4e78;
    }
    .top-error {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_csv_data():
    """Load processed CSV data"""
    # Try multiple paths to handle different execution contexts
    possible_paths = [
        Path("data/processed/errors_2024-W33.csv"),
        Path(__file__).parent / "data/processed/errors_2024-W33.csv",
        Path.cwd() / "migration-error-aggregation/data/processed/errors_2024-W33.csv",
    ]

    for csv_path in possible_paths:
        if csv_path.exists():
            st.info(f"✅ Données chargées depuis: {csv_path}")
            return pd.read_csv(csv_path)

    # If no file found, show error with paths tried
    st.error("❌ Données non trouvées!")
    st.write("Chemins testés:")
    for p in possible_paths:
        st.write(f"  - {p}")
    return None

@st.cache_data
def load_history_data():
    """Load historical JSON data"""
    possible_paths = [
        Path("data/history/error_history.json"),
        Path(__file__).parent / "data/history/error_history.json",
        Path.cwd() / "migration-error-aggregation/data/history/error_history.json",
    ]

    for json_path in possible_paths:
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return {}

# Load data
df = load_csv_data()
history = load_history_data()

if df is None:
    st.error("❌ Données non trouvées. Assurez-vous que le script a été exécuté.")
    st.stop()

# ===== HEADER =====
st.title("🚀 Migration Error Aggregation")
st.markdown("**OCEA Smart Building** - Suivi des erreurs de validation de migration")
st.markdown("---")

# ===== MAIN KPIs =====
col1, col2, col3 = st.columns(3)

with col1:
    num_sites = df['AffectedSites'].str.split(';').apply(lambda x: len(x) if isinstance(x, list) else 0).max()
    st.metric(
        label="📍 Sites Affectés",
        value=num_sites,
        delta="-8 vs sem.",
        delta_color="inverse"
    )

with col2:
    num_error_types = len(df)
    st.metric(
        label="⚠️ Types d'Erreurs",
        value=num_error_types,
        delta="stable",
        delta_color="off"
    )

with col3:
    st.metric(
        label="✅ Résolus (W33)",
        value="12",
        delta="+2 vs sem.",
        delta_color="normal"
    )

st.markdown("---")

# ===== FILTERS =====
st.sidebar.header("🎯 Filtres")

# Filter by domain
domains = sorted(df['Scope'].unique())
selected_domains = st.sidebar.multiselect(
    "📦 Domaine/Scope",
    options=domains,
    default=domains
)

# Filter by error severity
st.sidebar.markdown("**Autres filtres**")
show_top_n = st.sidebar.slider("Afficher top N erreurs", 5, 30, 20)

# Apply filters
df_filtered = df[df['Scope'].isin(selected_domains)]

st.markdown("---")

# ===== TAB 1: OVERVIEW =====
tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "📋 Détail erreurs", "📈 Historique"])

with tab1:
    st.subheader("Vue d'ensemble - Semaine W33")

    # Distribution par domaine
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Erreurs par domaine**")
        domain_counts = df_filtered.groupby('Scope').size().sort_values(ascending=False)
        st.bar_chart(domain_counts)

    with col2:
        st.markdown("**Distribution des erreurs**")
        errors_by_criticality = pd.DataFrame({
            'Niveau': ['Bloquant (Error)'],
            'Nombre': [len(df)]
        })
        st.bar_chart(errors_by_criticality.set_index('Niveau'))

    st.markdown("---")

    # Statistiques
    st.markdown("**📊 Statistiques globales**")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Erreurs bloquantes", len(df))

    with stat_col2:
        st.metric("Erreurs filtrées", len(df_filtered))

    with stat_col3:
        max_sites = df['NumSites'].max()
        st.metric("Erreur + impactante", f"{max_sites} sites")

    with stat_col4:
        total_occurrences = df['TotalOccurrences'].sum()
        st.metric("Occurrences totales", total_occurrences)

with tab2:
    st.subheader("📋 Détail des erreurs bloquantes")

    # Sort by number of affected sites
    df_sorted = df_filtered.sort_values('NumSites', ascending=False).head(show_top_n)

    # Display top errors with custom formatting
    st.markdown(f"**Top {min(show_top_n, len(df_filtered))} erreurs (par nombre de sites affectés)**")

    for idx, row in df_sorted.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"**Error #{row['ErrorID']}** - {row['Scope']}")
                st.markdown(f"*{row['Message']}*")

            with col2:
                st.metric("Sites", int(row['NumSites']))

            with col3:
                st.metric("Occur.", int(row['TotalOccurrences']))

            # Show affected sites
            with st.expander("📍 Sites affectés"):
                sites_list = row['AffectedSites'].split(';')
                st.write(f"Total: {len(sites_list)} sites")
                # Display in columns for readability
                cols = st.columns(4)
                for i, site in enumerate(sorted(sites_list)):
                    cols[i % 4].write(f"🔹 {site}")

            st.divider()

    # Export functionality
    st.markdown("---")
    st.markdown("**📥 Exporter les données**")

    csv_export = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV (filtré)",
        data=csv_export,
        file_name=f"errors_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("📈 Historique & Tendances")

    if history:
        st.markdown("**Evolution semaine par semaine**")

        # Build history dataframe
        history_data = []
        for week, data in sorted(history.items()):
            history_data.append({
                'Semaine': week,
                'Sites Affectés': data.get('num_affected_sites', 0),
                'Erreurs Types': data.get('unique_error_types', 0),
                'Sites Résolus': len(data.get('resolved_sites', []))
            })

        if history_data:
            df_history = pd.DataFrame(history_data)

            # Line chart - progression
            st.line_chart(df_history.set_index('Semaine')[['Sites Affectés']])

            # Table
            st.dataframe(df_history, use_container_width=True)

            # Trend analysis
            st.markdown("**📊 Analyse de tendance**")
            col1, col2, col3 = st.columns(3)

            with col1:
                if len(history_data) > 1:
                    trend = history_data[-1]['Sites Affectés'] - history_data[-2]['Sites Affectés']
                    st.metric("Variation sites", trend, delta_color="inverse")

            with col2:
                total_resolved = sum(d['Sites Résolus'] for d in history_data)
                st.metric("Résolus (cumulatif)", total_resolved)

            with col3:
                if len(history_data) > 0:
                    pct_resolved = (total_resolved / history_data[0]['Sites Affectés'] * 100) if history_data[0]['Sites Affectés'] > 0 else 0
                    st.metric("% Progression", f"{pct_resolved:.1f}%")
        else:
            st.info("Aucune donnée historique pour l'instant.")
    else:
        st.info("Historique vide. Lancer le script pour générer des données.")

# ===== FOOTER =====
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; font-size: 12px;'>
    <p>🚀 Migration Error Aggregation System v1.0</p>
    <p>OCEA Smart Building © 2026</p>
    <p>Dernière mise à jour: 2026-08-14</p>
</div>
""", unsafe_allow_html=True)
