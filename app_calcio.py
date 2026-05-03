import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE DETECTOR PRO", page_icon="⚽", layout="wide")

# --- INIZIALIZZAZIONE DATABASE ---
if 'db_partite' not in st.session_state:
    st.session_state.db_partite = []

# --- CSS PER LOOK PROFESSIONALE E COMPATTO ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 10px; font-size: 1.5rem !important; }
    
    /* Rimpicciolisce sensibilmente le schede */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 16px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { font-size: 12px !important; }
    
    /* Pulsanti piccoli */
    .stButton>button { height: 24px !important; font-size: 10px !important; padding: 0px 5px !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

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
q1_b = st.sidebar.number_input("Quota 1", value=2.00)
qx_b = st.sidebar.number_input("Quota X", value=3.20)
q2_b = st.sidebar.number_input("Quota 2", value=3.50)

# --- CALCOLO MEDIE PESATE ---
def weighted(s_f, r_5, g_s):
    return ((s_f / (g_s if g_s>0 else 1)) * 0.4) + ((r_5 / 5) * 0.6)

exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2

# Nomi squadre per database
st.write("### 📝 NOME INCONTRO PER SALVATAGGIO")
cn1, cn2 = st.columns(2)
t_h = cn1.text_input("Casa", value="Team A")
t_o = cn2.text_input("Ospite", value="Team B")

def salva_in_db(pron):
    st.session_state.db_partite.append({'Gara': f"{t_h}-{t_o}", 'Scelta': pron, 'Esito': '⏳', 'Ora': pd.Timestamp.now().strftime("%H:%M")})
    st.toast("Inviato al Database!")

tab1, tab2, tab3 = st.tabs(["🎯 FT SCORE & MULTIGOL", "📊 POWER RATING SYSTEM", "📂 ARCHIVIO DATABASE"])

with tab1:
    st.info(f"📊 Baricentro: Casa {exp_c:.2f} | Ospite {exp_o:.2f}")
    max_g = 6 
    matrix = np.zeros((max_g, max_g))
    prob_c_l = [poisson(exp_c, i) for i in range(max_g)]
    prob_o_l = [poisson(exp_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g):
            matrix[h, a] = prob_c_l[h] * prob_o_l[a]

    s_list = [f"{int(round(exp_c))}-{int(round(exp_o))}", f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}", f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"]
    top_scen = list(dict.fromkeys(s_list))

    col1, col2 = st.columns([2, 1.2])
    with col1:
        st.subheader("📊 Matrice")
        df_m = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)])
        st.dataframe(df_m.style.format("{:.1f}%").background_gradient(cmap='Greens', axis=None), height=230)
    with col2:
        st.subheader("🎯 Classifica")
        ris = []
        for h in range(max_g):
            for a in range(max_g):
                p = matrix[h, a]
                ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
        df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
        def hl(r): return ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in top_scen else ['']*3
        st.dataframe(df_r[["Risultato", "Prob", "QF"]].style.apply(hl, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, height=230, use_container_width=True)

    # Scenari Esatti
    st.subheader("💡 Scenari Esatti")
    c_sce = st.columns(4)
    for i, res_n in enumerate(top_scen):
        p_s = matrix[int(res_n.split('-')[0]), int(res_n.split('-')[1])] * 100
        with c_sce[i]:
            st.metric(res_n, f"{p_s:.1f}%")
            if st.button("📌 Invia", key=f"s_{res_n}"): salva_in_db(f"Esatto {res_n}")

    # Combo Dinamiche
    st.subheader("🚀 Scenari Combo")
    def get_combo_p(c_min, c_max, o_min, o_max): return sum(matrix[h, a] for h in range(c_min, c_max+1) for a in range(o_min, o_max+1) if h<max_g and a<max_g) * 100
    r_c = (0,1) if exp_c < 1.2 else (1,3) if exp_c < 2.2 else (2,4)
    r_o = (0,1) if exp_o < 1.2 else (1,3) if exp_o < 2.2 else (2,4)
    
    c_bil = f"CASA {r_c[0]}-{r_c[1]} + OSPITE {r_o[0]}-{r_o[1]}"
    p_bil = get_combo_p(r_c[0], r_c[1], r_o[0], r_o[1])
    
    cc = st.columns(3)
    with cc[0]:
        st.metric("BILANCIATO", c_bil, f"{p_bil:.1f}%")
        if st.button("📌 Invia Bil"): salva_in_db(c_bil)
    with cc[1]:
        if exp_c >= exp_o:
            name, p = f"CASA {r_c[0]}-{r_c[1]} + OSPITE 0-1", get_combo_p(r_c[0], r_c[1], 0, 1)
            st.metric("DOMINIO CASA", name, f"{p:.1f}%")
            if st.button("📌 Invia Dom"): salva_in_db(name)
        else:
            name, p = f"CASA 0-1 + OSPITE {r_o[0]}-{r_o[1]}", get_combo_p(0, 1, r_o[0], r_o[1])
            st.metric("DOMINIO OSPITE", name, f"{p:.1f}%")
            if st.button("📌 Invia Dom"): salva_in_db(name)
    with cc[2]:
        p_g = get_combo_p(1,3,1,3)
        st.metric("COMBO GOAL", "CASA 1-3 + OSPITE 1-3", f"{p_g:.1f}%")
        if st.button("📌 Invia Goal"): salva_in_db("CASA 1-3 + OSPITE 1-3")

    # Mercati Principali
    st.subheader("📈 Mercati")
    p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
    ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
    pg = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
    m_c = st.columns(6)
    m_c[0].metric("1", f"{p1:.1f}%")
    m_c[1].metric("X", f"{px:.1f}%")
    m_c[2].metric("2", f"{p2:.1f}%")
    m_c[3].metric("Over 2.5", f"{ov25:.1f}%")
    m_c[4].metric("GOAL", f"{pg:.1f}%")
    m_c[5].metric("NO GOAL", f"{100-pg:.1f}%")

    # Multigol Partita
    st.subheader("🔢 Multigol Partita")
    def gm(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
    mg_l = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
    cmg = st.columns(4)
    for i, mg in enumerate(mg_l):
        p = gm(mg[0], mg[1])
        cmg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{p:.1f}%")

    # Multigol Squadra e Doppia Chance
    st.markdown("---")
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.write("**🏠 MG CASA**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_c_l[i] for i in range(l, h+1)) * 100
            st.metric(f"Casa {l}-{h}", f"{p:.1f}%")
    with cd2:
        st.write("**🚀 MG OSPITE**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_o_l[i] for i in range(l, h+1)) * 100
            st.metric(f"Ospite {l}-{h}", f"{p:.1f}%")
    with cd3:
        st.write("**⚖️ DOPPIA CHANCE**")
        st.metric("1X", f"{(p1+px):.1f}%")
        st.metric("X2", f"{(p2+px):.1f}%")
        st.metric("12", f"{(p1+p2):.1f}%")

with tab2:
    st.subheader("📊 Power Rating System")
    m_gf_c, m_gs_c = c_f_s/c_g_s if c_g_s>0 else 0, c_s_s/c_g_s if c_g_s>0 else 0
    m_gf_o, m_gs_o = o_f_s/o_g_s if o_g_s>0 else 0, o_s_s/o_g_s if o_g_s>0 else 0
    t1 = ((m_gf_c + m_gs_o) / 2) * 25
    t2 = ((m_gf_o + m_gs_c) / 2) * 25
    tx = 107.05 - t1 - t2
    b1, bx, b2 = t1*(106/107.05), tx*(106/107.05), t2*(106/107.05)
    qf1, qfx, qf2 = 100/b1, 100/bx, 100/b2
    v1, vx, v2 = st.columns(3)
    v1.metric("SEGNO 1", f"QF: {qf1:.2f}", "✅ VALORE" if q1_b > qf1 else "❌ NO")
    vx.metric("SEGNO X", f"QF: {qfx:.2f}", "✅ VALORE" if qx_b > qfx else "❌ NO")
    v2.metric("SEGNO 2", f"QF: {qf2:.2f}", "✅ VALORE" if q2_b > qf2 else "❌ NO")
    st.markdown("---")
    df_b = pd.DataFrame({"Segno": ["1", "X", "2"], "Prob. Teorica": [t1, tx, t2], "Prob. BVS": [b1, bx, b2], "Quota Book": [q1_b, qx_b, q2_b]})
    st.dataframe(df_b.style.highlight_max(subset=["Prob. BVS"], color="#dcfce7").format({"Prob. Teorica": "{:.2f}%", "Prob. BVS": "{:.2f}%"}), use_container_width=True)

with tab3:
    st.subheader("📂 Archivio Pronostici")
    if st.session_state.db_partite:
        for i, item in enumerate(st.session_state.db_partite):
            with st.expander(f"{item['Ora']} - {item['Gara']} ({item['Scelta']})", expanded=True):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 0.5])
                c1.write(f"**{item['Scelta']}** - Stato: **{item['Esito']}**")
                if c2.button("WIN ✅", key=f"w_{i}"): st.session_state.db_partite[i]['Esito'] = 'VINTO 💰'; st.rerun()
                if c3.button("LOSS ❌", key=f"l_{i}"): st.session_state.db_partite[i]['Esito'] = 'PERSO 📉'; st.rerun()
                if c4.button("🗑️", key=f"d_{i}"): st.session_state.db_partite.pop(i); st.rerun()
