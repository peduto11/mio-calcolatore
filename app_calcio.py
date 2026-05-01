import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Calcolatore Scommesse", layout="wide")

# --- CSS PER MASSIMA LEGGIBILITÀ (SFONDO CHIARO) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #1e293b; font-family: 'Arial', sans-serif; }
    .stMetric { border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; background-color: #f8fafc; }
    .stDataFrame { border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ Predictor Risultati & Multigol")
st.write("Inserisci i dati delle squadre nella barra a sinistra per calcolare le probabilità.")

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
    # Colori verdi chiari per le celle più probabili
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

# --- ESITO FINALE 1X2 ---
st.markdown("---")
st.subheader("📈 Esito Finale & Over")
m1, m2, m3, m4 = st.columns(4)

p_1 = np.sum(np.tril(matrix, -1)) * 100
p_x = np.trace(matrix) * 100
p_2 = np.sum(np.triu(matrix, 1)) * 100
over_25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100

m1.metric("Segno 1", f"{p_1:.1f}%", f"Fair Q: {100/p_1:.2f}")
m2.metric("Segno X", f"{p_x:.1f}%", f"Fair Q: {100/p_x:.2f}")
m3.metric("Segno 2", f"{p_2:.1f}%", f"Fair Q: {100/p_2:.2f}")
m4.metric("Over 2.5", f"{over_25:.1f}%", f"Fair Q: {100/over_25:.2f}")

# --- SEZIONE MULTIGOL ---
st.subheader("🔢 Sezione Multigol")

def calc_mg(min_g, max_g):
    prob = 0
    for h in range(max_goals):
        for a in range(max_goals):
            total = h + a
            if min_g <= total <= max_g:
                prob += matrix[h, a]
    return prob * 100

g1, g2, g3, g4 = st.columns(4)
# Multigol da visualizzare
m_list = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
cols = [g1, g2, g3, g4, g1, g2, g3, g4]

for i, (low, high) in enumerate(m_list):
    p = calc_mg(low, high)
    cols[i].metric(f"Multigol {low}-{high}", f"{p:.1f}%", f"Fair Q: {100/p:.2f}")

# --- DOPPIA CHANCE ---
st.markdown("---")
st.write(f"**Doppia Chance:** 1X: **{(p_1+p_x):.1f}%** | X2: **{(p_2+p_x):.1f}%** | 12: **{(p_1+p_2):.1f}%**")
