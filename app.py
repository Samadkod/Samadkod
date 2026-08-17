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

# ========= Custom CSS pour rendre les tabs bien visibles =========
st.markdown("""
<style>
/* Rendre les tabs PLUS GRANDS et COLORÉS */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    height: 60px;
    white-space: pre-wrap;
    background-color: #ecf0f7;
    border-radius: 6px;
    padding: 12px 20px;
    border: 2px solid #1f77b4;
    font-size: 15px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] [data-baseweb="tab"] {
    background-color: #1f77b4;
    color: white;
    border: 2px solid #0f3d7f;
    box-shadow: 0 4px 8px rgba(31, 119, 180, 0.4);
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #2D6CDF;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(45, 108, 223, 0.3);
}

/* Ajouter des icônes en couleur */
.stTabs [data-baseweb="tab"] div {
    font-size: 18px;
    margin-right: 8px;
}
</style>
""", unsafe_allow_html=True)

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
tab_glossaire, tab_synth, tab_s2, tab_ctrl, tab_anom, tab_dict, tab_lin, tab_audit = st.tabs(
    [
        "📚\nComprendre\nl'Assurance",
        "📊\nSynthèse\nQualité",
        "💰\nSolvabilité 2\nImpact",
        "✅\nContrôles",
        "🔎\nAnomalies",
        "📖\nDictionnaire",
        "🗺️\nCartographie\n& Lignage",
        "🧾\nPiste\nd'Audit",
    ]
)

# ---- Comprendre l'Assurance (Glossaire) ---- #
with tab_glossaire:
    st.subheader("📚 Comprendre l'Assurance — Expliqué Simplement")
    st.caption("Si vous êtes nouveau dans l'assurance, commencez ici. Les concepts fondamentaux expliqués sans jargon.")

    # Concept 1: Assurance Basique
    with st.expander("🏦 Qu'est-ce qu'une Assurance? (Le Concept de Base)"):
        st.markdown("""
        **L'idée simple:**
        - Vous payez une prime (ex: 500€/an pour assurer votre maison)
        - Si quelque chose de grave arrive (incendie, vol), l'assureur vous paie

        **Exemple concret (Assurance Habitation):**
        ```
        Janvier 2024: Vous payez 500€ à l'assureur pour assurer votre maison
        → L'assureur rentre 500€
        → L'assureur met de côté de l'argent pour les sinistres possibles

        Juillet 2024: Votre maison brûle
        → Vous demandez 200,000€ de compensation
        → L'assureur paie les 200,000€
        ```

        **Le problème pour l'assureur:**
        Si 1000 gens paient 500€ chacun (500,000€ total), mais que 100 maisons brûlent (20,000,000€ à payer), l'assureur PERD 19,500,000€!

        **C'est pour ça qu'il faut des provisions (des réserves).**
        """)

    with st.expander("💰 Provisions Techniques — L'Argent de Côté"):
        st.markdown("""
        **Qu'est-ce que c'est?**
        L'argent que l'assureur DOIT mettre de côté pour payer les sinistres futurs.

        **Exemple:**
        - L'assureur reçoit 500,000€ de primes cette année
        - Historiquement, il doit payer ~400,000€ de sinistres
        - Donc il doit mettre de côté 400,000€ (= provision)
        - Les 100,000€ restants = son profit/fonds propres

        **Pourquoi c'est important?**
        Si l'assureur se trompe sur la provision (calcule 300,000€ au lieu de 400,000€), il n'a pas assez d'argent quand les sinistres arrivent → faillite → clients ne sont pas payés.
        """)

    with st.expander("🎯 Solvabilité 2 — La Règle du Jeu"):
        st.markdown("""
        **Qu'est-ce que c'est?**
        Une règle stricte que les assureurs DOIVENT respecter. Elle dit:
        "Vous devez avoir assez d'argent pour survivre même en cas de crise majeure"

        **Les 3 seuils importants:**

        1. **Best Estimate** = Votre estimation des sinistres futurs
           - C'est la "moyenne" des sinistres qu'on anticipe
           - Calculée à partir de vos données historiques
           - Si vos données sont pourries → Best Estimate est faux → tout le calcul est faux

        2. **SCR (Solvency Capital Requirement)** = Capital requis pour crise majeure
           - Il faut que vous ayez au moins ce montant
           - Si vous en avez moins → attention! L'ACPR va vous surveiller
           - Si vous avez exactement SCR → limite minimale, ok mais stressant
           - Si vous en avez 130% du SCR → confortable

        3. **MCR (Minimum Capital Requirement)** = Le dernier seuil critique
           - En dessous de ça, c'est catastrophe
           - L'ACPR intervient et peut vous fermer l'entreprise
           - C'est "vous êtes complètement insolvable"

        **En gros:** Solvabilité 2 = "Vous devez prouver à l'ACPR que vous pouvez payer vos clients même en cas de crise"
        """)

    with st.expander("🔎 QDD (Qualité des Données) — Pourquoi C'est Important"):
        st.markdown("""
        **Le problème:**
        Toutes les calculs de Solvabilité 2 dépendent de VOS DONNÉES.

        Si vos données sont pourries → tous vos calculs sont pourris → vous rapportez des chiffres faux à l'ACPR

        **Exemples d'anomalies (données pourries):**
        - Un client est enregistré 3 fois (doublon)
        - Un montant de sinistre est négatif (-50,000€ au lieu de +50,000€)
        - Une date est incohérente (sinistre déclaré en 2026 mais survenu en 2020)
        - Un sinistre n'est lié à aucun contrat (orphelin)

        **Impact direct:**
        ```
        Données pourries
        ↓
        Best Estimate faux
        ↓
        SCR/MCR faux
        ↓
        Rapports ACPR faux
        ↓
        ACPR découvre l'erreur
        ↓
        Sanction / Perte de confiance / Clients non couverts
        ```

        **C'est pour ça qu'on met en place QDD:**
        Vérifier que les données sont bonnes AVANT de les utiliser pour les calculs S2.
        """)

    with st.expander("✅ Contrôles QDD — Comment On Vérifie"):
        st.markdown("""
        **L'idée simple:**
        On écrit des règles. On les applique à vos données. On voit combien de lignes ne respectent pas les règles.

        **Exemple de contrôles:**

        1. **"Pas de doublon client"** (Dimension: Unicité)
           - Règle: Chaque client doit avoir 1 seule entrée
           - Test: On regarde les clients avec le même numéro
           - Résultat: Si y'en a 2, c'est une anomalie

        2. **"Montants positifs"** (Dimension: Exactitude)
           - Règle: Un sinistre ne peut pas coûter -50,000€
           - Test: On regarde tous les montants < 0
           - Résultat: Si c'est négatif, c'est une anomalie

        3. **"Date de déclaration ≥ date de sinistre"** (Dimension: Cohérence)
           - Règle: Vous déclarez pas un sinistre avant qu'il n'arrive
           - Test: On compare les dates
           - Résultat: Si déclaration < sinistre, c'est une anomalie

        4. **"Aucun champ obligatoire vide"** (Dimension: Exhaustivité)
           - Règle: Les champs importants ne doivent pas être NULL
           - Test: On regarde les cases vides
           - Résultat: Si vide, c'est une anomalie

        **Criticité:**
        - **Bloquant** = Données NON éligibles S2, faut absolument fixer avant reporting ACPR
        - **Majeur** = Important, ça fausse les calculs, à fixer rapidement
        - **Mineur** = Ça peut attendre, pas immédiat mais à tracer
        """)

    with st.expander("📊 Comment Lire les Stats de Cette App"):
        st.markdown("""
        **Score QDD Global (ex: 85%)**
        - = Pourcentage de données conformes
        - Calculé: (Lignes OK / Total lignes) × 100
        - 100% = parfait, 85% = bon, <50% = alerte rouge

        **Contrôles Exécutés (ex: 14)**
        - = Nombre de règles qu'on a appliquées
        - Chaque règle teste un aspect de la qualité

        **Contrôles en Échec (ex: 3)**
        - = Nombre de règles qui ont trouvé des anomalies
        - 0 = parfait, >5 = problème

        **Anomalies Détectées (ex: 287)**
        - = Nombre de LIGNES qui ne respectent pas les règles
        - 1 doublon = 1 anomalie
        - 1 date fausse = 1 anomalie
        - 1 montant vide = 1 anomalie
        - Total = somme de tout

        **Anomalies Bloquantes (ex: 2)**
        - = Nombre d'anomalies CRITIQUES
        - Si c'est >0 = STOP, faut fixer avant de rapporter à l'ACPR
        - Si c'est 0 = OK, vous pouvez utiliser les données pour S2

        **Best Estimate (ex: 3.4M)**
        - = Montant des provisions qu'il faut mettre de côté
        - En euros
        - Si c'est faux de 10%, ça coûte 340,000€!

        **Impact Qualité (ex: -1.8M)**
        - = Combien les anomalies vous font perdre en provisions
        - Négatif = perte de fiabilité
        - Plus c'est négatif, plus les anomalies sont graves

        **Ratio SCR/MCR (ex: 130% / 145%)**
        - Doit être ≥ 100% (minimum requis)
        - 130% = confortable, largement au-dessus du minimum
        - <100% = problème, vous devez améliorer
        """)

    st.divider()
    st.markdown("### 📖 Glossaire Complet")

    glossaire = {
        "🏢 **Assurance**": "Contrat où vous payez une prime et l'assureur vous paie si malheur arrive",
        "💵 **Prime**": "L'argent que vous payez chaque année pour être assuré(e)",
        "💰 **Sinistre**": "Le malheur qui arrive (incendie, accident, décès) — ce que l'assureur doit payer",
        "🛡️ **Assureur**": "La compagnie d'assurance (celle qui vous paie si sinistre)",
        "📋 **Provisions Techniques**": "Argent que l'assureur met de côté pour payer les sinistres futurs",
        "📊 **Best Estimate**": "Estimation du montant des sinistres futurs (base du calcul des provisions)",
        "⚖️ **Solvabilité**": "Capacité de payer ses obligations (clients). Une assurance insolvable = faillite",
        "🎯 **Solvabilité 2**": "Cadre réglementaire stricte imposé par l'Europe aux assureurs",
        "💎 **SCR (Solvency Capital Requirement)**": "Capital que vous DEVEZ avoir pour survivre à une crise majeure",
        "🚨 **MCR (Minimum Capital Requirement)**": "Capital MINIMUM — en dessous, c'est catastrophe",
        "📈 **Ratio de Solvabilité**": "Fonds propres / Capital requis. Doit être ≥100%",
        "🔎 **QDD (Qualité des Données)**": "Dispositif de vérification que vos données sont correctes",
        "📋 **Contrôle QDD**": "Une règle qu'on applique à vos données pour détecter anomalies",
        "❌ **Anomalie**": "Une ligne de données qui ne respecte pas une règle (doublon, date fausse, etc.)",
        "🔄 **Doublon**": "Deux fois la même donnée (ex: même client enregistré 2 fois)",
        "💨 **Orphelin**": "Données sans lien (ex: sinistre pas lié à aucun contrat)",
        "🎨 **Dimension EIOPA**": "6 aspects de qualité: Exhaustivité, Exactitude, Cohérence, Validité, Unicité, Intégrité",
        "🚩 **Criticité**": "Niveau de gravité (Bloquant, Majeur, Mineur)",
        "✅ **Conformité**": "Pourcentage de données qui respectent les règles",
        "🏦 **ACPR**": "L'autorité française qui régule les assureurs (autorité de contrôle)",
        "📄 **QRT**": "Rapports standardisés qu'on envoie à l'ACPR",
        "🧾 **Piste d'Audit**": "Journal traçable de tous les contrôles exécutés (preuve pour l'ACPR)",
    }

    cols = st.columns(2)
    for i, (terme, definition) in enumerate(glossaire.items()):
        with cols[i % 2]:
            st.markdown(f"**{terme}**")
            st.write(definition)
            st.markdown("---")

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
