import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Correct Score PRO", layout="wide")

# --- CSS PER LOOK PROFESSIONALE (DARK THEME) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1f2937 !important; border-radius: 10px; padding: 15px; border: 1px solid #374151; color: white !important; }
    [data-testid="stSidebar"] { background-color: #111827; }
    h1, h2, h3 { color: #00ff88 !important; }
    .stDataFrame { border: 1px solid #374151; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("🏆 Correct Score & Multigol Predictor")
st.write("Analisi statistica basata sulla distribuzione di Poisson")

# --- INPUT DATI ---
st.sidebar.header("📊 Dati Squadre")
casa_gol = st.sidebar.number_input("Gol Fatti Casa (Totali)", value=20)
casa_match = st.sidebar.number_input("Partite Casa", value=10)
st.sidebar.markdown("---")
ospite_gol = st.sidebar.number_input("Gol Fatti Ospite (Totali)", value=15)
ospite_match = st.sidebar.number_input("Partite Ospite", value=10)

media_casa = casa_gol / casa_match if casa_match > 0 else 0
media_ospite = ospite_gol / ospite_match if ospite_match > 0 else 0

st.sidebar.info(f"Media Casa: {media_casa:.2f} | Media Ospite: {media_ospite:.2f}")

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
    st.subheader("🖼️ Matrice Probabilità")
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

# --- MERCATI PRINCIPALI (1X2, Over) ---
st.markdown("---")
st.subheader("📈 Esito Finale 1X2 & Over")
m1, m2, m3, m4 = st.columns(4)

p_1 = np.sum(np.tril(matrix, -1)) * 100
p_x = np.trace(matrix) * 100
p_2 = np.sum(np.triu(matrix, 1)) * 100
over_25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100

m1.metric("Segno 1", f"{p_1:.1f}%", f"Quota: {100/p_1:.2f}")
m2.metric("Segno X", f"{p_x:.1f}%", f"Quota: {100/p_x:.2f}")
m3.metric("Segno 2", f"{p_2:.1f}%", f"Quota: {100/p_2:.2f}")
m4.metric("Over 2.5", f"{over_25:.1f}%", f"Quota: {100/over_25:.2f}")

# --- SEZIONE MULTIGOL ---
st.subheader("🔢 Sezione Multigol")
mg_col1, mg_col2, mg_col3, mg_col4 = st.columns(4)

def calc_mg(min_g, max_g):
    prob = 0
    for h in range(max_goals):
        for a in range(max_goals):
            total = h + a
            if min_g <= total <= max_g:
                prob += matrix[h, a]
    return prob * 100

# Calcolo Multigol
mg12 = calc_mg(1, 2)
mg13 = calc_mg(1, 3)
mg23 = calc_mg(2, 3)
mg24 = calc_mg(2, 4)

mg_col1.metric("Multigol 1-2", f"{mg12:.1f}%", f"Quota: {100/mg12:.2f}")
mg_col2.metric("Multigol 1-3", f"{mg13:.1f}%", f"Quota: {100/mg13:.2f}")
mg_col3.metric("Multigol 2-3", f"{mg23:.1f}%", f"Quota: {100/mg23:.2f}")
mg_col4.metric("Multigol 2-4", f"{mg24:.1f}%", f"Quota: {100/mg24:.2f}")

# Seconda riga Multigol
st.write("")
mg_col5, mg_col6, mg_col7, mg_col8 = st.columns(4)
mg14 = calc_mg(1, 4)
mg25 = calc_mg(2, 5)
mg34 = calc_mg(3, 4)
mg35 = calc_mg(3, 5)

mg_col5.metric("Multigol 1-4", f"{mg14:.1f}%", f"Quota: {100/mg14:.2f}")
mg_col6.metric("Multigol 2-5", f"{mg25:.1f}%", f"Quota: {100/mg25:.2f}")
mg_col7.metric("Multigol 3-4", f"{mg34:.1f}%", f"Quota: {100/mg34:.2f}")
mg_col8.metric("Multigol 3-5", f"{mg35:.1f}%", f"Quota: {100/mg35:.2f}")

# --- DOPPIA CHANCE ---
st.markdown("---")
st.write(f"**Doppia Chance:** 1X: {(p_1+p_x):.1f}% (Q: {100/(p_1+p_x):.2f}) | X2: {(p_2+p_x):.1f}% (Q: {100/(p_2+p_x):.2f}) | 12: {(p_1+p_2):.1f}% (Q: {100/(p_1+p_2):.2f})")
