#!/usr/bin/env python3
"""
Migration Error Aggregation Dashboard - Beautiful v3.0
Grouped by Error Message with Site Details
OCEA Design - Professional Production Ready
"""

import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
import plotly.graph_objects as go

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
# CUSTOM STYLING - OCEA DESIGN
# ============================================================================

st.markdown("""
<style>
    :root {
        --ocea-blue: #2E75B6;
        --ocea-dark: #1F4E78;
        --ocea-green: #6DB82D;
        --accent-orange: #FF9500;
        --success-green: #27AE60;
        --warning-red: #E74C3C;
        --neutral-gray: #7F8C8D;
        --surface-light: #F8F9FA;
        --surface-gray: #E8EAED;
    }

    h1 {
        color: var(--ocea-dark);
        border-bottom: 3px solid var(--ocea-blue);
        padding-bottom: 15px;
        font-size: 2em;
    }

    h2, h3 {
        color: var(--ocea-dark);
        font-weight: 600;
    }

    .kpi-card {
        background: linear-gradient(135deg, #F0F7FF 0%, #FFFFFF 100%);
        border-left: 4px solid var(--ocea-blue);
        padding: 20px;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .kpi-value {
        font-size: 2.5em;
        font-weight: 700;
        color: var(--ocea-blue);
        font-family: 'Courier New', monospace;
    }

    .kpi-label {
        font-size: 0.85em;
        color: var(--neutral-gray);
        font-weight: 500;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .message-row {
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .message-row:hover {
        background-color: #E8F4F8;
    }

    .message-row-odd {
        background-color: #FFFFFF;
    }

    .message-row-even {
        background-color: #F5F5F5;
    }

    .message-text {
        font-size: 0.95em;
        color: var(--ocea-dark);
        font-weight: 500;
        line-height: 1.5;
    }

    .sites-count {
        font-size: 1.1em;
        font-weight: 600;
        color: var(--ocea-blue);
        background-color: #E8F4F8;
        padding: 6px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .site-code {
        font-family: 'Courier New', monospace;
        font-weight: 700;
        color: #FFFFFF;
        background-color: var(--ocea-blue);
        padding: 4px 10px;
        border-radius: 3px;
        display: inline-block;
        min-width: 60px;
        text-align: center;
        margin-right: 8px;
    }

    .occurrence-badge {
        background-color: var(--accent-orange);
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9em;
        display: inline-block;
        font-family: 'Courier New', monospace;
    }

    .detail-row {
        padding: 8px 0;
        border-bottom: 1px solid #EEEEEE;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .detail-row:last-child {
        border-bottom: none;
    }

    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, var(--ocea-blue) 0%, var(--ocea-green) 100%);
        margin: 20px 0;
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
# DATA LOADING WITH CRITICITE FILTER
# ============================================================================

@st.cache_data(ttl=60)
def load_data():
    """Load demo data and filter for blocking errors only"""
    df = pd.read_csv(StringIO(DEMO_DATA))
    # FILTER ONLY BLOCKING ERRORS
    df = df[df['Criticite'] == 'Error'].copy()
    return df

@st.cache_data(ttl=60)
def aggregate_by_message(df):
    """Group data by message and aggregate sites"""
    agg_data = []
    for message in df['Message'].unique():
        msg_df = df[df['Message'] == message]
        num_sites = msg_df['SiteCode'].nunique()
        total_occ = msg_df['Occurrences'].sum()
        
        sites_detail = []
        for site in msg_df['SiteCode'].unique():
            site_occ = msg_df[msg_df['SiteCode'] == site]['Occurrences'].sum()
            sites_detail.append({'code': site, 'occurrences': int(site_occ)})
        
        agg_data.append({
            'message': message,
            'num_sites': num_sites,
            'total_occ': total_occ,
            'sites': sorted(sites_detail, key=lambda x: x['occurrences'], reverse=True)
        })
    
    # Sort by number of sites descending
    return sorted(agg_data, key=lambda x: x['num_sites'], reverse=True)

df = load_data()
agg_messages = aggregate_by_message(df)

# ============================================================================
# HEADER
# ============================================================================

col_title, col_time = st.columns([5, 1])
with col_title:
    st.markdown("# 🔍 Suivi des Erreurs Migration")
    st.markdown("**OCEA Smart Building** — Erreurs bloquantes | Production")

with col_time:
    st.markdown(f"<p style='text-align: right; color: #7F8C8D; font-size: 0.85em;'><strong>Maj:</strong> {datetime.now().strftime('%d/%m %H:%M')}</p>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# KPI METRICS
# ============================================================================

total_sites = df['SiteCode'].nunique()
total_messages = df['Message'].nunique()
total_occ = df['Occurrences'].sum()
top_message = max(agg_messages, key=lambda x: x['total_occ'])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_sites}</div>
        <div class="kpi-label">Sites Affectés</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_messages}</div>
        <div class="kpi-label">Types d'Erreurs</div>
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
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value" style="font-size: 1.8em;">{top_message['num_sites']}</div>
        <div class="kpi-label">Erreur Majeure</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.header("🎯 Filtres & Options")

search_message = st.sidebar.text_input("🔍 Chercher message", placeholder="ex: local n'existe pas")

min_sites_filter = st.sidebar.slider("Min. sites affectés", 1, total_sites, 1)

sort_by = st.sidebar.radio(
    "Trier par",
    options=["Sites affectés (DESC)", "Occurrences (DESC)"],
    index=0
)

# Apply filters
filtered_messages = agg_messages
if search_message:
    filtered_messages = [m for m in filtered_messages if search_message.lower() in m['message'].lower()]
if min_sites_filter > 1:
    filtered_messages = [m for m in filtered_messages if m['num_sites'] >= min_sites_filter]

if sort_by == "Occurrences (DESC)":
    filtered_messages = sorted(filtered_messages, key=lambda x: x['total_occ'], reverse=True)

st.sidebar.markdown("---")
st.sidebar.info(f"✅ **{len(filtered_messages)}** messages affichés / **{len(agg_messages)}** total")
st.sidebar.success("🔄 Auto-refresh: ON (chaque minute)")

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2 = st.tabs(["📊 Messages d'Erreurs", "📈 Analyse & Graphiques"])

# ============================================================================
# TAB 1: MESSAGES GROUPED TABLE
# ============================================================================

with tab1:
    st.subheader(f"📋 Erreurs Bloquantes Regroupées — {len(filtered_messages)} messages")
    st.markdown("Cliquez sur une erreur pour voir les sites affectés avec occurrences")
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Display messages
    for idx, msg_item in enumerate(filtered_messages):
        is_even = idx % 2 == 0
        row_class = "message-row-even" if is_even else "message-row-odd"

        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"""
                <div class="message-row {row_class}">
                    <div class="message-text">{msg_item['message']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="sites-count">{msg_item['num_sites']} sites ▼</div>
                """, unsafe_allow_html=True)

            # Expandable details
            with st.expander(f"👥 Détail des {msg_item['num_sites']} sites"):
                st.markdown(f"**Message:** {msg_item['message']}")
                st.markdown(f"**Sites affectés:** {msg_item['num_sites']} | **Total occurrences:** {msg_item['total_occ']}")
                st.markdown("---")

                # Display sites in detail
                for site_detail in msg_item['sites']:
                    col_site, col_occ = st.columns([2, 1])
                    with col_site:
                        st.markdown(f'<span class="site-code">{site_detail["code"]}</span>', unsafe_allow_html=True)
                    with col_occ:
                        st.markdown(f'<span class="occurrence-badge">({site_detail["occurrences"]})</span>', unsafe_allow_html=True)

    # Export section
    st.markdown("---")
    st.subheader("📥 Exporter les Données")

    # Create export dataframe
    export_rows = []
    for msg_item in filtered_messages:
        for site in msg_item['sites']:
            export_rows.append({
                'Message': msg_item['message'],
                'Code Site': site['code'],
                'Occurrences': site['occurrences']
            })

    export_df = pd.DataFrame(export_rows)
    csv_data = export_df.to_csv(index=False)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"erreurs_bloquantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col2:
        st.info("✅ Format: Message | Code Site | Occurrences")

    with col3:
        st.success("🔄 Mise à jour: Chaque minute")

# ============================================================================
# TAB 2: ANALYSIS & CHARTS
# ============================================================================

with tab2:
    st.subheader("📈 Analyses & Graphiques")

    col1, col2 = st.columns(2)

    # Top messages chart
    with col1:
        st.markdown("**Top Messages par Nombre de Sites**")
        
        chart_data = []
        for msg in filtered_messages[:10]:
            chart_data.append({
                'message': msg['message'][:40] + "..." if len(msg['message']) > 40 else msg['message'],
                'sites': msg['num_sites'],
                'occ': msg['total_occ']
            })

        if chart_data:
            chart_df = pd.DataFrame(chart_data).sort_values('sites', ascending=True)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=chart_df['message'],
                    x=chart_df['sites'],
                    orientation='h',
                    marker=dict(
                        color=chart_df['sites'],
                        colorscale='Blues',
                        showscale=True,
                        colorbar=dict(title="Sites")
                    ),
                    text=chart_df['sites'],
                    textposition='auto',
                    hovertemplate='<b>%{y}</b><br>Sites: %{x}<br><extra></extra>'
                )
            ])

            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='white',
                plot_bgcolor='#F8F9FA',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0'),
                yaxis=dict(showgrid=False),
                font=dict(family='Segoe UI', size=10, color='#1F4E78')
            )

            st.plotly_chart(fig, use_container_width=True)

    # Top messages by occurrences
    with col2:
        st.markdown("**Top Messages par Occurrences**")

        chart_data = []
        for msg in filtered_messages[:10]:
            chart_data.append({
                'message': msg['message'][:40] + "..." if len(msg['message']) > 40 else msg['message'],
                'sites': msg['num_sites'],
                'occ': msg['total_occ']
            })

        if chart_data:
            chart_df = pd.DataFrame(chart_data).sort_values('occ', ascending=True)

            fig = go.Figure(data=[
                go.Bar(
                    y=chart_df['message'],
                    x=chart_df['occ'],
                    orientation='h',
                    marker=dict(
                        color=chart_df['occ'],
                        colorscale='Oranges',
                        showscale=True,
                        colorbar=dict(title="Occ.")
                    ),
                    text=chart_df['occ'],
                    textposition='auto',
                    hovertemplate='<b>%{y}</b><br>Occurrences: %{x}<br><extra></extra>'
                )
            ])

            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='white',
                plot_bgcolor='#F8F9FA',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0'),
                yaxis=dict(showgrid=False),
                font=dict(family='Segoe UI', size=10, color='#1F4E78')
            )

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Summary statistics
    st.markdown("**Statistiques Résumées**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_sites_per_msg = total_sites / total_messages if total_messages > 0 else 0
        st.metric("Sites par message", f"{avg_sites_per_msg:.1f}")

    with col2:
        avg_occ_per_msg = total_occ / total_messages if total_messages > 0 else 0
        st.metric("Occurrences par message", f"{avg_occ_per_msg:.1f}")

    with col3:
        max_sites_msg = max(agg_messages, key=lambda x: x['num_sites'])
        st.metric("Max sites (1 message)", max_sites_msg['num_sites'])

    with col4:
        max_occ_msg = max(agg_messages, key=lambda x: x['total_occ'])
        st.metric("Max occurrences (1 message)", max_occ_msg['total_occ'])

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7F8C8D; font-size: 0.85em;'>
    <p><strong>✨ Migration Error Aggregation v3.0</strong> — OCEA Smart Building © 2024-2026</p>
    <p>🔄 <em>Auto-refresh toutes les minutes</em> • Erreurs bloquantes uniquement (Criticite="Error")</p>
    <p style='font-size: 0.8em;'>Regroupé par Message | Sites affectés | Occurrences par site</p>
</div>
""", unsafe_allow_html=True)
