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

# --------------------------------------------------------------------------- #
# En-tête + KPI
# --------------------------------------------------------------------------- #
st.title("Dispositif Qualité des Données — Solvabilité 2")
st.markdown(
    "Chaîne de fiabilisation des données alimentant les provisions techniques "
    "et les **QRT**. Contrôles structurés sur les dimensions réglementaires "
    "**EIOPA** (Exhaustivité · Exactitude · Cohérence)."
)

total_anomalies = int(rapport["Anomalies"].sum())
nb_bloquants = int(
    rapport[(rapport["Criticité"] == "Bloquant") & (rapport["Statut"] == "KO")].shape[0]
)
nb_ctrl_ko = int((rapport["Statut"] == "KO").sum())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Score QDD global", f"{score} %", help="Moyenne des taux de conformité pondérée par la criticité.")
c2.metric("Contrôles exécutés", len(resultats))
c3.metric("Contrôles en échec", nb_ctrl_ko, delta=f"-{nb_ctrl_ko}" if nb_ctrl_ko else "0",
          delta_color="inverse")
c4.metric("Anomalies détectées", f"{total_anomalies:,}".replace(",", " "))
c5.metric("Anomalies bloquantes", nb_bloquants,
          delta="Attention" if nb_bloquants else "RAS",
          delta_color="inverse" if nb_bloquants else "off")

if nb_bloquants:
    st.error(
        f"🚫 {nb_bloquants} contrôle(s) **bloquant(s)** en échec — "
        "les données ne sont pas éligibles à l'alimentation des calculs S2 en l'état."
    )
else:
    st.success("✅ Aucun contrôle bloquant en échec.")

st.divider()

# --------------------------------------------------------------------------- #
# Onglets
# --------------------------------------------------------------------------- #
tab_synth, tab_ctrl, tab_anom, tab_dict, tab_lin, tab_audit = st.tabs(
    [
        "📊 Synthèse qualité",
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
