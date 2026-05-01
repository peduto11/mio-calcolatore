import streamlit as st
import math
import pandas as pd
import numpy as np

st.set_page_config(page_title="Predittore Betting PRO", layout="wide")

# --- STILE PULITO E LEGGIBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; background-color: #f8fafc; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e293b !important; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ Calcolatore Professionale Risultati Esatti")
st.write("Questo modello incrocia l'Attacco di una squadra con la Difesa dell'altra.")

# --- SIDEBAR: DATI AVANZATI ---
st.sidebar.header("🏠 Squadra in Casa")
c_fatti = st.sidebar.number_input("Gol FATTI in casa", value=25)
c_subiti = st.sidebar.number_input("Gol SUBITI in casa", value=15)
c_gare = st.sidebar.number_input("Partite giocate in casa", value=17)

st.sidebar.markdown("---")

st.sidebar.header("🚀 Squadra Ospite")
o_fatti = st.sidebar.number_input("Gol FATTI in trasferta", value=19)
o_subiti = st.sidebar.number_input("Gol SUBITI in trasferta", value=30)
o_gare = st.sidebar.number_input("Partite giocate in trasferta", value=17)

# Calcolo medie
if c_gare > 0 and o_gare > 0:
    att_casa = c_fatti / c_gare
    def_casa = c_subiti / c_gare
    att_ospite = o_fatti / o_gare
    def_ospite = o_subiti / o_gare
    
    # Media Poisson Incrociata (Attacco vs Difesa)
    exp_casa = (att_casa + def_ospite) / 2
    exp_ospite = (att_ospite + def_casa) / 2
else:
    exp_casa = exp_ospite = 0

st.sidebar.info(f"Potenziale Casa: {exp_casa:.2f} gol")
st.sidebar.info(f"Potenziale Ospite: {exp_ospite:.2f} gol")

# --- CALCOLO MATRICE ---
max_goals = 6 
matrix = np.zeros((max_goals, max_goals))
prob_casa = [poisson_probability(exp_casa, i) for i in range(max_goals)]
prob_ospite = [poisson_probability(exp_ospite, i) for i in range(max_goals)]

for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = prob_casa[h] * prob_ospite[a]

# --- VISUALIZZAZIONE ---
col_mat, col_res = st.columns([2, 1])

with col_mat:
    st.subheader("📊 Matrice di Probabilità (Incrociata)")
    df_matrix = pd.DataFrame(matrix * 100, 
                             index=[f"Casa {i}" for i in range(max_goals)], 
                             columns=[f"Ospite {i}" for i in range(max_goals)])
    st.dataframe(df_matrix.style.format("{:.2f}%").background_gradient(cmap='Greens'))

with col_res:
    st.subheader("🎯 Top 10 Risultati Esatti")
    ris = []
    for h in range(max_goals):
        for a in range(max_goals):
            p = matrix[h, a]
            if p > 0.001:
                ris.append({"Risultato": f"{h}-{a}", "Probabilità": p * 100, "Quota Fair": 1/p if p > 0 else 0})
    df_res = pd.DataFrame(ris).sort_values(by="Probabilità", ascending=False)
    st.dataframe(df_res.head(10).style.format({"Probabilità": "{:.2f}%", "Quota Fair": "{:.2f}"}), hide_index=True)

# --- MERCATI 1X2 ---
st.markdown("---")
st.subheader("📈 Analisi Mercati Principali")
p1 = np.sum(np.tril(matrix, -1)) * 100
px = np.trace(matrix) * 100
p2 = np.sum(np.triu(matrix, 1)) * 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("Segno 1", f"{p1:.1f}%", f"Fair: {100/p1:.2f}")
m2.metric("Segno X", f"{px:.1f}%", f"Fair: {100/px:.2f}")
m3.metric("Segno 2", f"{p2:.1f}%", f"Fair: {100/p2:.2f}")
m4.metric("Over 2.5", f"{(1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100:.1f}%")

# --- MULTIGOL ---
st.subheader("🔢 Multigol Partita")
def get_mg(low, high):
    p = 0
    for h in range(max_goals):
        for a in range(max_goals):
            if low <= h+a <= high: p += matrix[h, a]
    return p * 100

g1, g2, g3, g4 = st.columns(4)
for i, mg in enumerate([(1,2), (1,3), (2,3), (2,4)]):
    prob = get_mg(mg[0], mg[1])
    [g1, g2, g3, g4][i].metric(f"Multigol {mg[0]}-{mg[1]}", f"{prob:.1f}%", f"Q: {100/prob:.2f}")
