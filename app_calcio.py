import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Calcolatore Scommesse PRO", layout="wide")

# --- CSS PER MASSIMA LEGGIBILITÀ ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    h1, h2, h3 { color: #1e293b !important; }
    .stMetric { border: 1px solid #d1d5db !important; padding: 10px; border-radius: 8px; background-color: #f9fafb !important; }
    div[data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ Predictor Completo: Risultati, Over & Multigol")

# --- INPUT DATI (Barra laterale) ---
st.sidebar.header("📊 Dati Squadre")
casa_gol = st.sidebar.number_input("Gol Fatti Casa (Totali)", value=20)
casa_match = st.sidebar.number_input("Partite Casa", value=10)
st.sidebar.markdown("---")
ospite_gol = st.sidebar.number_input("Gol Fatti Ospite (Totali)", value=15)
ospite_match = st.sidebar.number_input("Partite Ospite", value=10)

media_casa = casa_gol / casa_match if casa_match > 0 else 0
media_ospite = ospite_gol / ospite_match if ospite_match > 0 else 0

st.sidebar.info(f"Media Casa: {media_casa:.2f}")
st.sidebar.info(f"Media Ospite: {media_ospite:.2f}")

# --- CALCOLO MATRICE ---
max_goals = 6 
matrix = np.zeros((max_goals, max_goals))
prob_casa = [poisson_probability(media_casa, i) for i in range(max_goals)]
prob_ospite = [poisson_probability(media_ospite, i) for i in range(max_goals)]

for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = prob_casa[h] * prob_ospite[a]

# --- LAYOUT TABELLE ---
col_mat, col_val = st.columns([2, 1])

with col_mat:
    st.subheader("📊 Matrice Probabilità Risultati")
    df_matrix = pd.DataFrame(matrix * 100, 
                             index=[f"Casa {i}" for i in range(max_goals)], 
                             columns=[f"Ospite {i}" for i in range(max_goals)])
    st.dataframe(df_matrix.style.format("{:.2f}%").background_gradient(cmap='Greens'))

with col_val:
    st.subheader("🎯 Top 10 Risultati Esatti")
    risultati = []
    for h in range(max_goals):
        for a in range(max_goals):
            prob = matrix[h, a]
            if prob > 0.005:
                risultati.append({"Risultato": f"{h}-{a}", "Probabilità": prob * 100, "Quota Fair": 1 / prob})
    df_res = pd.DataFrame(risultati).sort_values(by="Probabilità", ascending=False)
    st.dataframe(df_res.head(10).style.format({"Probabilità": "{:.2f}%", "Quota Fair": "{:.2f}"}), hide_index=True, use_container_width=True)

# --- ESITO FINALE 1X2 E GOAL ---
st.markdown("---")
st.subheader("📈 Mercati Principali & Goal/NoGoal")
m1, m2, m3, m4, m5 = st.columns(5)

p_1 = np.sum(np.tril(matrix, -1)) * 100
p_x = np.trace(matrix) * 100
p_2 = np.sum(np.triu(matrix, 1)) * 100
over_25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100

# Calcolo Goal (Entrambi segnano)
p_goal = 0
for h in range(1, max_goals):
    for a in range(1, max_goals):
        p_goal += matrix[h, a]
p_goal = p_goal * 100

m1.metric("Segno 1", f"{p_1:.1f}%", f"Q: {100/p_1:.2f}")
m2.metric("Segno X", f"{p_x:.1f}%", f"Q: {100/p_x:.2f}")
m3.metric("Segno 2", f"{p_2:.1f}%", f"Q: {100/p_2:.2f}")
m4.metric("Over 2.5", f"{over_25:.1f}%", f"Q: {100/over_25:.2f}")
m5.metric("GOAL (GG)", f"{p_goal:.1f}%", f"Q: {100/p_goal:.2f}")

# --- SEZIONE MULTIGOL ---
st.subheader("🔢 Sezione Multigol Partita")

def calc_mg(min_g, max_g):
    prob = 0
    for h in range(max_goals):
        for a in range(max_goals):
            total = h + a
            if min_g <= total <= max_g:
                prob += matrix[h, a]
    return prob * 100

g1, g2, g3, g4 = st.columns(4)
m_list = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
cols = [g1, g2, g3, g4, g1, g2, g3, g4]

for i, (low, high) in enumerate(m_list):
    p = calc_mg(low, high)
    cols[i].metric(f"Multigol {low}-{high}", f"{p:.1f}%", f"Fair Q: {100/p:.2f}")

# --- MULTIGOL SQUADRA ---
st.markdown("---")
st.subheader("🏠 Multigol Squadra (Casa e Ospite)")
c1, c2 = st.columns(2)

with c1:
    st.write("**CASA**")
    for low, high in [(1,2), (1,3), (2,3)]:
        p = sum(prob_casa[i] for i in range(low, high+1)) * 100
        st.write(f"Multigol Casa {low}-{high}: **{p:.1f}%** | Quota: **{100/p:.2f}**")

with c2:
    st.write("**OSPITE**")
    for low, high in [(1,2), (1,3), (2,3)]:
        p = sum(prob_ospite[i] for i in range(low, high+1)) * 100
        st.write(f"Multigol Ospite {low}-{high}: **{p:.1f}%** | Quota: **{100/p:.2f}**")
