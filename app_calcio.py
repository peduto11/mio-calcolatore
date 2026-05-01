import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Predictor Calcio PRO", layout="wide")

# --- STILE PULITO (SFONDO BIANCO) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    h1, h2, h3 { color: #1e293b !important; }
    .stMetric { border: 1px solid #d1d5db !important; padding: 10px; border-radius: 8px; background-color: #f9fafb !important; }
    div[data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; }
    .stSidebar { background-color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("🏆 Calcolatore Betting PRO: Statistiche & Forma")

# --- SIDEBAR: DATI ---
st.sidebar.header("🏠 SQUADRA IN CASA")
c_fatti_s = st.sidebar.number_input("Gol Fatti in CASA (Stagione)", value=15)
c_subiti_s = st.sidebar.number_input("Gol Subiti in CASA (Stagione)", value=10)
c_gare_s = st.sidebar.number_input("Partite in CASA (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma (Ultime 5)")
c_fatti_5 = st.sidebar.number_input("Gol Fatti (Ultime 5 Casa)", value=8)
c_subiti_5 = st.sidebar.number_input("Gol Subiti (Ultime 5 Casa)", value=4)

st.sidebar.markdown("---")

st.sidebar.header("🚀 SQUADRA OSPITE")
o_fatti_s = st.sidebar.number_input("Gol Fatti in TRASFERTA (Stagione)", value=10)
o_subiti_s = st.sidebar.number_input("Gol Subiti in TRASFERTA (Stagione)", value=18)
o_gare_s = st.sidebar.number_input("Partite in TRASFERTA (Stagione)", value=8)
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

# --- CALCOLO MATRICE ---
max_goals = 6 
matrix = np.zeros((max_goals, max_goals))
prob_casa_list = [poisson_probability(exp_casa, i) for i in range(max_goals)]
prob_ospite_list = [poisson_probability(exp_ospite, i) for i in range(max_goals)]

for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = prob_casa_list[h] * prob_ospite_list[a]

# --- LAYOUT TABELLE ---
col_mat, col_res = st.columns([2, 1])

with col_mat:
    st.subheader("📊 Matrice Probabilità")
    df_matrix = pd.DataFrame(matrix * 100, index=[f"Casa {i}" for i in range(max_goals)], columns=[f"Ospite {i}" for i in range(max_goals)])
    st.dataframe(df_matrix.style.format("{:.2f}%").background_gradient(cmap='Greens'))

with col_res:
    st.subheader("🎯 Top 10 Risultati")
    ris = []
    for h in range(max_goals):
        for a in range(max_goals):
            p = matrix[h, a]
            if p > 0.001:
                ris.append({"Risultato": f"{h}-{a}", "Probabilità": p * 100, "Fair Q.": 1/p if p > 0 else 0})
    df_res = pd.DataFrame(ris).sort_values(by="Probabilità", ascending=False)
    st.dataframe(df_res.head(10).style.format({"Probabilità": "{:.2f}%", "Fair Q.": "{:.2f}"}), hide_index=True, use_container_width=True)

# --- MERCATI 1X2 E GOAL ---
st.markdown("---")
st.subheader("📈 Mercati Principali")
p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
p_goal = sum(matrix[h, a] for h in range(1, max_goals) for a in range(1, max_goals)) * 100

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Segno 1", f"{p1:.1f}%", f"Q: {100/p1:.2f}")
m2.metric("Segno X", f"{px:.1f}%", f"Q: {100/px:.2f}")
m3.metric("Segno 2", f"{p2:.1f}%", f"Q: {100/p2:.2f}")
m4.metric("Over 2.5", f"{ov25:.1f}%", f"Q: {100/ov25:.2f}")
m5.metric("GOAL (GG)", f"{p_goal:.1f}%", f"Q: {100/p_goal:.2f}")

# --- SEZIONE MULTIGOL ---
st.subheader("🔢 Multigol Partita")
def get_mg(low, high):
    p = sum(matrix[h, a] for h in range(max_goals) for a in range(max_goals) if low <= h+a <= high)
    return p * 100

g1, g2, g3, g4 = st.columns(4)
m_list = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
for i, mg in enumerate(m_list):
    p_mg = get_mg(mg[0], mg[1])
    target_col = [g1, g2, g3, g4][i % 4]
    target_col.metric(f"Multigol {mg[0]}-{mg[1]}", f"{p_mg:.1f}%", f"Q: {100/p_mg:.2f}")

# --- MULTIGOL SQUADRA E DOPPIA CHANCE ---
st.markdown("---")
col_c, col_o, col_dc = st.columns(3)

with col_c:
    st.write("**MG CASA**")
    for low, high in [(1,2), (1,3), (2,3)]:
        p = sum(prob_casa_list[i] for i in range(low, high+1)) * 100
        st.write(f"MG Casa {low}-{high}: **{p:.1f}%** | Q: **{100/p:.2f}**")

with col_o:
    st.write("**MG OSPITE**")
    for low, high in [(1,2), (1,3), (2,3)]:
        p = sum(prob_ospite_list[i] for i in range(low, high+1)) * 100
        st.write(f"MG Ospite {low}-{high}: **{p:.1f}%** | Q: **{100/p:.2f}**")

with col_dc:
    st.write("**DOPPIA CHANCE**")
    st.write(f"1X: **{(p1+px):.1f}%** | Q: **{100/(p1+px):.2f}**")
    st.write(f"X2: **{(p2+px):.1f}%** | Q: **{100/(p2+px):.2f}**")
    st.write(f"12: **{(p1+p2):.1f}%** | Q: **{100/(p1+p2):.2f}**")
