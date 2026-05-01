import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Betting Predictor PRO", layout="wide")

# --- CSS PER LOOK PROFESSIONALE E COMPATTO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    h1, h2, h3 { color: #1e293b !important; margin-bottom: 5px !important; padding-top: 5px !important; }
    /* Ristringe i riquadri delle metriche */
    div[data-testid="stMetric"] {
        background-color: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        padding: 5px 10px !important;
        border-radius: 8px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; color: #4b5563 !important; }
    /* Toglie spazio eccessivo tra le righe */
    .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ Predictor Risultati & Multigol PRO")

# --- SIDEBAR: DATI ---
st.sidebar.header("🏠 CASA")
c_fatti_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", value=15)
c_subiti_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", value=10)
c_gare_s = st.sidebar.number_input("Partite Casa (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma (Ultime 5)")
c_fatti_5 = st.sidebar.number_input("Gol Fatti (Ultime 5 Casa)", value=8)
c_subiti_5 = st.sidebar.number_input("Gol Subiti (Ultime 5 Casa)", value=4)

st.sidebar.markdown("---")

st.sidebar.header("🚀 OSPITE")
o_fatti_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", value=10)
o_subiti_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", value=18)
o_gare_s = st.sidebar.number_input("Partite Ospite (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma (Ultime 5)")
o_fatti_5 = st.sidebar.number_input("Gol Fatti (Ultime 5 Ospite)", value=3)
o_subiti_5 = st.sidebar.number_input("Gol Subiti (Ultime 5 Ospite)", value=9)

# --- CALCOLO MEDIE PESATE ---
def get_weighted_avg(seasonal_f, recent_5, games_s):
    avg_s = seasonal_f / games_s if games_s > 0 else 0
    avg_5 = recent_5 / 5
    return (avg_s * 0.4) + (avg_5 * 0.6)

if c_gare_s > 0 and o_gare_s > 0:
    att_casa = get_weighted_avg(c_fatti_s, c_fatti_5, c_gare_s)
    def_casa = get_weighted_avg(c_subiti_s, c_subiti_5, c_gare_s)
    att_ospite = get_weighted_avg(o_fatti_s, o_fatti_5, o_gare_s)
    def_ospite = get_weighted_avg(o_subiti_s, o_subiti_5, o_gare_s)
    exp_casa = (att_casa + def_ospite) / 2
    exp_ospite = (att_ospite + def_casa) / 2
else:
    exp_casa = exp_ospite = 0

# --- MATRICE ---
max_goals = 6 
matrix = np.zeros((max_goals, max_goals))
prob_casa_list = [poisson_probability(exp_casa, i) for i in range(max_goals)]
prob_ospite_list = [poisson_probability(exp_ospite, i) for i in range(max_goals)]
for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = prob_casa_list[h] * prob_ospite_list[a]

# --- LAYOUT SUPERIORE (MATRICE E TOP 10) ---
col_mat, col_res = st.columns([2, 1])
with col_mat:
    st.subheader("📊 Matrice Probabilità")
    df_matrix = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_goals)], columns=[f"O{i}" for i in range(max_goals)])
    st.dataframe(df_matrix.style.format("{:.1f}%").background_gradient(cmap='Greens'), height=240)

with col_res:
    st.subheader("🎯 Top 10 Esatti")
    ris = []
    for h in range(max_goals):
        for a in range(max_goals):
            p = matrix[h, a]
            if p > 0.001:
                ris.append({"Risultato": f"{h}-{a}", "Prob. %": f"{p*100:.1f}%", "Q. Fair": f"{1/p:.2f}"})
    df_res = pd.DataFrame(ris).sort_values(by="Prob. %", ascending=False)
    st.dataframe(df_res.head(10), hide_index=True, height=240, use_container_width=True)

# --- MERCATI PRINCIPALI (6 COLONNE) ---
st.subheader("📈 Esito Finale, Over & Goal")
p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
p_goal = sum(matrix[h, a] for h in range(1, max_goals) for a in range(1, max_goals)) * 100
p_nogoal = 100 - p_goal

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Segno 1", f"{p1:.1f}%", f"QF: {100/p1:.2f}")
m2.metric("Segno X", f"{px:.1f}%", f"QF: {100/px:.2f}")
m3.metric("Segno 2", f"{p2:.1f}%", f"QF: {100/p2:.2f}")
m4.metric("Over 2.5", f"{ov25:.1f}%", f"QF: {100/ov25:.2f}")
m5.metric("GOAL", f"{p_goal:.1f}%", f"QF: {100/p_goal:.2f}")
m6.metric("NO GOAL", f"{p_nogoal:.1f}%", f"QF: {100/p_nogoal:.2f}")

# --- MULTIGOL PARTITA (4 COLONNE x 2 RIGHE) ---
st.subheader("🔢 Multigol Partita")
def get_mg(low, high):
    p = sum(matrix[h, a] for h in range(max_goals) for a in range(max_goals) if low <= h+a <= high)
    return p * 100

mg_list = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
cols_mg = st.columns(4)
for i, mg in enumerate(mg_list):
    p_mg = get_mg(mg[0], mg[1])
    cols_mg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{p_mg:.1f}%", f"QF: {100/p_mg:.2f}")

# --- MULTIGOL SQUADRA E DOPPIA CHANCE (ORGANIZZATI BENE) ---
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.write("**MG CASA**")
    for low, high in [(1,2), (1,3), (2,3)]:
        p = sum(prob_casa_list[i] for i in range(low, high+1)) * 100
        st.info(f"MG Casa {low}-{high}: **{p:.1f}%** (Q: {100/p:.2f})")

with c2:
    st.write("**MG OSPITE**")
    for low, high in [(1,2), (1,3), (2,3)]:
        p = sum(prob_ospite_list[i] for i in range(low, high+1)) * 100
        st.info(f"MG Ospite {low}-{high}: **{p:.1f}%** (Q: {100/p:.2f})")

with c3:
    st.write("**DOPPIA CHANCE**")
    st.success(f"1X: **{(p1+px):.1f}%** (QF: {100/(p1+px):.2f})")
    st.success(f"X2: **{(p2+px):.1f}%** (QF: {100/(p2+px):.2f})")
    st.success(f"12: **{(p1+p2):.1f}%** (QF: {100/(p1+p2):.2f})")
