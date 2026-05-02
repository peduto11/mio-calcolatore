import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE & BVS 2026 PRO", layout="wide")

# --- CSS PER LOOK PROFESSIONALE E COMPATTO ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 10px; }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 10px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: bold !important; }
    .value-box { padding: 20px; border-radius: 10px; border: 2px solid #00ff88; background-color: rgba(0, 255, 136, 0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.title("⚽ FT SCORE DETECTOR & BVS 2026 PRO")

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
st.sidebar.header("💰 QUOTE BOOKMAKER")
q1_b = st.sidebar.number_input("Quota 1", value=2.00)
qx_b = st.sidebar.number_input("Quota X", value=3.20)
q2_b = st.sidebar.number_input("Quota 2", value=3.50)

# --- CALCOLO MEDIE ---
def weighted(s_f, r_5, g_s):
    if g_s <= 0: return 0
    return ((s_f / g_s) * 0.4) + ((r_5 / 5) * 0.6)

exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2

# --- TABS ---
tab1, tab2 = st.tabs(["🎯 FT SCORE & MULTIGOL", "📊 BVS 2026 VALUE ANALYZER"])

with tab1:
    st.info(f"📊 **Baricentro Match:** Casa **{exp_c:.2f}** | Ospite **{exp_o:.2f}**")
    max_g = 6 
    matrix = np.zeros((max_g, max_g))
    prob_c_l = [poisson(exp_c, i) for i in range(max_g)]
    prob_o_l = [poisson(exp_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g):
            matrix[h, a] = prob_c_l[h] * prob_o_l[a]

    s_list = [f"{int(round(exp_c))}-{int(round(exp_o))}", f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}", f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"]
    top_scen = list(dict.fromkeys(s_list))

    c_m1, c_m2 = st.columns([2, 1.2])
    with c_m1:
        st.subheader("📊 Matrice Probabilità")
        df_m = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)])
        st.dataframe(df_m.style.format("{:.1f}%").background_gradient(cmap='Greens', axis=None), height=245)
    with c_m2:
        st.subheader("🎯 Classifica Esatti")
        ris = []
        for h in range(max_g):
            for a in range(max_g):
                p = matrix[h, a]
                ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
        df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
        df_r["Prob. %"] = df_r["Prob"].map("{:.1f}%".format)
        df_r["QF"] = df_r["QF"].map("{:.2f}".format)
        st.dataframe(df_r[["Risultato", "Prob. %", "QF"]].style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in top_scen else ['']*3, axis=1), hide_index=True, height=245, use_container_width=True)

    st.subheader("📈 Mercati Principali")
    p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
    ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
    p_g = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
    mc = st.columns(6)
    mc[0].metric("Segno 1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
    mc[1].metric("Segno X", f"{px:.1f}%", f"QF:{100/px:.2f}")
    mc[2].metric("Segno 2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
    mc[3].metric("Over 2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
    mc[4].metric("GOAL", f"{p_g:.1f}%", f"QF:{100/p_g:.2f}")
    mc[5].metric("NO GOAL", f"{100-p_g:.1f}%", f"QF:{100/(100-p_g):.2f}")

    st.subheader("🔢 Multigol Partita")
    def get_mg(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
    mg_l = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
    cmg = st.columns(4)
    for i, mg in enumerate(mg_l):
        p = get_mg(mg[0], mg[1])
        cmg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{p:.1f}%", f"QF:{100/p:.2f}")

    st.markdown("---")
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.write("**🏠 MULTIGOL CASA**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_c_l[i] for i in range(l, h+1)) * 100
            st.metric(f"Casa {l}-{h}", f"{p:.1f}%", f"QF: {100/p:.2f}")
    with cd2:
        st.write("**🚀 MULTIGOL OSPITE**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_o_l[i] for i in range(l, h+1)) * 100
            st.metric(f"Ospite {l}-{h}", f"{p:.1f}%", f"QF: {100/p:.2f}")
    with cd3:
        st.write("**⚖️ DOPPIA CHANCE**")
        st.metric("1X", f"{(p1+px):.1f}%", f"QF:{100/(p1+px):.2f}")
        st.metric("X2", f"{(p2+px):.1f}%", f"QF:{100/(p2+px):.2f}")
        st.metric("12", f"{(p1+p2):.1f}%", f"QF:{100/(p1+p2):.2f}")

with tab2:
    st.subheader("📊 BVS 2026: Rilevatore di Valore (1X2)")
    
    # Logica BVS specifica
    m_gf_c, m_gs_c = c_f_s/c_g_s if c_g_s>0 else 0, c_s_s/c_g_s if c_g_s>0 else 0
    m_gf_o, m_gs_o = o_f_s/o_g_s if o_g_s>0 else 0, o_s_s/o_g_s if o_g_s>0 else 0
    t1 = ((m_gf_c + m_gs_o) / 2) * 25
    t2 = ((m_gf_o + m_gs_c) / 2) * 25
    tx = 107.05 - t1 - t2
    b1, bx, b2 = t1*(106/107.05), tx*(106/107.05), t2*(106/107.05)
    qf1, qfx, qf2 = 100/b1, 100/bx, 100/b2

    # Visualizzazione a Schede (Cards)
    c_b1, c_bx, c_b2 = st.columns(3)
    
    with c_b1:
        val1 = "✅ VALORE" if q1_b > qf1 else "❌ NO VALUE"
        st.metric("SEGNO 1", f"{b1:.1f}%", f"QF: {qf1:.2f}")
        st.write(f"**Bookmaker: {q1_b}**")
        st.caption(val1)

    with c_bx:
        valx = "✅ VALORE" if qx_b > qfx else "❌ NO VALUE"
        st.metric("SEGNO X", f"{bx:.1f}%", f"QF: {qfx:.2f}")
        st.write(f"**Bookmaker: {qx_b}**")
        st.caption(valx)

    with c_b2:
        val2 = "✅ VALORE" if q2_b > qf2 else "❌ NO VALUE"
        st.metric("SEGNO 2", f"{b2:.1f}%", f"QF: {qf2:.2f}")
        st.write(f"**Bookmaker: {q2_b}**")
        st.caption(val2)

    # SENTENZA FINALE BVS
    st.markdown("---")
    st.subheader("⚖️ Sentenza del Modello BVS 2026")
    
    # Trova il miglior valore
    diffs = [q1_b - qf1, qx_b - qfx, q2_b - qf2]
    best_idx = np.argmax(diffs)
    best_bet = ["Segno 1", "Segno X", "Segno 2"][best_idx]
    
    if diffs[best_idx] > 0:
        st.success(f"🎯 **SCOMMESSA CONSIGLIATA:** Il miglior valore è sul **{best_bet}** (Vantaggio: +{diffs[best_idx]:.2f} punti di quota)")
    else:
        st.error("⚠️ **ATTENZIONE:** Il bookmaker ha quote troppo basse su tutti i segni. Nessun valore trovato.")
