"""
Sentinel QDD-S2 — Dispositif Qualité des Données Solvabilité 2
==============================================================

Prototype d'un dispositif de Qualité des Données (QDD) alimentant les
calculs et reportings Solvabilité 2. Matérialise les livrables de gouvernance
attendus : dictionnaire de données, cartographie/lignage des flux, contrôles
qualité, reporting de qualité et piste d'audit.

Lancement local :  streamlit run app.py
"""

from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_dictionary import dictionnaire_df
from src.data_generator import generer_jeu_donnees
from src.lineage import graphe_dot
from src.quality_engine import (
    anomalies_completes,
    executer_controles,
    piste_audit,
    rapport_detaille,
    score_global,
    scorecard_dimension,
)
from src.solvabilite2_impact import (
    calculer_provisions_techniques,
    calculer_scr_mcr,
    formatter_montant,
    generer_rapport_s2,
)

st.set_page_config(
    page_title="Sentinel QDD-S2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Données (mises en cache)
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def charger_donnees(n_clients, n_contrats, n_sinistres, seed, avec_anomalies):
    return generer_jeu_donnees(
        n_clients=n_clients,
        n_contrats=n_contrats,
        n_sinistres=n_sinistres,
        seed=seed,
        avec_anomalies=avec_anomalies,
    )


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


# --------------------------------------------------------------------------- #
# Sidebar — paramétrage
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("## 🛡️ Sentinel QDD-S2")
    st.caption("Dispositif Qualité des Données · Solvabilité 2")
    st.divider()
    st.markdown("### Paramètres du jeu de données")
    n_contrats = st.slider("Nombre de contrats", 500, 5000, 2000, step=250)
    n_sinistres = st.slider("Nombre de sinistres", 200, 3000, 900, step=100)
    n_clients = st.slider("Nombre de clients", 200, 2000, 800, step=100)
    avec_anomalies = st.toggle("Injecter des anomalies", value=True,
                               help="Simule des données amont dégradées à fiabiliser.")
    seed = st.number_input("Graine aléatoire", value=42, step=1)
    st.divider()
    st.caption("Données 100 % synthétiques — aucune donnée réelle.")

datasets = charger_donnees(n_clients, n_contrats, n_sinistres, seed, avec_anomalies)
resultats = executer_controles(datasets)
rapport = rapport_detaille(resultats)
scorecard = scorecard_dimension(resultats)
score = score_global(resultats)

# Impact Solvabilité 2
rapport_s2 = generer_rapport_s2(datasets, resultats, rapport)
provisions = rapport_s2["provisions"]
solvabilite = rapport_s2["solvabilite"]

# --------------------------------------------------------------------------- #
# En-tête + KPI
# --------------------------------------------------------------------------- #
st.title("🛡️ Dispositif Qualité des Données — Solvabilité 2")
st.markdown(
    "**Chaîne de fiabilisation** des données alimentant les provisions techniques, "
    "le Best Estimate, et les rapports QRT. Contrôles structurés sur les dimensions réglementaires "
    "**EIOPA** (Exhaustivité · Exactitude · Cohérence · Unicité · Intégrité). "
    "Contexte : Assurance BTP (RC, Décennale, Flotte)."
)

total_anomalies = int(rapport["Anomalies"].sum())
nb_bloquants = int(
    rapport[(rapport["Criticité"] == "Bloquant") & (rapport["Statut"] == "KO")].shape[0]
)
nb_ctrl_ko = int((rapport["Statut"] == "KO").sum())

# KPIs Qualité
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Score QDD", f"{score} %", help="Taux de conformité global pondéré par criticité.")
c2.metric("Contrôles exécutés", len(resultats), help=f"Dimension QDD : {', '.join(sorted(rapport['Dimension'].unique()))}")
c3.metric("Contrôles KO", nb_ctrl_ko, delta=f"-{nb_ctrl_ko}" if nb_ctrl_ko else "✅",
          delta_color="inverse")
c4.metric("Anomalies détectées", f"{total_anomalies:,}".replace(",", " "))
c5.metric(f"{rapport_s2['risque_qdd']}", "Risque QDD",
          help="Évaluation du risque associé aux anomalies détectées.")

st.divider()

# KPIs Solvabilité 2
st.subheader("📊 Impact Solvabilité 2")
col_s2_1, col_s2_2, col_s2_3, col_s2_4 = st.columns(4)

with col_s2_1:
    st.metric(
        "Best Estimate",
        formatter_montant(provisions["best_estimate_degrade"]),
        delta=f"{formatter_montant(-provisions['impact_financier'])} (ajusté pour qualité)",
        delta_color="inverse",
        help="Provisions techniques actualisées en fonction de la qualité des données."
    )

with col_s2_2:
    st.metric(
        "Ratio SCR",
        f"{solvabilite['ratio_scr']:.1f} %",
        delta="Conforme" if solvabilite['ratio_scr'] >= 100 else "Non conforme",
        delta_color="off" if solvabilite['ratio_scr'] >= 100 else "inverse",
        help="Capital de solvabilité requis : doit être ≥ 100%."
    )

with col_s2_3:
    st.metric(
        "Ratio MCR",
        f"{solvabilite['ratio_mcr']:.1f} %",
        delta="Conforme" if solvabilite['ratio_mcr'] >= 100 else "ALERTE",
        delta_color="off" if solvabilite['ratio_mcr'] >= 100 else "inverse",
        help="Minimum Capital Requirement : seuil critique."
    )

with col_s2_4:
    statut = solvabilite['statut_s2']
    st.metric(
        "Statut S2",
        statut.split()[0],  # ✅ ou 🚫
        delta=statut.split()[1] if len(statut.split()) > 1 else "",
        help="État global de solvabilité de l'organisme."
    )

if nb_bloquants:
    st.error(
        f"🚫 **{nb_bloquants} contrôle(s) bloquant(s) en échec** — "
        "Les données ne sont **PAS** éligibles aux calculs S2 en l'état. Action urgente requise."
    )
else:
    st.success(
        f"✅ **Aucun contrôle bloquant** — Données éligibles S2. "
        f"Fiabilité : {provisions['ratio_fiabilite']:.1f} %"
    )

st.divider()

# --------------------------------------------------------------------------- #
# Onglets
# --------------------------------------------------------------------------- #
tab_synth, tab_s2, tab_ctrl, tab_anom, tab_dict, tab_lin, tab_audit = st.tabs(
    [
        "📊 Synthèse qualité",
        "💰 Solvabilité 2 — Impact",
        "✅ Contrôles",
        "🔎 Anomalies",
        "📖 Dictionnaire",
        "🗺️ Cartographie & lignage",
        "🧾 Piste d'audit",
    ]
)

# ---- Synthèse qualité ---- #
with tab_synth:
    col_g, col_d = st.columns([1, 1])

    with col_g:
        st.subheader("Conformité par dimension réglementaire")
        fig = px.bar(
            scorecard.sort_values("Taux conformité (%)"),
            x="Taux conformité (%)",
            y="Dimension",
            orientation="h",
            text="Taux conformité (%)",
            color="Taux conformité (%)",
            color_continuous_scale=["#dc2626", "#f59e0b", "#16a34a"],
            range_color=[90, 100],
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_range=[90, 101],
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Répartition des anomalies par criticité")
        anom_par_crit = (
            rapport.groupby("Criticité")["Anomalies"].sum().reset_index()
        )
        ordre = {"Bloquant": 0, "Majeur": 1, "Mineur": 2}
        anom_par_crit = anom_par_crit.sort_values(
            "Criticité", key=lambda s: s.map(ordre)
        )
        fig2 = px.pie(
            anom_par_crit,
            names="Criticité",
            values="Anomalies",
            hole=0.55,
            color="Criticité",
            color_discrete_map={
                "Bloquant": "#dc2626",
                "Majeur": "#f59e0b",
                "Mineur": "#3b82f6",
            },
        )
        fig2.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Volumétrie du périmètre contrôlé")
    vol = pd.DataFrame(
        {
            "Table": ["Clients", "Contrats", "Sinistres"],
            "Lignes": [
                len(datasets["clients"]),
                len(datasets["contrats"]),
                len(datasets["sinistres"]),
            ],
        }
    )
    st.dataframe(vol, use_container_width=True, hide_index=True)

# ---- Solvabilité 2 — Impact ---- #
with tab_s2:
    st.subheader("💰 Impact des anomalies QDD sur Solvabilité 2")
    st.caption(
        "La qualité des données impacte directement les provisions techniques et le ratio de solvabilité. "
        "Cette section montre l'effet financier des anomalies détectées."
    )

    # Row 1: Provisions techniques
    st.markdown("#### Provisions Techniques (Best Estimate)")
    prov_col1, prov_col2 = st.columns(2)

    with prov_col1:
        st.markdown("**Scénario : Données sans anomalies**")
        st.info(f"Best Estimate : {formatter_montant(provisions['best_estimate_ideal'])}\n\n"
                f"Exposition totale : {formatter_montant(provisions['exposition_totale'])}\n\n"
                f"Montant sinistré : {formatter_montant(provisions['montant_sinistre'])}")

    with prov_col2:
        st.markdown("**Scénario : Avec anomalies détectées**")
        delta_val = provisions['impact_financier']
        delta_pct = (delta_val / provisions['best_estimate_ideal'] * 100) if provisions['best_estimate_ideal'] > 0 else 0
        st.warning(f"Best Estimate : {formatter_montant(provisions['best_estimate_degrade'])}\n\n"
                   f"**Impact financier : -{formatter_montant(delta_val)}** (-{delta_pct:.1f} %)\n\n"
                   f"Fiabilité données : {provisions['ratio_fiabilite']:.1f} %")

    st.divider()

    # Row 2: SCR vs MCR
    st.markdown("#### Exigences de Capital Solvabilité 2")
    scr_col1, scr_col2, scr_col3 = st.columns(3)

    with scr_col1:
        st.markdown("**📊 SCR (Solvency Capital Requirement)**")
        fig_scr = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=solvabilite['ratio_scr'],
                title="Ratio SCR (%)",
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 150]},
                    "bar": {"color": "#16a34a" if solvabilite['ratio_scr'] >= 100 else "#dc2626"},
                    "steps": [
                        {"range": [0, 100], "color": "#fee2e2"},
                        {"range": [100, 150], "color": "#dcfce7"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 100,
                    },
                },
                delta={"reference": 100, "suffix": " vs cible"},
            )
        )
        fig_scr.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_scr, use_container_width=True)
        st.caption(f"Capital requis : {formatter_montant(solvabilite['scr'])}")

    with scr_col2:
        st.markdown("**💎 MCR (Minimum Capital Requirement)**")
        fig_mcr = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=solvabilite['ratio_mcr'],
                title="Ratio MCR (%)",
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 150]},
                    "bar": {"color": "#16a34a" if solvabilite['ratio_mcr'] >= 100 else "#dc2626"},
                    "steps": [
                        {"range": [0, 100], "color": "#fee2e2"},
                        {"range": [100, 150], "color": "#dcfce7"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 100,
                    },
                },
                delta={"reference": 100, "suffix": " vs minimum"},
            )
        )
        fig_mcr.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_mcr, use_container_width=True)
        st.caption(f"Minimum requis : {formatter_montant(solvabilite['mcr'])}")

    with scr_col3:
        st.markdown("**💼 Fonds Propres Disponibles**")
        fig_fp = go.Figure(data=[
            go.Bar(name="Fonds Propres", x=["Disponible"], y=[solvabilite['fonds_propres']], marker_color="#3b82f6"),
            go.Bar(name="SCR", x=["Disponible"], y=[solvabilite['scr']], marker_color="#f59e0b"),
            go.Bar(name="MCR", x=["Disponible"], y=[solvabilite['mcr']], marker_color="#dc2626"),
        ])
        fig_fp.update_layout(
            barmode="group",
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(x=0, y=1),
            yaxis_title="Montant (€)",
        )
        st.plotly_chart(fig_fp, use_container_width=True)
        st.caption(f"Fonds propres : {formatter_montant(solvabilite['fonds_propres'])}")

    st.divider()

    # Row 3: Recommandations
    st.markdown("#### 📋 Recommandations Actions")
    recs = rapport_s2["recommandations"]

    for rec in recs:
        with st.expander(f"{rec['severite']} — {rec['action']}"):
            st.write(rec['detail'])

# ---- Contrôles ---- #
with tab_ctrl:
    st.subheader("Registre des contrôles qualité")
    st.caption(
        "Chaque contrôle est déclaratif et rattaché à une dimension réglementaire "
        "et à une criticité. Le taux de conformité conditionne l'éligibilité S2."
    )

    fcol1, fcol2, fcol3 = st.columns(3)
    dim_sel = fcol1.multiselect("Dimension", sorted(rapport["Dimension"].unique()))
    crit_sel = fcol2.multiselect("Criticité", ["Bloquant", "Majeur", "Mineur"])
    statut_sel = fcol3.multiselect("Statut", ["OK", "KO"])

    vue = rapport.copy()
    if dim_sel:
        vue = vue[vue["Dimension"].isin(dim_sel)]
    if crit_sel:
        vue = vue[vue["Criticité"].isin(crit_sel)]
    if statut_sel:
        vue = vue[vue["Statut"].isin(statut_sel)]

    def styler(df):
        def couleur_statut(v):
            return "background-color:#fee2e2" if v == "KO" else "background-color:#dcfce7"

        def couleur_crit(v):
            return {
                "Bloquant": "color:#dc2626;font-weight:600",
                "Majeur": "color:#d97706;font-weight:600",
                "Mineur": "color:#2563eb",
            }.get(v, "")

        return (
            df.style.applymap(couleur_statut, subset=["Statut"])
            .applymap(couleur_crit, subset=["Criticité"])
            .format({"Taux conformité (%)": "{:.2f}"})
        )

    st.dataframe(styler(vue), use_container_width=True, hide_index=True, height=520)
    st.download_button(
        "⬇️ Exporter le rapport de contrôles (CSV)",
        to_csv_bytes(vue),
        file_name=f"rapport_controles_qdd_{datetime.now():%Y%m%d}.csv",
        mime="text/csv",
    )

# ---- Anomalies ---- #
with tab_anom:
    st.subheader("Détail des lignes en anomalie")
    st.caption("Échantillon des enregistrements détectés, par contrôle — support à la résolution.")

    controles_ko = [r for r in resultats if r.nb_anomalies > 0]
    if not controles_ko:
        st.success("Aucune anomalie détectée sur le périmètre courant.")
    else:
        options = {
            f"{r.controle.id} — {r.controle.libelle} ({r.nb_anomalies} anomalies)": r
            for r in controles_ko
        }
        choix = st.selectbox("Sélectionner un contrôle", list(options.keys()))
        r = options[choix]
        st.markdown(
            f"**Dimension :** {r.controle.dimension}  ·  "
            f"**Table :** `{r.controle.table}`  ·  "
            f"**Criticité :** {r.controle.criticite}  ·  "
            f"**Taux de conformité :** {r.taux_conformite:.2f} %"
        )
        st.dataframe(r.echantillon, use_container_width=True, height=380)

        st.divider()
        toutes = anomalies_completes(resultats)
        st.download_button(
            "⬇️ Exporter toutes les anomalies (CSV)",
            to_csv_bytes(toutes),
            file_name=f"anomalies_qdd_{datetime.now():%Y%m%d}.csv",
            mime="text/csv",
        )

# ---- Dictionnaire ---- #
with tab_dict:
    st.subheader("Dictionnaire de données")
    st.caption(
        "Source de vérité de la gouvernance : type, obligation, domaine/référentiel "
        "et usage aval Solvabilité 2 de chaque champ. Pilote les contrôles d'exhaustivité et de validité."
    )
    dico = dictionnaire_df()
    table_sel = st.radio(
        "Table", ["Toutes"] + sorted(dico["table"].unique()), horizontal=True
    )
    vue_dico = dico if table_sel == "Toutes" else dico[dico["table"] == table_sel]
    st.dataframe(vue_dico, use_container_width=True, hide_index=True, height=520)
    st.download_button(
        "⬇️ Exporter le dictionnaire (CSV)",
        to_csv_bytes(dico),
        file_name="dictionnaire_donnees.csv",
        mime="text/csv",
    )

# ---- Cartographie & lignage ---- #
with tab_lin:
    st.subheader("Cartographie & lignage des flux de données")
    st.caption(
        "Du système source à la production des QRT, en passant par le dispositif QDD. "
        "Support de traçabilité pour les audits ACPR et commissaires aux comptes."
    )
    st.graphviz_chart(graphe_dot(), use_container_width=True)
    with st.expander("Légende des couches"):
        st.markdown(
            "- **Sources** : systèmes de production (contrats, sinistres, référentiel tiers)\n"
            "- **Ingestion / Staging** : extraction ODBC (SAS/SQL) et zones tampons\n"
            "- **Dispositif QDD** : exécution des contrôles, alimenté par le dictionnaire\n"
            "- **Fiabilisation → Datamart** : traitements correctifs puis mise à disposition actuariat\n"
            "- **Calcul → QRT** : provisions techniques (Best Estimate) puis reporting réglementaire\n"
            "- **Restitution** : pilotage BI (Qlik Sense)"
        )

# ---- Piste d'audit ---- #
with tab_audit:
    st.subheader("Piste d'audit — traçabilité des contrôles")
    st.caption(
        "Journal horodaté de l'exécution des contrôles. Exportable pour constituer "
        "le corpus de preuve en revue interne / externe."
    )
    audit = piste_audit(resultats)
    st.dataframe(audit, use_container_width=True, hide_index=True, height=480)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        rapport.to_excel(writer, sheet_name="Rapport_controles", index=False)
        scorecard.to_excel(writer, sheet_name="Scorecard_dimensions", index=False)
        audit.to_excel(writer, sheet_name="Piste_audit", index=False)
        dictionnaire_df().to_excel(writer, sheet_name="Dictionnaire", index=False)
    st.download_button(
        "⬇️ Exporter le dossier QDD complet (Excel)",
        buffer.getvalue(),
        file_name=f"dossier_qdd_s2_{datetime.now():%Y%m%d}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.divider()
st.caption(
    "Sentinel QDD-S2 · Prototype démonstrateur — Python / Streamlit. "
    "Transposable en production sur socle SAS / SQL / Qlik Sense."
)
