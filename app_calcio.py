import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE & BVS 2026 PRO", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 10px; }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 5px 10px !important;
        border-radius: 8px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ FT SCORE DETECTOR & BVS 2026 PRO")

# --- SIDEBAR UNICA ---
st.sidebar.header("🏠 DATI CASA (Stagione)")
c_f_s = st.sidebar.number_input("Gol Fatti Casa", value=15)
c_s_s = st.sidebar.number_input("Gol Subiti Casa", value=10)
c_g_s = st.sidebar.number_input("Partite Casa", value=8)
st.sidebar.subheader("🔥 Forma (U5)")
c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", value=8)
c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", value=4)

st.sidebar.markdown("---")

st.sidebar.header("🚀 DATI OSPITE (Stagione)")
o_f_s = st.sidebar.number_input("Gol Fatti Ospite", value=10)
o_s_s = st.sidebar.number_input("Gol Subiti Ospite", value=18)
o_g_s = st.sidebar.number_input("Partite Ospite", value=8)
st.sidebar.subheader("🔥 Forma (U5)")
o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", value=3)
o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", value=9)

st.sidebar.markdown("---")
st.sidebar.header("💰 QUOTE BOOKMAKER")
q1_book = st.sidebar.number_input("Quota Segno 1", value=2.10, step=0.01)
qx_book = st.sidebar.number_input("Quota Segno X", value=3.20, step=0.01)
q2_book = st.sidebar.number_input("Quota Segno 2", value=3.50, step=0.01)

# --- CALCOLO MEDIE ---
def weighted(s_f, r_5, g_s):
    if g_s <= 0: return 0
    return ((s_f / g_s) * 0.4) + ((r_5 / 5) * 0.6)

exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2

# --- CREAZIONE TAB ---
tab1, tab2 = st.tabs(["🎯 FT SCORE & MULTIGOL", "📊 BVS 2026 SYSTEM"])

# ==========================================
# SCHEDA 1: POISSON ENGINE
# ==========================================
with tab1:
    st.info(f"📊 **Baricentro:** Casa **{exp_c:.2f}** | Ospite **{exp_o:.2f}**")
    max_g = 6 
    matrix = np.zeros((max_g, max_g))
    for h in range(max_g):
        for a in range(max_g):
            matrix[h, a] = poisson(exp_c, h) * poisson(exp_o, a)

    s1, s2, s3 = f"{int(round(exp_c))}-{int(round(exp_o))}", f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}", f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"
    top_scenarios_list = [s1, s2, s3]

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

    # --- MERCATI 1X2 POISSON ---
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

# ==========================================
# SCHEDA 2: BVS 2026 SYSTEM (LOGICA EXCEL CON QUOTE)
# ==========================================
with tab2:
    st.subheader("📊 Confronto Quote e Analisi Valore (BVS 2026)")
    
    def calc_bvs_logic(gf_c, gs_c, gp_c, gf_o, gs_o, gp_o):
        m_gf_c, m_gs_c = gf_c/gp_c if gp_c>0 else 0, gs_c/gp_c if gp_c>0 else 0
        m_gf_o, m_gs_o = gf_o/gp_o if gp_o>0 else 0, gs_o/gp_o if gp_o>0 else 0
        t1 = ((m_gf_c + m_gs_o) / 2) * 25
        t2 = ((m_gf_o + m_gs_c) / 2) * 25
        tx = 107.05 - t1 - t2
        return [t1*(106/107.05), tx*(106/107.05), t2*(106/107.05)]

    b_p1, b_px, b_p2 = calc_bvs_logic(c_f_s, c_s_s, c_g_s, o_f_s, o_s_s, o_g_s)
    q_b1, q_bx, q_b2 = 100/b_p1, 100/b_px, 100/b_p2

    # Tabella di confronto
    data_bvs = {
        "Segno": ["1", "X", "2"],
        "Probabilità BVS": [f"{b_p1:.2f}%", f"{b_px:.2f}%", f"{b_p2:.2f}%"],
        "Quota Fair BVS": [round(q_b1, 2), round(q_bx, 2), round(q_b2, 2)],
        "Quota Bookmaker": [q1_book, qx_book, q2_book],
        "VALUE?": [
            "✅ SI" if q1_book > q_b1 else "❌ NO",
            "✅ SI" if qx_book > q_bx else "❌ NO",
            "✅ SI" if q2_book > q_b2 else "❌ NO"
        ]
    }
    df_bvs = pd.DataFrame(data_bvs)
    
    st.table(df_bvs)
    
    st.info("💡 **Come leggere questa tabella:** Se vedi '✅ SI', significa che la quota del bookmaker è più alta della quota teorica BVS. Quello è il segno su cui conviene puntare.")
