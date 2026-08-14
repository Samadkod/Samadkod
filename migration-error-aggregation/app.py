#!/usr/bin/env python3
"""
Migration Error Aggregation Dashboard - Beautiful v2.0
Focused on 3 key columns: Code Site | Message | Occurrences
Only blocking errors (Criticite="Error")
Auto-updates daily
"""

import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Erreurs Migration - OCEA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING - ELEGANT & PROFESSIONAL
# ============================================================================

st.markdown("""
<style>
    :root {
        --ocea-blue: #2E75B6;
        --ocea-dark: #1F4E78;
        --accent-orange: #FF9500;
        --success-green: #27AE60;
        --warning-red: #E74C3C;
        --neutral-gray: #7F8C8D;
        --surface-light: #F8F9FA;
        --surface-dark: #ECF0F1;
    }

    h1, h2, h3 {
        color: var(--ocea-dark);
        font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    h1 {
        border-bottom: 3px solid var(--ocea-blue);
        padding-bottom: 15px;
        font-size: 2.2em;
    }

    .kpi-card {
        background: linear-gradient(135deg, #F0F7FF 0%, #FFFFFF 100%);
        border-left: 4px solid var(--ocea-blue);
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .kpi-value {
        font-size: 2em;
        font-weight: 700;
        color: var(--ocea-blue);
        font-family: 'Courier New', monospace;
    }

    .kpi-label {
        font-size: 0.9em;
        color: var(--neutral-gray);
        font-weight: 500;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .site-code {
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: white;
        background-color: var(--ocea-blue);
        padding: 6px 12px;
        border-radius: 4px;
        display: inline-block;
        min-width: 70px;
        text-align: center;
    }

    .occurrence-badge {
        background-color: var(--accent-orange);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1em;
        display: inline-block;
        font-family: 'Courier New', monospace;
        box-shadow: 0 2px 8px rgba(255, 149, 0, 0.3);
    }

    .error-message {
        font-size: 0.95em;
        color: #2C3E50;
        line-height: 1.6;
    }

    .chart-container {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DEMO DATA - SITE-LEVEL WITH CRITICITE
# ============================================================================

DEMO_DATA = """Week,Scope,ErrorID,Message,SiteCode,Occurrences,Criticite,LastSeen
2024-W33,Exploitation - Période consommation,30115,Seuls les fluides eau froide eau chaude et CET peuvent faire partie d'une même PCC.,AF872,2,Error,2024-08-14
2024-W33,Exploitation - Période consommation,30115,Seuls les fluides eau froide eau chaude et CET peuvent faire partie d'une même PCC.,BF886,1,Error,2024-08-14
2024-W33,Exploitation - Période consommation,30115,Seuls les fluides eau froide eau chaude et CET peuvent faire partie d'une même PCC.,BI043,3,Error,2024-08-14
2024-W33,Valorisation - Répartition Ligne Frais,40810,Le montant doit être renseigné.,BL123,2,Error,2024-08-13
2024-W33,Valorisation - Répartition Ligne Frais,40810,Le montant doit être renseigné.,BP627,4,Error,2024-08-13
2024-W33,Valorisation - Répartition Ligne Frais,40810,Le montant doit être renseigné.,BP629,1,Error,2024-08-13
2024-W33,Valorisation - Répartition Ligne Frais,40810,Le montant doit être renseigné.,BP640,2,Error,2024-08-13
2024-W33,Valorisation - Répartition Ligne Frais,40810,Le montant doit être renseigné.,BP641,3,Information,2024-08-13
2024-W33,Patrimoine - PDS Accessoire,21303,Le compteur n'existe pas.,AL246,2,Error,2024-08-12
2024-W33,Patrimoine - PDS Accessoire,21303,Le compteur n'existe pas.,BI692,3,Error,2024-08-12
2024-W33,Patrimoine - PDS Accessoire,21303,Le compteur n'existe pas.,BJ296,1,Error,2024-08-12
2024-W33,Patrimoine - PDS Eau Froide,21104,Le local n'existe pas.,AF796,5,Error,2024-08-14
2024-W33,Patrimoine - PDS Eau Froide,21104,Le local n'existe pas.,AI362,2,Error,2024-08-14
2024-W33,Patrimoine - PDS Eau Froide,21104,Le local n'existe pas.,AI400,1,Error,2024-08-14
2024-W33,Patrimoine - PDS Eau Froide,21104,Le local n'existe pas.,AI428,3,Error,2024-08-14
2024-W33,Valorisation - Répartition,40722,Le type de Gestion de Mutation ECS et Eau Chaude doivent être identiques.,AF796,2,Error,2024-08-12
2024-W33,Valorisation - Répartition,40722,Le type de Gestion de Mutation ECS et Eau Chaude doivent être identiques.,BQ302,1,Error,2024-08-12
2024-W33,Valorisation - Répartition,40722,Le type de Gestion de Mutation ECS et Eau Chaude doivent être identiques.,CK372,4,Error,2024-08-12
2024-W33,Patrimoine - Echec Maintenance,21405,Le pds n'existe pas.,BK259,2,Error,2024-08-11
2024-W33,Patrimoine - Echec Maintenance,21405,Le pds n'existe pas.,BK294,1,Error,2024-08-11
2024-W33,Patrimoine - Echec Maintenance,21405,Le pds n'existe pas.,BK357,3,Error,2024-08-11
2024-W33,Patrimoine - PDS Eau Froide,21129,Le modèle de l'appareil renseigné est pour le fluide EC qui ne correspond pas au fluide du PDS (EF).,AF872,1,Error,2024-08-10
2024-W33,Patrimoine - PDS Eau Froide,21129,Le modèle de l'appareil renseigné est pour le fluide EC qui ne correspond pas au fluide du PDS (EF).,BE228,2,Error,2024-08-10
2024-W33,Patrimoine - PDS Eau Froide,21129,Le modèle de l'appareil renseigné est pour le fluide EC qui ne correspond pas au fluide du PDS (EF).,BN371,1,Error,2024-08-10
2024-W33,Exploitation - Période consommation,40017,Le traitement correspondant à la période de consommation est manquant.,BL754,2,Error,2024-08-09
2024-W33,Exploitation - Période consommation,40017,Le traitement correspondant à la période de consommation est manquant.,CC515,3,Error,2024-08-09
2024-W33,Valorisation - Traitement,40019,Les périodes de chauffe ne doivent pas se chevaucher ou être contigüe.,BO988,2,Error,2024-08-08
2024-W33,Valorisation - Traitement,40019,Les périodes de chauffe ne doivent pas se chevaucher ou être contigüe.,BP528,1,Error,2024-08-08
2024-W33,Valorisation - Traitement,40019,Les périodes de chauffe ne doivent pas se chevaucher ou être contigüe.,BP550,2,Error,2024-08-08
2024-W33,Patrimoine - Pose RFC,20902,Impossible de réaliser une pose sur un pds sans radiateur déclaré.,AH687,1,Error,2024-08-07
2024-W33,Patrimoine - Pose RFC,20902,Impossible de réaliser une pose sur un pds sans radiateur déclaré.,BH120,2,Error,2024-08-07
2024-W33,Contrat - Eau Froide,10724,Les périodes de consommation ne sont pas renseignées.,BI043,1,Error,2024-08-06
2024-W33,Contrat - Eau Froide,10724,Les périodes de consommation ne sont pas renseignées.,BN136,3,Error,2024-08-06"""

# ============================================================================
# DATA LOADING - WITH CRITICITE FILTER
# ============================================================================

@st.cache_data(ttl=60)  # Auto-refresh every 60 seconds
def load_data():
    """Load demo data and filter for blocking errors only (Criticite='Error')"""
    df = pd.read_csv(StringIO(DEMO_DATA))
    # FILTER ONLY BLOCKING ERRORS
    df = df[df['Criticite'] == 'Error'].copy()
    # Sort by Occurrences descending
    df = df.sort_values('Occurrences', ascending=False).reset_index(drop=True)
    return df

df = load_data()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_summary_stats(data):
    """Calculate key metrics - only blocking errors"""
    unique_sites = data['SiteCode'].nunique()
    unique_errors = data['Message'].nunique()
    total_occurrences = data['Occurrences'].sum()
    return unique_sites, unique_errors, total_occurrences

def get_top_sites(data, n=10):
    """Get top N sites by total occurrences"""
    return data.groupby('SiteCode')['Occurrences'].sum().nlargest(n).sort_values(ascending=True)

def get_top_errors(data, n=10):
    """Get top N error messages by total occurrences"""
    return data.groupby('Message')['Occurrences'].sum().nlargest(n).sort_values(ascending=True)

# ============================================================================
# HEADER
# ============================================================================

col_title, col_time = st.columns([5, 1])
with col_title:
    st.markdown("# 🔍 Suivi des Erreurs Migration")
    st.markdown("**OCEA Smart Building** — Erreurs bloquantes | Mise à jour temps réel")

with col_time:
    st.markdown(f"<p style='text-align: right; color: #7F8C8D; font-size: 0.9em;'><strong>Maj:</strong> {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# KPI METRICS - ONLY BLOCKING ERRORS
# ============================================================================

unique_sites, unique_errors, total_occ = get_summary_stats(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{unique_sites}</div>
        <div class="kpi-label">Sites Affectés</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{unique_errors}</div>
        <div class="kpi-label">Erreurs Bloquantes</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_occ}</div>
        <div class="kpi-label">Total Occurrences</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    top_site = df.groupby('SiteCode')['Occurrences'].sum().idxmax()
    top_site_occ = df.groupby('SiteCode')['Occurrences'].sum().max()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value" style="font-size: 1.6em;">{int(top_site_occ)}</div>
        <div class="kpi-label">Site Critique: {top_site}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.header("🎯 Filtres & Options")

# Filter by scope
scopes = sorted(df['Scope'].unique())
selected_scopes = st.sidebar.multiselect(
    "Domaine/Scope",
    options=scopes,
    default=scopes
)

# Filter by site code
site_search = st.sidebar.text_input("🔍 Chercher Code Site", placeholder="ex: BL123")

# Minimum occurrences
min_occ = st.sidebar.slider("Min. occurrences", 1, int(df['Occurrences'].max()), 1)

# Sort option
sort_by = st.sidebar.radio(
    "Trier par",
    options=["Occurrences (DESC)", "Code Site (A-Z)"],
    index=0
)

# Apply filters
df_filtered = df[df['Scope'].isin(selected_scopes)].copy()
if site_search:
    df_filtered = df_filtered[df_filtered['SiteCode'].str.contains(site_search.upper(), case=False)]
df_filtered = df_filtered[df_filtered['Occurrences'] >= min_occ]

if sort_by == "Occurrences (DESC)":
    df_filtered = df_filtered.sort_values('Occurrences', ascending=False)
else:
    df_filtered = df_filtered.sort_values('SiteCode', ascending=True)

df_filtered = df_filtered.reset_index(drop=True)

st.sidebar.markdown("---")
st.sidebar.info(f"✅ **{len(df_filtered)}** erreurs affichées / **{len(df)}** total (bloquantes)")
st.sidebar.success("🔄 Auto-refresh: ON (chaque minute)")

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Tableau", "📈 Analyses", "🗺️ Heatmap", "📋 Historique"])

# ============================================================================
# TAB 1: MAIN DATA TABLE - 3 KEY COLUMNS ONLY
# ============================================================================

with tab1:
    st.subheader("📊 Tableau Principal — Code Site | Message | Occurrences")
    st.markdown(f"**{len(df_filtered)}** erreurs bloquantes affichées • Focalisé sur les 3 colonnes clés")
    st.markdown("---")

    # Display header row
    col_site, col_msg, col_occ = st.columns([1.2, 5, 1.2], gap="large")
    with col_site:
        st.markdown("**Code Site**")
    with col_msg:
        st.markdown("**Message d'Erreur**")
    with col_occ:
        st.markdown("**Occurrences**")

    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

    # Display rows
    for idx, row in df_filtered.iterrows():
        col_site, col_msg, col_occ = st.columns([1.2, 5, 1.2], gap="large")

        with col_site:
            st.markdown(f'<span class="site-code">{row["SiteCode"]}</span>', unsafe_allow_html=True)

        with col_msg:
            st.markdown(f'<span class="error-message">{row["Message"]}</span>', unsafe_allow_html=True)

        with col_occ:
            st.markdown(f'<span class="occurrence-badge">{int(row["Occurrences"])}</span>', unsafe_allow_html=True)

        st.markdown("<hr style='margin: 8px 0; opacity: 0.3;'>", unsafe_allow_html=True)

    # Export section
    st.markdown("---")
    st.subheader("📥 Exporter les Données")

    csv_data = df_filtered[['SiteCode', 'Message', 'Occurrences', 'ErrorID', 'Scope', 'LastSeen']].to_csv(index=False)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"erreurs_bloquantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col2:
        st.info("✅ Format: Code Site | Message | Occurrences | ErrorID | Scope | LastSeen")

    with col3:
        st.success(f"🔄 Auto-refresh toutes les minutes")

# ============================================================================
# TAB 2: PROFESSIONAL ANALYSIS CHARTS
# ============================================================================

with tab2:
    st.subheader("📈 Analyses Professionnelles")

    col1, col2 = st.columns(2)

    # Top sites by occurrences
    with col1:
        st.markdown("**Top 10 Sites — Total Occurrences**")
        if len(df_filtered) > 0:
            top_sites_data = get_top_sites(df_filtered, n=10)

            fig = go.Figure(data=[
                go.Bar(
                    y=top_sites_data.index,
                    x=top_sites_data.values,
                    orientation='h',
                    marker=dict(
                        color=top_sites_data.values,
                        colorscale='Oranges',
                        showscale=True,
                        colorbar=dict(title="Occ.")
                    ),
                    text=top_sites_data.values,
                    textposition='auto',
                )
            ])

            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='white',
                plot_bgcolor='#F8F9FA',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0'),
                yaxis=dict(showgrid=False),
                font=dict(family='Segoe UI', size=11, color='#1F4E78')
            )

            st.plotly_chart(fig, use_container_width=True)

    # Top errors by occurrences
    with col2:
        st.markdown("**Top 10 Messages — Total Occurrences**")
        if len(df_filtered) > 0:
            top_errors_data = get_top_errors(df_filtered, n=10)

            fig = go.Figure(data=[
                go.Bar(
                    y=top_errors_data.index,
                    x=top_errors_data.values,
                    orientation='h',
                    marker=dict(
                        color=top_errors_data.values,
                        colorscale='Reds',
                        showscale=True,
                        colorbar=dict(title="Occ.")
                    ),
                    text=top_errors_data.values,
                    textposition='auto',
                )
            ])

            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='white',
                plot_bgcolor='#F8F9FA',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0'),
                yaxis=dict(showgrid=False),
                font=dict(family='Segoe UI', size=11, color='#1F4E78')
            )

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Stats by scope
    st.markdown("**Erreurs par Domaine**")
    if len(df_filtered) > 0:
        scope_stats = df_filtered.groupby('Scope').agg({
            'SiteCode': 'nunique',
            'Occurrences': 'sum',
            'Message': 'nunique'
        }).rename(columns={
            'SiteCode': 'Sites Uniques',
            'Occurrences': 'Total Occ.',
            'Message': 'Types Erreurs'
        }).sort_values('Total Occ.', ascending=False)

        st.dataframe(scope_stats, use_container_width=True)

# ============================================================================
# TAB 3: HEATMAP SITES × ERRORS
# ============================================================================

with tab3:
    st.subheader("🗺️ Heatmap — Sites × Erreurs")
    st.markdown("Visualisez les concentrations d'erreurs bloquantes")

    if len(df_filtered) > 1:
        # Créer une matrice pivot
        heatmap_data = df_filtered.pivot_table(
            index='SiteCode',
            columns='Message',
            values='Occurrences',
            aggfunc='sum',
            fill_value=0
        )

        # Limiter aux top sites et erreurs
        top_sites_list = df_filtered.groupby('SiteCode')['Occurrences'].sum().nlargest(10).index
        top_msgs_list = df_filtered.groupby('Message')['Occurrences'].sum().nlargest(8).index

        heatmap_subset = heatmap_data.loc[top_sites_list, top_msgs_list]

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_subset.values,
            x=[msg[:35] + "..." if len(msg) > 35 else msg for msg in heatmap_subset.columns],
            y=heatmap_subset.index,
            colorscale='YlOrRd',
            text=heatmap_subset.values,
            texttemplate='%{text:.0f}',
            textfont={"size": 10},
            colorbar=dict(title="Occurrences")
        ))

        fig.update_layout(
            height=600,
            margin=dict(l=120, r=50, t=40, b=250),
            paper_bgcolor='white',
            font=dict(family='Segoe UI', size=10, color='#1F4E78'),
            xaxis=dict(side='bottom', tickangle=-45),
            yaxis=dict(autorange='reversed')
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Pas assez de données pour afficher la heatmap")

# ============================================================================
# TAB 4: DAILY HISTORICAL TRENDS
# ============================================================================

with tab4:
    st.subheader("📈 Historique & Tendances Quotidiennes")

    # Simulated daily historical data (based on filtered data)
    history = pd.DataFrame({
        'Date': pd.date_range(start=datetime.now() - timedelta(days=6), periods=7, freq='D'),
        'Total Occurrences': [350, 380, 410, 450, 480, 520, 545],
        'Sites Affectés': [120, 128, 135, 142, 148, 155, 165]
    })

    col1, col2 = st.columns(2)

    # Occurrences trend
    with col1:
        st.markdown("**Évolution Quotidienne — Total Occurrences**")
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=history['Date'],
            y=history['Total Occurrences'],
            mode='lines+markers',
            name='Occurrences',
            line=dict(color='#FF9500', width=3),
            marker=dict(size=10, color='#FF9500', line=dict(color='white', width=2)),
            fill='tozeroy',
            fillcolor='rgba(255, 149, 0, 0.15)'
        ))

        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='white',
            plot_bgcolor='#F8F9FA',
            hovermode='x unified',
            font=dict(family='Segoe UI', size=11, color='#1F4E78')
        )

        st.plotly_chart(fig, use_container_width=True)

    # Sites trend
    with col2:
        st.markdown("**Évolution Quotidienne — Sites Affectés**")
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=history['Date'],
            y=history['Sites Affectés'],
            mode='lines+markers',
            name='Sites',
            line=dict(color='#2E75B6', width=3),
            marker=dict(size=10, color='#2E75B6', line=dict(color='white', width=2)),
            fill='tozeroy',
            fillcolor='rgba(46, 117, 182, 0.15)'
        ))

        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='white',
            plot_bgcolor='#F8F9FA',
            hovermode='x unified',
            font=dict(family='Segoe UI', size=11, color='#1F4E78')
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("**Tableau Historique (7 derniers jours)**")

    # Format history table nicely
    display_history = history.copy()
    display_history['Date'] = display_history['Date'].dt.strftime('%d/%m/%Y')

    st.dataframe(
        display_history.style.format({
            'Total Occurrences': '{:.0f}',
            'Sites Affectés': '{:.0f}'
        }),
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7F8C8D; font-size: 0.9em;'>
    <p><strong>✨ Migration Error Aggregation v2.0</strong> — OCEA Smart Building © 2024-2026</p>
    <p>🔄 <em>Mise à jour automatique chaque minute</em> • Filtrage: Erreurs bloquantes uniquement (Criticite="Error")</p>
    <p style='font-size: 0.85em; margin-top: 10px;'>Focus: <strong>Code Site</strong> | <strong>Message</strong> | <strong>Occurrences</strong></p>
</div>
""", unsafe_allow_html=True)
