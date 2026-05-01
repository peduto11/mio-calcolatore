import streamlit as st
import math
import pandas as pd
import numpy as np

st.set_page_config(page_title="Betting Predictor AI-Form", layout="wide")

# --- STILE PULITO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    .stMetric { border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; background-color: #f8fafc; }
    h1, h2, h3 { color: #1e293b !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ Predictor PRO: Analisi Stagionale + Forma Recente")
st.write("Questo modello pesa il 60% sulla forma recente (ultime 5) e il 40% sulla stagione.")

# --- SIDEBAR: DATI ---
st.sidebar.header("🏠 SQUADRA CASA")
c_fatti_s = st.sidebar.number_input("GOL FATTI Stagione (Casa)", value=25)
c_subiti_s = st.sidebar.number_input("GOL SUBITI Stagione (Casa)", value=15)
c_gare_s = st.sidebar.number_input("Partite giocate Stagione (Casa)", value=17)
st.sidebar.subheader("Ultime 5 Partite")
c_fatti_5 = st.sidebar.number_input("GOL FATTI (Ultime 5 Casa)", value=10)
c_subiti_5 = st.sidebar.number_input("GOL SUBITI (Ultime 5 Casa)", value=5)

st.sidebar.markdown("---")

st.sidebar.header("🚀 SQUADRA OSPITE")
o_fatti_s = st.sidebar.number_input("GOL FATTI Stagione (Trasferta)", value=19)
o_subiti_s = st.sidebar.number_input("GOL SUBITI Stagione (Trasferta)", value=30)
o_gare_s = st.sidebar.number_input("Partite giocate Stagione (Trasferta)", value=17)
st.sidebar.subheader("Ultime 5 Partite")
o_fatti_5 = st.sidebar.number_input("GOL FATTI (Ultime 5 Trasferta)", value=6)
o_subiti_5 = st.sidebar.number_input("GOL SUBITI (Ultime 5 Trasferta)", value=12)

# --- CALCOLO MEDIE PESATE ---
def get_weighted_avg(seasonal_f, recent_5, games_s):
    avg_s = seasonal_f / games_s if games_s > 0 else 0
    avg_5 = recent_5 / 5
    return (avg_s * 0.4) + (avg_5 * 0.6) # Peso 40% stagione, 60% ultime 5

if c_gare_s > 0 and o_gare_s > 0:
    # Attacco e Difesa Pesati
    att_casa_w = get_weighted_avg(c_fatti_s, c_fatti_5, c_gare_s)
    def_casa_w = get_weighted_avg(c_subiti_s, c_subiti_5, c_gare_s)
    att_ospite_w = get_weighted_avg(o_fatti_s, o_fatti_5, o_gare_s)
    def_ospite_w = get_weighted_avg(o_subiti_s, o_subiti_5, o_gare_s)
    
    # Valore atteso finale (Incrocio attacco casa vs difesa ospite)
    exp_casa = (att_casa_w + def_ospite_w) / 2
    exp_ospite = (att_ospite_w + def_casa_w) / 2
else:
    exp_casa = exp_ospite = 0

# --- CALCOLO MATRICE ---
max_goals = 6 
matrix = np.zeros((max_goals, max_goals))
for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = poisson_probability(exp_casa, h) * poisson_probability(exp_ospite, a)

# --- LAYOUT ---
col_mat, col_res = st.columns([2, 1])

with col_mat:
    st.subheader("📊 Matrice Probabilità (Forma Pesata)")
    df_matrix = pd.DataFrame(matrix * 100, 
                             index=[f"Casa {i}" for i in range(max_goals)], 
                             columns=[f"Ospite {i}" for i in range(max_goals)])
    st.dataframe(df_matrix.style.format("{:.2f}%").background_gradient(cmap='Greens'))

with col_res:
    st.subheader("🎯 Top 10 Risultati")
    ris = []
    for h in range(max_goals):
        for a in range(max_goals):
            p = matrix[h, a]
            if p > 0.001:
                ris.append({"Risultato": f"{h}-{a}", "Probabilità": p * 100, "Quota Fair": 1/p if p > 0 else 0})
    df_res = pd.DataFrame(ris).sort_values(by="Probabilità", ascending=False)
    st.dataframe(df_res.head(10).style.format({"Probabilità": "{:.2f}%", "Quota Fair": "{:.2f}"}), hide_index=True)

# --- ANALISI FINALE ---
st.markdown("---")
p1 = np.sum(np.tril(matrix, -1)) * 100
px = np.trace(matrix) * 100
p2 = np.sum(np.triu(matrix, 1)) * 100
ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100

st.subheader("📈 Mercati Principali")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Segno 1", f"{p1:.1f}%", f"Fair: {100/p1:.2f}")
m2.metric("Segno X", f"{px:.1f}%", f"Fair: {100/px:.2f}")
m3.metric("Segno 2", f"{p2:.1f}%", f"Fair: {100/p2:.2f}")
m4.metric("Over 2.5", f"{ov25:.1f}%", f"Fair: {100/ov25:.2f}")

# --- MULTIGOL ---
st.subheader("🔢 Multigol Partita")
def get_mg(low, high):
    p = 0
    for h in range(max_goals):
        for a in range(max_goals):
            if low <= h+a <= high: p += matrix[h, a]
    return p * 100

g1, g2, g3, g4 = st.columns(4)
multigols = [(1,2), (1,3), (2,3), (2,4)]
for i, mg in enumerate(multigols):
    prob = get_mg(mg[0], mg[1])
    [g1, g2, g3, g4][i].metric(f"Multigol {mg[0]}-{mg[1]}", f"{prob:.1f}%", f"Q: {100/prob:.2f}")
