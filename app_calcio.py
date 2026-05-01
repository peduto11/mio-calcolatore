import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Correct Score & Multigol PRO", layout="wide")

# --- CSS PER LOOK "DARK PREMIUM" ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    .stMetric { background-color: #1a1a1a; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    h1, h2, h3 { color: #00ff88; font-family: 'Segoe UI', sans-serif; }
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    div[data-testid="stExpander"] { background-color: #111111; border: 1px solid #333; }
    </style>
    """, unsafe_content_as_html=True)

def poisson_probability(lmbda, x):
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ Correct Score & Multigol PRO")
st.write("Analisi statistica basata sulla distribuzione di Poisson")

# --- INPUT DATI ---
st.sidebar.header("📊 Parametri Squadre")
casa_gol = st.sidebar.number_input("Gol Fatti Casa (Totali)", value=25)
casa_match = st.sidebar.number_input("Partite Casa", value=10)
st.sidebar.markdown("---")
ospite_gol = st.sidebar.number_input("Gol Fatti Ospite (Totali)", value=18)
ospite_match = st.sidebar.number_input("Partite Ospite", value=10)

media_casa = casa_gol / casa_match if casa_match > 0 else 0
media_ospite = ospite_gol / ospite_match if ospite_match > 0 else 0

st.sidebar.success(f"Media Casa: {media_casa:.2f}")
st.sidebar.warning(f"Media Ospite: {media_ospite:.2f}")

# --- CALCOLO MATRICE ---
max_goals = 6 
matrix = np.zeros((max_goals, max_goals))
prob_casa = [poisson_probability(media_casa, i) for i in range(max_goals)]
prob_ospite = [poisson_probability(media_ospite, i) for i in range(max_goals)]

for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = prob_casa[h] * prob_ospite[a]

# --- LAYOUT PRINCIPALE ---
col_mat, col_val = st.columns([2, 1])

with col_mat:
    st.subheader("📊 Matrice Probabilità")
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

# --- MERCATI 1X2 ---
st.markdown("---")
st.subheader("📈 Esito Finale 1X2 & Doppia Chance")
m1, m2, m3, m4 = st.columns(4)

p_1 = np.sum(np.tril(matrix, -1)) * 100
p_x = np.trace(matrix) * 100
p_2 = np.sum(np.triu(matrix, 1)) * 100

m1.metric("Segno 1", f"{p_1:.1f}%", f"Fair: {100/p_1:.2f}")
m2.metric("Segno X", f"{p_x:.1f}%", f"Fair: {100/p_x:.2f}")
m3.metric("Segno 2", f"{p_2:.1f}%", f"Fair: {100/p_2:.2f}")
m4.metric("1X DC", f"{(p_1+p_x):.1f}%", f"Fair: {100/(p_1+p_x):.2f}")

# --- SEZIONE MULTIGOL COMPLETA ---
st.markdown("---")
st.subheader("🔢 Sezione Multigol Generali")

def calc_mg(min_g, max_g):
    prob = 0
    for h in range(max_goals):
        for a in range(max_goals):
            total = h + a
            if min_g <= total <= max_g:
                prob += matrix[h, a]
    return prob * 100

g1, g2, g3, g4 = st.columns(4)
multigols = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
cols = [g1, g2, g3, g4, g1, g2, g3, g4]

for i, (min_g, max_g) in enumerate(multigols):
    p = calc_mg(min_g, max_g)
    cols[i].metric(f"Multigol {min_g}-{max_g}", f"{p:.1f}%", f"Fair: {100/p:.2f}")

# --- MULTIGOL CASA E OSPITE ---
st.markdown("---")
st.subheader("🏠 Multigol Squadre")
c1, c2 = st.columns(2)

with c1:
    st.write("**MULTIGOL CASA**")
    for mg in [(1,2), (1,3), (2,3)]:
        prob = sum(prob_casa[i] for i in range(mg[0], mg[1]+1)) * 100
        st.write(f"Variazione {mg[0]}-{mg[1]}: **{prob:.1f}%** | Quota: **{100/prob:.2f}**")

with c2:
    st.write("**MULTIGOL OSPITE**")
    for mg in [(1,2), (1,3), (2,3)]:
        prob = sum(prob_ospite[i] for i in range(mg[0], mg[1]+1)) * 100
        st.write(f"Variazione {mg[0]}-{mg[1]}: **{prob:.1f}%** | Quota: **{100/prob:.2f}**")

# --- UNDER/OVER ---
st.markdown("---")
st.subheader("⚽ Mercati Gol")
o1, o2, o3, o4 = st.columns(4)

over05 = (1 - matrix[0,0]) * 100
over15 = (1 - (matrix[0,0] + matrix[1,0] + matrix[0,1])) * 100
over25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
goal = 0
for h in range(1, max_goals):
    for a in range(1, max_goals):
        goal += matrix[h, a]

o1.metric("Over 0.5", f"{over05:.1f}%")
o2.metric("Over 1.5", f"{over15:.1f}%")
o3.metric("Over 2.5", f"{over25:.1f}%")
o4.metric("Goal/Entrambi", f"{goal*100:.1f}%")
