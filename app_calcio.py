import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Betting Predictor PRO", layout="wide")

# --- CSS PER LOOK PULITO E SENZA CATENINE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    /* Nasconde l'icona della catenina vicino ai titoli */
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { color: #1e293b !important; margin-bottom: 5px !important; }
    div[data-testid="stMetric"] {
        background-color: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        padding: 8px !important;
        border-radius: 8px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 20px !important; }
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

# --- CALCOLO ---
def get_weighted_avg(seasonal_f, recent_5, games_s):
    avg_s = seasonal_f / games_s if games_s > 0 else 0
    avg_5 = recent_5 / 5
    return (avg_s * 0.4) + (avg_5 * 0.6)

if c_gare_s > 0 and o_gare_s > 0:
    exp_casa = (get_weighted_avg(c_fatti_s, c_fatti_5, c_gare_s) + get_weighted_avg(o_subiti_s, o_subiti_5, o_gare_s)) / 2
    exp_ospite = (get_weighted_avg(o_fatti_s, o_fatti_5, o_gare_s) + get_weighted_avg(c_subiti_s, c_subiti_5, c_gare_s)) / 2
else:
    exp_casa = exp_ospite = 0

max_goals = 6 
matrix = np.zeros((max_goals, max_goals))
prob_casa_list = [poisson_probability(exp_casa, i) for i in range(max_goals)]
prob_ospite_list = [poisson_probability(exp_ospite, i) for i in range(max_goals)]
for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = prob_casa_list[h] * prob_ospite_list[a]

# --- LAYOUT MATRICE E TOP 10 ---
col_mat, col_res = st.columns([2, 1.2])
with col_mat:
    st.subheader("📊 Matrice Probabilità")
    df_matrix = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_goals)], columns=[f"O{i}" for i in range(max_goals)])
    st.dataframe(df_matrix.style.format("{:.1f}%").background_gradient(cmap='Greens'), height=245)

with col_res:
    st.subheader("🎯 Top 10 Esatti")
    ris = []
    for h in range(max_goals):
        for a in range(max_goals):
            p = matrix[h, a]
            ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "Fair Q": 1/p if p > 0 else 0})
    
    # ORDINE NUMERICO CORRETTO PRIMA DELLA FORMATTAZIONE
    df_res = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
    # Formattiamo solo dopo aver ordinato
    df_res["Prob. %"] = df_res["Prob"].map("{:.1f}%".format)
    df_res["Q. Fair"] = df_res["Fair Q"].map("{:.2f}".format)
    st.dataframe(df_res[["Risultato", "Prob. %", "Q. Fair"]], hide_index=True, height=245, use_container_width=True)

# --- MERCATI ---
st.subheader("📈 Esito Finale, Over & Goal")
p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
p_goal = sum(matrix[h, a] for h in range(1, max_goals) for a in range(1, max_goals)) * 100
p_nogoal = 100 - p_goal

m_cols = st.columns(6)
m_cols[0].metric("Segno 1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
m_cols[1].metric("Segno X", f"{px:.1f}%", f"QF:{100/px:.2f}")
m_cols[2].metric("Segno 2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
m_cols[3].metric("Over 2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
m_cols[4].metric("GOAL", f"{p_goal:.1f}%", f"QF:{100/p_goal:.2f}")
m_cols[5].metric("NO GOAL", f"{p_nogoal:.1f}%", f"QF:{100/p_nogoal:.2f}")

# --- MULTIGOL ---
st.subheader("🔢 Multigol Partita")
def get_mg(low, high):
    return sum(matrix[h, a] for h in range(max_goals) for a in range(max_goals) if low <= h+a <= high) * 100

mg_list = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
cols_mg = st.columns(4)
for i, mg in enumerate(mg_list):
    p_mg = get_mg(mg[0], mg[1])
    cols_mg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{p_mg:.1f}%", f"QF:{100/p_mg:.2f}")

# --- BASSO ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.write("**MG CASA**")
    for l, h in [(1,2), (1,3), (2,3)]:
        p = sum(prob_casa_list[i] for i in range(l, h+1)) * 100
        st.info(f"Casa {l}-{h}: {p:.1f}% (Q:{100/p:.2f})")
with c2:
    st.write("**MG OSPITE**")
    for l, h in [(1,2), (1,3), (2,3)]:
        p = sum(prob_ospite_list[i] for i in range(l, h+1)) * 100
        st.info(f"Ospite {l}-{h}: {p:.1f}% (Q:{100/p:.2f})")
with c3:
    st.write("**DOPPIA CHANCE**")
    st.success(f"1X: {(p1+px):.1f}% (QF:{100/(p1+px):.2f})")
    st.success(f"X2: {(p2+px):.1f}% (QF:{100/(p2+px):.2f})")
    st.success(f"12: {(p1+p2):.1f}% (QF:{100/(p1+p2):.2f})")
