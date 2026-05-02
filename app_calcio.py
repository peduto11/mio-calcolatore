import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE DETECTOR PRO", page_icon="⚽", layout="wide")

# --- CSS PER LOOK PROFESSIONALE E COMPATTO ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 10px; }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 5px 10px !important;
        border-radius: 8px !important;
        margin-bottom: 5px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 18px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ FT SCORE DETECTOR & MULTIGOL PRO")

# --- SIDEBAR UNICA ---
st.sidebar.header("🏠 DATI CASA")
c_f_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", value=15)
c_s_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", value=10)
c_g_s = st.sidebar.number_input("Partite Casa (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma (U5)")
c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", value=8)
c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", value=4)

st.sidebar.markdown("---")
st.sidebar.header("🚀 DATI OSPITE")
o_f_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", value=10)
o_s_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", value=18)
o_g_s = st.sidebar.number_input("Partite Ospite (Stagione)", value=8)
st.sidebar.subheader("🔥 Forma (U5)")
o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", value=3)
o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", value=9)

st.sidebar.markdown("---")
st.sidebar.header("💰 QUOTE BOOKMAKER (1X2)")
q1_book = st.sidebar.number_input("Quota Segno 1", value=2.00, step=0.01)
qx_book = st.sidebar.number_input("Quota Segno X", value=3.20, step=0.01)
q2_book = st.sidebar.number_input("Quota Segno 2", value=3.50, step=0.01)

# --- CALCOLO MEDIE PESATE ---
def weighted(s_f, r_5, g_s):
    if g_s <= 0: return 0
    return ((s_f / g_s) * 0.4) + ((r_5 / 5) * 0.6)

exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2

# --- TABS ---
tab1, tab2 = st.tabs(["🎯 FT SCORE & MULTIGOL", "📊 BVS 2026 SYSTEM"])

with tab1:
    st.info(f"📊 **Baricentro Match:** Casa **{exp_c:.2f}** | Ospite **{exp_o:.2f}**")
    
    max_g = 6 
    matrix = np.zeros((max_g, max_g))
    prob_c_list = [poisson(exp_c, i) for i in range(max_g)]
    prob_o_list = [poisson(exp_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g):
            matrix[h, a] = prob_c_list[h] * prob_o_list[a]

    # LOGICA SCENARI
    s1 = f"{int(round(exp_c))}-{int(round(exp_o))}"
    s2 = f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}"
    s3 = f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"
    top_scen = list(dict.fromkeys([s1, s2, s3]))

    # Matrice e Classifica
    c_m1, c_m2 = st.columns([2, 1.2])
    with c_m1:
        st.subheader("📊 Matrice Probabilità")
        df_matrix = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)])
        st.dataframe(df_matrix.style.format("{:.1f}%").background_gradient(cmap='Greens', axis=None), height=245)
    with c_m2:
        st.subheader("🎯 Classifica Esatti")
        ris = []
        for h in range(max_g):
            for a in range(max_g):
                p = matrix[h, a]
                ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
        df_res = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
        df_res_styled = df_res.copy()
        df_res_styled["Prob. %"] = df_res["Prob"].map("{:.1f}%".format)
        df_res_styled["QF"] = df_res["QF"].map("{:.2f}".format)
        def highlight_row(row):
            return ['background-color: #ffff00; color: #000000; font-weight: bold'] * len(row) if row['Risultato'] in top_scen else [''] * len(row)
        st.dataframe(df_res_styled[["Risultato", "Prob. %", "QF"]].style.apply(highlight_row, axis=1), hide_index=True, height=245, use_container_width=True)

    # --- SCENARI (REINSERITI E CORRETTI) ---
    st.subheader("💡 Scenari Suggeriti dal Modello")
    c_sce = st.columns(4)
    for i, res_n in enumerate(top_scen):
        h_s, a_s = map(int, res_n.split('-'))
        p_s = matrix[h_s, a_s] * 100
        with c_sce[i]:
            st.metric(f"SCENARIO: {res_n}", f"{p_s:.1f}%", f"QF: {100/p_s:.2f}")

    # Mercati Principali
    st.subheader("📈 Esito Finale, Over & Goal")
    p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
    ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
    p_g = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
    m_c = st.columns(6)
    m_c[0].metric("Segno 1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
    m_c[1].metric("Segno X", f"{px:.1f}%", f"QF:{100/px:.2f}")
    m_c[2].metric("Segno 2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
    m_c[3].metric("Over 2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
    m_c[4].metric("GOAL", f"{p_g:.1f}%", f"QF:{100/p_g:.2f}")
    m_c[5].metric("NO GOAL", f"{100-p_g:.1f}%", f"QF:{100/(100-p_g):.2f}")

    # Multigol Partita
    st.subheader("🔢 Multigol Partita")
    def get_mg(low, high):
        return sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if low <= h+a <= high) * 100
    mg_l = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
    c_mg = st.columns(4)
    for i, mg in enumerate(mg_l):
        p_m = get_mg(mg[0], mg[1])
        c_mg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{p_m:.1f}%", f"QF:{100/p_m:.2f}")

    # Multigol Squadra e Doppia Chance
    st.markdown("---")
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.write("**🏠 MULTIGOL CASA**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_c_list[i] for i in range(l, h+1)) * 100
            st.metric(f"Casa {l}-{h}", f"{p:.1f}%", f"QF: {100/p:.2f}")
    with cd2:
        st.write("**🚀 MULTIGOL OSPITE**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_o_list[i] for i in range(l, h+1)) * 100
            st.metric(f"Ospite {l}-{h}", f"{p:.1f}%", f"QF: {100/p:.2f}")
    with cd3:
        st.write("**⚖️ DOPPIA CHANCE**")
        st.metric("1X", f"{(p1+px):.1f}%", f"QF:{100/(p1+px):.2f}")
        st.metric("X2", f"{(p2+px):.1f}%", f"QF:{100/(p2+px):.2f}")
        st.metric("12", f"{(p1+p2):.1f}%", f"QF:{100/(p1+p2):.2f}")

with tab2:
    st.subheader("📊 Analisi Valore BVS 2026")
    m_gf_c, m_gs_c = c_f_s/c_g_s if c_g_s>0 else 0, c_s_s/c_g_s if c_g_s>0 else 0
    m_gf_o, m_gs_o = o_f_s/o_g_s if o_g_s>0 else 0, o_s_s/o_g_s if o_g_s>0 else 0
    t1 = ((m_gf_c + m_gs_o) / 2) * 25
    t2 = ((m_gf_o + m_gs_c) / 2) * 25
    tx = 107.05 - t1 - t2
    b1, bx, b2 = t1*(106/107.05), tx*(106/107.05), t2*(106/107.05)
    qf1, qfx, qf2 = 100/b1, 100/bx, 100/b2

    cb1, cbx, cb2 = st.columns(3)
    with cb1:
        st.metric("SEGNO 1", f"{b1:.1f}%", f"QF: {qf1:.2f}")
        st.info("VALORE" if q1_book > qf1 else "NO VALUE")
    with cbx:
        st.metric("SEGNO X", f"{bx:.1f}%", f"QF: {qfx:.2f}")
        st.info("VALORE" if qx_book > qfx else "NO VALUE")
    with cb2:
        st.metric("SEGNO 2", f"{b2:.1f}%", f"QF: {qf2:.2f}")
        st.info("VALORE" if q2_book > qf2 else "NO VALUE")
