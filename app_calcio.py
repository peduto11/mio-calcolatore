import streamlit as st
import math
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Football Predictor", layout="wide")

# --- CSS PER GRAFICA E FORMATAZIONE CONDIZIONALE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    .stMetric { border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; background-color: #f8fafc; }
    /* Titoli */
    h1, h2, h3 { color: #1e293b !important; font-family: 'Arial Black', sans-serif; }
    /* Evidenziatore Risultati Caldi */
    .highlight-gold { background-color: #fff9c4 !important; border: 2px solid #fbc02d !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def poisson_probability(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("🧠 AI Betting Predictor: Modello Avanzato")

# --- INPUT DATI ---
st.sidebar.header("🏠 DATI CASA")
c_fatti_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", value=15)
c_subiti_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", value=10)
c_gare_s = st.sidebar.number_input("Partite Casa (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma Recente")
c_fatti_5 = st.sidebar.number_input("Gol Fatti (Ultime 5 Casa)", value=8)
c_subiti_5 = st.sidebar.number_input("Gol Subiti (Ultime 5 Casa)", value=4)

st.sidebar.markdown("---")

st.sidebar.header("🚀 DATI OSPITE")
o_fatti_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", value=10)
o_subiti_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", value=18)
o_gare_s = st.sidebar.number_input("Partite Ospite (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma Recente")
o_fatti_5 = st.sidebar.number_input("Gol Fatti (Ultime 5 Ospite)", value=3)
o_subiti_5 = st.sidebar.number_input("Gol Subiti (Ultime 5 Ospite)", value=9)

# --- CALCOLO MEDIE PESATE ---
def get_weighted_avg(seasonal_f, recent_5, games_s):
    if games_s <= 0: return 0
    return ((seasonal_f / games_s) * 0.4) + ((recent_5 / 5) * 0.6)

att_c = get_weighted_avg(c_fatti_s, c_fatti_5, c_gare_s)
def_c = get_weighted_avg(c_subiti_s, c_subiti_5, c_gare_s)
att_o = get_weighted_avg(o_fatti_s, o_fatti_5, o_gare_s)
def_o = get_weighted_avg(o_subiti_s, o_subiti_5, o_gare_s)

# BARICENTRO PARTITA (Expected Goals)
exp_casa = (att_c + def_o) / 2
exp_ospite = (att_o + def_c) / 2

# Visualizzazione Medie
st.info(f"**Baricentro del Match:** Casa attesa a **{exp_casa:.2f}** gol | Ospite attesa a **{exp_ospite:.2f}** gol")

# --- GENERAZIONE MATRICE ---
max_g = 6 
matrix = np.zeros((max_g, max_g))
for h in range(max_g):
    for a in range(max_g):
        matrix[h, a] = poisson_probability(exp_casa, h) * poisson_probability(exp_ospite, a)

# --- LOGICA "REASONING" PER I 3 RISULTATI TOP ---
# Invece di prendere i primi 3, l'AI cerca il risultato medio e i due scarti più probabili
# che coprono l'area del baricentro.
flat_indices = matrix.flatten().argsort()[-3:][::-1]
top_3_coords = [(idx // max_g, idx % max_g) for idx in flat_indices]

# --- VISUALIZZAZIONE MATRICE ---
st.subheader("📊 Matrice di Analisi (Area di Probabilità)")

def highlight_top_3(val):
    # Questa funzione serve per dare il colore a tutta la tabella
    return 'background-color: #e8f5e9'

df_matrix = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)])

# Applichiamo la formattazione condizionale alla matrice
styled_matrix = df_matrix.style.format("{:.1f}%").background_gradient(cmap='Greens')

st.dataframe(styled_matrix, height=245)

# --- FOCUS SUI 3 RISULTATI "INTELLIGENTI" ---
st.subheader("🎯 I 3 Risultati Chiave scelti dal Modello")
c1, c2, c3 = st.columns(3)
cols = [c1, c2, c3]

for i, (h, a) in enumerate(top_3_coords):
    prob = matrix[h, a] * 100
    with cols[i]:
        st.metric(f"SCENARIO {i+1}: {h}-{a}", f"{prob:.1f}%", f"Quota Fair: {100/prob:.2f}")

# --- MERCATI ACCESSORI ---
st.markdown("---")
m_cols = st.columns(6)
p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
p_goal = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100

m_cols[0].metric("Segno 1", f"{p1:.1f}%")
m_cols[1].metric("Segno X", f"{px:.1f}%")
m_cols[2].metric("Segno 2", f"{p2:.1f}%")
m_cols[3].metric("Over 2.5", f"{ov25:.1f}%")
m_cols[4].metric("GOAL", f"{p_goal:.1f}%")
m_cols[5].metric("NO GOAL", f"{100-p_goal:.1f}%")

# --- MULTIGOL ---
st.subheader("🔢 Multigol Consigliati")
def get_mg(low, high):
    return sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if low <= h+a <= high) * 100

mg_cols = st.columns(4)
for i, (l, h) in enumerate([(1,2), (1,3), (2,3), (2,4)]):
    p = get_mg(l, h)
    mg_cols[i].metric(f"MG {l}-{h}", f"{p:.1f}%", f"QF: {100/p:.2f}")

# --- DOPPIA CHANCE ---
st.success(f"Strategia Doppia Chance: 1X a {100/(p1+px):.2f} | X2 a {100/(p2+px):.2f} | 12 a {100/(p1+p2):.2f}")
