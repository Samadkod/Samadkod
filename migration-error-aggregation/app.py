#!/usr/bin/env python3
"""
Migration Error Aggregation Dashboard - Production Version
Professional dashboard for tracking and managing migration validation errors
"""

import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Migration Error Aggregation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
<style>
    h1 {
        color: #1f4e78;
        border-bottom: 3px solid #2E75B6;
        padding-bottom: 10px;
    }

    .error-row {
        background-color: #f8f9fa;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #2E75B6;
        border-radius: 5px;
    }

    .site-badge {
        display: inline-block;
        background-color: #e8f4f8;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 20px;
        font-size: 12px;
        border: 1px solid #2E75B6;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DEMO DATA
# ============================================================================

DEMO_DATA = """Week,Scope,ErrorID,Message,NumSites,TotalOccurrences,AffectedSites
2024-W33,Exploitation - Période consommation,30115,Seuls les fluides eau froide eau chaude et CET peuvent faire partie d'une même PCC.,27,29,AF872;BF886;BI043;BL754;BN136;BO289;BP218;BP583;BP933;CB808;CC515;CD101;CE338;CF070;CF113;CF229;CG745;CG797;CI595;CI722;CI996;CJ057;CL135;CO721;CQ837;CV600;CZ671
2024-W33,Valorisation - Répartition Ligne Frais,40810,Le montant doit être renseigné.,27,46,BL123;BP627;BP629;BP640;BP641;BP642;BP792;BP795;BQ301;BQ302;BQ547;BR436;BZ871;CC515;CD312;CE338;CG015;CG800;CH068;CH497;CI916;CJ138;CJ395;CJ433;CJ717;CO527;CP678
2024-W33,Patrimoine - PDS Accessoire,21303,Le compteur n'existe pas.,23,24,AL246;BI692;BJ296;BK256;BM096;BN136;BN370;BO913;BP038;BP267;BV917;CA008;CB454;CG346;CG401;CH817;CI163;CI957;CI996;CJ370;CL869;CQ151;CZ842
2024-W33,Patrimoine - PDS Eau Froide,21104,Le local n'existe pas.,22,92,AF796;AI362;AI400;AI428;AI888;AJ235;BI431;BJ407;BK219;BK970;BL652;BR436;CA654;CB680;CD914;CE663;CJ395;CK193;CK194;CL841;CM005;CR387
2024-W33,Valorisation - Répartition,40722,Le type de Gestion de Mutation ECS et Eau Chaude doivent être identiques.,9,23,AF796;BQ302;CK372;CM372;CT454;CT668;CT792;CW250;DB676
2024-W33,Patrimoine - Echec Maintenance,21405,Le pds n'existe pas.,12,12,BK259;BK294;BK357;BM061;BM070;BM093;BM497;BM591;BO289;BO959;BQ323;BQ404
2024-W33,Patrimoine - PDS Eau Froide,21129,Le modèle de l'appareil renseigné est pour le fluide EC qui ne correspond pas au fluide du PDS (EF).,8,10,AF872;BE228;BN371;BN455;BP477;BP523;BQ599;CB062
2024-W33,Exploitation - Période consommation,40017,Le traitement correspondant à la période de consommation est manquant.,7,7,BL754;CC515;CF070;CG745;CO721;CS021;CS494
2024-W33,Valorisation - Traitement,40019,Les périodes de chauffe ne doivent pas se chevaucher ou être contigüe.,7,12,BO988;BP528;BP550;CO047;CT987;DA015;DB676
2024-W33,Patrimoine - Pose RFC,20902,Impossible de réaliser une pose sur un pds sans radiateur déclaré.,7,9,AH687;BH120;BK207;BM161;BN189;BO848;BP182
2024-W33,Contrat - Eau Froide,10724,Les périodes de consommation ne sont pas renseignées.,5,5,BI043;BN136;CF113;CI722;CI996
2024-W33,Patrimoine - PDS Evènements (Codes Obs),23008,Le PDS EF possède une dépose définitive du compteur,4,4,BK123;BK124;BM364;CI618
2024-W33,Patrimoine - PDS Evènements (Codes Obs),23204,Le PDS virtuel n'est ni un RFC ni un PAS.,3,6,BK130;CC448;CC503
2024-W33,Exploitation - Exercice Comptable,30114,Les périodes de consommation doivent être consécutives.,3,6,BL754;BP218;CC515
2024-W33,Contrat - Eau Froide,10702,Le modele d'appareil préconisé doit être renseigné.,3,3,BP071;CK372;CL035
2024-W33,Contrat - Eau Froide,10727,En présence d'une prestation de relève il doit exister au moins un device actif.,3,3,BP071;CK372;CL035
2024-W33,Valorisation - Consommation Local,40014,Une consommation doit être fournie pour le scope Traitement Local Fluide Distribution.,2,16,BP188;CB062
2024-W33,Patrimoine - PDS Eau Chaude,21004,Le local n'existe pas.,4,11,BR436;CB680;CD914;CR387
2024-W33,Exploitation - Période consommation,30116,Il doit exister une prestation de relève pour les fluides présents dans une PCC.,5,42,BK404;BP973;CB794;CD682;CI535
2024-W33,Patrimoine - PDS Général,21360,Le PDS général doit avoir au moins un compteur historique dans l'onglet S_PdsGenerauxCompteurs.,1,1,BK130"""

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load demo data and sort by number of sites"""
    df = pd.read_csv(StringIO(DEMO_DATA))
    df = df.sort_values('NumSites', ascending=False).reset_index(drop=True)
    return df

df = load_data()

# ============================================================================
# HEADER
# ============================================================================

st.title("🚀 Migration Error Aggregation")
st.markdown("**OCEA Smart Building** - Système de suivi professionnel des erreurs de validation de migration")
st.markdown("Semaine: W33 | Dernière mise à jour: 2026-08-14")
st.markdown("---")

# ============================================================================
# KPI METRICS
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📍 Sites Affectés", "187", "-8 vs sem.")
with col2:
    st.metric("⚠️ Types d'Erreurs", len(df), "-")
with col3:
    st.metric("🔄 Occurrences", df['TotalOccurrences'].sum(), "Total")
with col4:
    st.metric("✅ Résolus", "12", "+2")

st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.header("🎯 Filtres")

domains = sorted(df['Scope'].unique())
selected_domains = st.sidebar.multiselect("Domaine", options=domains, default=domains)

min_sites = st.sidebar.slider("Min. sites affectés", 1, int(df['NumSites'].max()), 1)

search = st.sidebar.text_input("🔍 Rechercher message")

max_show = st.sidebar.slider("Erreurs à afficher", 5, len(df), 20)

# Apply filters
df_filtered = df[df['Scope'].isin(selected_domains)]
df_filtered = df_filtered[df_filtered['NumSites'] >= min_sites]
if search:
    df_filtered = df_filtered[df_filtered['Message'].str.contains(search, case=False)]
df_filtered = df_filtered.head(max_show)

st.sidebar.markdown("---")
st.sidebar.info(f"✅ {len(df_filtered)} erreurs affichées")

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["📋 Erreurs", "📊 Analyse", "📈 Historique"])

# ============================================================================
# TAB 1: DETAILED ERRORS
# ============================================================================

with tab1:
    st.subheader(f"📋 Détail des erreurs ({len(df_filtered)} affichées)")
    st.markdown("Triées par nombre de sites affectés (décroissant)")
    st.markdown("---")

    for idx, row in df_filtered.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

        with col1:
            st.markdown(f"**Error {row['ErrorID']}** - {row['Scope']}")

        with col2:
            st.markdown(f"📍 **{int(row['NumSites'])} sites**")

        with col3:
            st.markdown(f"🔄 {int(row['TotalOccurrences'])}")

        with col4:
            if row['NumSites'] >= 20:
                st.markdown("🔴")
            elif row['NumSites'] >= 10:
                st.markdown("🟠")
            else:
                st.markdown("🟡")

        st.markdown(f"`{row['Message']}`")

        # Affected sites
        with st.expander(f"👥 {int(row['NumSites'])} sites concernés"):
            sites = sorted(row['AffectedSites'].split(';'))
            cols = st.columns(5)
            for i, site in enumerate(sites):
                cols[i % 5].write(site)

        st.divider()

    # Export
    st.subheader("📥 Exporter")

    csv_data = df_filtered[['ErrorID', 'Scope', 'Message', 'NumSites', 'TotalOccurrences', 'AffectedSites']].to_csv(index=False)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 CSV",
            data=csv_data,
            file_name=f"errors_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with col2:
        st.info("✅ Excel export: Upgradeable à la demande")

# ============================================================================
# TAB 2: ANALYSIS
# ============================================================================

with tab2:
    st.subheader("📊 Analyse")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Erreurs par domaine**")
        domain_count = df_filtered.groupby('Scope').size().sort_values(ascending=False)
        st.bar_chart(domain_count)

    with col2:
        st.markdown("**Sites affectés par erreur**")
        top_errors = df_filtered.nlargest(10, 'NumSites')[['ErrorID', 'NumSites']].set_index('ErrorID')
        st.bar_chart(top_errors)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sites moyenne", f"{df_filtered['NumSites'].mean():.1f}")
    with col2:
        st.metric("Max sites", int(df_filtered['NumSites'].max()))
    with col3:
        st.metric("Total sites", int(df_filtered['NumSites'].sum()))

# ============================================================================
# TAB 3: HISTORICAL DATA
# ============================================================================

with tab3:
    st.subheader("📈 Historique")

    history = pd.DataFrame({
        'Semaine': ['W30', 'W31', 'W32', 'W33'],
        'Sites Affectés': [245, 212, 195, 187],
        'Erreurs Types': [68, 65, 62, 61],
        'Résolus': [0, 33, 17, 8]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.line_chart(history.set_index('Semaine')[['Sites Affectés']])

    with col2:
        st.bar_chart(history.set_index('Semaine')[['Résolus']])

    st.dataframe(history, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("✨ **Migration Error Aggregation v2.0** - OCEA Smart Building © 2026")
