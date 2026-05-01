import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="AI Betting Predictor PRO", layout="wide")

# --- CSS INTELLIGENTE PER DARK & LIGHT MODE ---
st.markdown("""
    <style>
    /* Nasconde link titoli */
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    
    /* Titoli compatti */
    h1, h2, h3 { margin-top: -20px; padding-bottom: 10px; }

    /* Riquadri metriche adattivi */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 5px 10px !important;
        border-radius: 8px !important;
    }
    
    /* Forza visibilità numeri nelle metriche */
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ Predictor Risultati & Multigol PRO")

# --- SIDEBAR INPUT ---
st.sidebar.header("🏠 DATI CASA")
c_f_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", value=15)
c_s_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", value=10)
c_g_s = st.sidebar.number_input("Partite Casa (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma (Ultime 5)")
c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", value=8)
c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", value=4)
st.sidebar.markdown("---")
st.sidebar.header("🚀 DATI OSPITE")
o_f_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", value=10)
o_s_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", value=18)
o_g_s = st.sidebar.number_input("Partite Ospite (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma (Ultime 5)")
o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", value=3)
o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", value=9)

# --- CALCOLO MEDIE PESATE (60/40) ---
def weighted(s_f, r_5, g_s):
    if g_s <= 0: return 0
    return ((s_f / g_s) * 0.4) + ((r_5 / 5) * 0.6)

if c_g_s > 0 and o_g_s > 0:
    exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
    exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2
else:
    exp_c = exp_o = 0

st.info(f"📊 **Medie Gol Attese (Baricentro):** Casa **{exp_c:.2f}** | Ospite **{exp_o:.2f}**")

# --- GENERAZIONE MATRICE ---
max_g = 6 
matrix = np.zeros((max_g, max_g))
for h in range(max_g):
    for a in range(max_g):
        matrix[h, a] = poisson(exp_c, h) * poisson(exp_o, a)

# --- LOGICA SCENARI ---
s1 = f"{int(round(exp_c))}-{int(round(exp_o))}"
s2 = f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}"
s3 = f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"
top_scenarios_list = [s1, s2, s3]

# --- LAYOUT SUPERIORE ---
col_mat, col_res = st.columns([2, 1.2])

with col_mat:
    st.subheader("📊 Matrice Probabilità")
    df_matrix = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)])
    st.dataframe(df_matrix.style.format("{:.1f}%").background_gradient(cmap='Greens', axis=None), height=245)

with col_res:
    st.subheader("🎯 Classifica Esatti")
    ris = []
    for h in range(max_g):
        for a in range(max_g):
            p = matrix[h, a]
            ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
    df_res = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
    
    def highlight_results(row):
        if row['Risultato'] in top_scenarios_list:
            return ['background-color: #ffff00; color: #000000; font-weight: bold'] * len(row)
        return [''] * len(row)

    df_res_styled = df_res.copy()
    df_res_styled["Prob. %"] = df_res["Prob"].map("{:.1f}%".format)
    df_res_styled["QF"] = df_res["QF"].map("{:.2f}".format)
    st.dataframe(df_res_styled[["Risultato", "Prob. %", "QF"]].style.apply(highlight_results, axis=1), hide_index=True, height=245, use_container_width=True)

# --- SCENARI SUGGERITI (COMPATTI) ---
st.subheader("💡 Scenari Suggeriti dal Modello")
scenarios_unique = list(dict.fromkeys(top_scenarios_list))
c_sce = st.columns(4) # Fisso a 4 per non allargarli troppo
for i, res_name in enumerate(scenarios_unique):
    h_s, a_s = map(int, res_name.split('-'))
    p_sce = matrix[h_s, a_s] * 100
    with c_sce[i]:
        st.metric(f"SCENARIO: {res_name}", f"{p_sce:.1f}%", f"QF: {100/p_sce:.2f}")

# --- MERCATI PRINCIPALI ---
st.subheader("📈 Esito Finale, Over & Goal")
p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
p_g = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100

m_cols = st.columns(6)
m_cols[0].metric("Segno 1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
m_cols[1].metric("Segno X", f"{px:.1f}%", f"QF:{100/px:.2f}")
m_cols[2].metric("Segno 2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
m_cols[3].metric("Over 2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
m_cols[4].metric("GOAL", f"{p_g:.1f}%", f"QF:{100/p_g:.2f}")
m_cols[5].metric("NO GOAL", f"{100-p_g:.1f}%", f"QF:{100/(100-p_g):.2f}")

# --- MULTIGOL ---
st.subheader("🔢 Multigol Partita")
def get_mg(low, high):
    return sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if low <= h+a <= high) * 100
mg_cols = st.columns(4)
m_l = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
for i, (l, h) in enumerate(m_l):
    p_mg = get_mg(l, h)
    mg_cols[i % 4].metric(f"MG {l}-{h}", f"{p_mg:.1f}%", f"QF:{100/p_mg:.2f}")

# --- BASSO ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.write("**MG CASA**")
    prob_c_list = [poisson(exp_c, i) for i in range(max_g)]
    for l, h in [(1,2), (1,3), (2,3)]:
        p = sum(prob_c_list[i] for i in range(l, h+1)) * 100
        st.write(f"Casa {l}-{h}: **{p:.1f}%** (Q:{100/p:.2f})")
with c2:
    st.write("**MG OSPITE**")
    prob_o_list = [poisson(exp_o, i) for i in range(max_g)]
    for l, h in [(1,2), (1,3), (2,3)]:
        p = sum(prob_o_list[i] for i in range(l, h+1)) * 100
        st.write(f"Ospite {l}-{h}: **{p:.1f}%** (Q:{100/p:.2f})")
with c3:
    st.write("**DOPPIA CHANCE**")
    st.write(f"1X: **{(p1+px):.1f}%** (QF:{100/(p1+px):.2f})")
    st.write(f"X2: **{(p2+px):.1f}%** (QF:{100/(p2+px):.2f})")
    st.write(f"12: **{(p1+p2):.1f}%** (QF:{100/(p1+p2):.2f})")
