import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE & DATABASE PRO", page_icon="⚽", layout="wide")

# --- INIZIALIZZAZIONE DATABASE ---
if 'db_partite' not in st.session_state:
    st.session_state.db_partite = []

# --- CSS PER LOOK PROFESSIONALE ---
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
    .stButton>button { width: 100%; border-radius: 5px; height: 30px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

# --- SIDEBAR SUPERIORE ---
st.write("### 📝 REGISTRAZIONE NUOVO INCONTRO")
c_n1, c_n2, c_n3 = st.columns([3, 3, 1])
t_home = c_n1.text_input("Squadra Casa", placeholder="es. Udinese", key="t_home")
t_away = c_n2.text_input("Squadra Ospite", placeholder="es. Torino", key="t_away")

# --- SIDEBAR LATERALE (DATI) ---
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
    return ((s_f / (g_s if g_s>0 else 1)) * 0.4) + ((r_5 / 5) * 0.6)

exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2

# Funzione per salvare nel DB
def salva_pronostico(pronostico_scelto):
    if t_home and t_away:
        st.session_state.db_partite.append({
            'Incontro': f"{t_home}-{t_away}",
            'Pronostico': pronostico_scelto,
            'Esito': '⏳ In corso',
            'Data': pd.Timestamp.now().strftime("%d/%m %H:%M")
        })
        st.toast(f"Salvato: {pronostico_scelto}")
    else:
        st.error("Inserisci prima i nomi delle squadre in alto!")

tab1, tab2, tab3 = st.tabs(["🎯 FT SCORE & MULTIGOL", "📊 POWER RATING SYSTEM", "📂 ARCHIVIO DATABASE"])

with tab1:
    st.info(f"📊 **Baricentro Match:** Casa **{exp_c:.2f}** | Ospite **{exp_o:.2f}**")
    max_g = 6 
    matrix = np.zeros((max_g, max_g))
    prob_c_l = [poisson(exp_c, i) for i in range(max_g)]
    prob_o_l = [poisson(exp_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g):
            matrix[h, a] = prob_c_l[h] * prob_o_l[a]

    s1, s2, s3 = f"{int(round(exp_c))}-{int(round(exp_o))}", f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}", f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"
    top_scen = list(dict.fromkeys([s1, s2, s3]))

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
        def hl(r): return ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in top_scen else ['']*3
        st.dataframe(df_r[["Risultato", "Prob", "QF"]].style.apply(hl, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, height=245, use_container_width=True)

    # SCENARI ESATTI
    st.subheader("💡 Scenari Risultati Esatti")
    c_sce = st.columns(4)
    for i, res_n in enumerate(top_scen):
        h_s, a_s = map(int, res_n.split('-'))
        p_s = matrix[h_s, a_s] * 100
        with c_sce[i]:
            st.metric(f"ESATTO: {res_n}", f"{p_s:.1f}%", f"QF: {100/p_s:.2f}")
            if st.button(f"📌 Invia {res_n}", key=f"btn_res_{res_n}"): salva_pronostico(f"Esatto {res_n}")

    # SCENARI COMBO
    st.subheader("🚀 Scenari Combo Multigol")
    def get_combo_p(c_r, o_r): return sum(matrix[h, a] for h in range(c_r[0], c_r[1]+1) for a in range(o_r[0], o_r[1]+1) if h < max_g and a < max_g) * 100
    def get_range(mu):
        if mu < 1.2: return (0, 1)
        if mu < 2.2: return (1, 3)
        return (2, 4)
    r_c, r_o = get_range(exp_c), get_range(exp_o)
    
    p_bil = get_combo_p(r_c, r_o)
    name_bil = f"CASA {r_c[0]}-{r_c[1]} + OSPITE {r_o[0]}-{r_o[1]}"
    
    if exp_c >= exp_o:
        label_dom, name_dom, p_dom = "DOMINIO CASA", f"CASA {r_c[0]}-{r_c[1]} + OSPITE 0-1", get_combo_p(r_c, (0, 1))
    else:
        label_dom, name_dom, p_dom = "DOMINIO OSPITE", f"CASA 0-1 + OSPITE {r_o[0]}-{r_o[1]}", get_combo_p((0, 1), r_o)
    
    p_goal_over = get_combo_p((1, 3), (1, 3))
    
    cc = st.columns(3)
    with cc[0]:
        st.metric("BILANCIATO", name_bil, f"{p_bil:.1f}%")
        if st.button("📌 Invia Bilanciato"): salva_pronostico(name_bil)
    with cc[1]:
        st.metric(label_dom, name_dom, f"{p_dom:.1f}%")
        if st.button(f"📌 Invia {label_dom}"): salva_pronostico(name_dom)
    with cc[2]:
        st.metric("COMBO GOAL", "CASA 1-3 + OSPITE 1-3", f"{p_goal_over:.1f}%")
        if st.button("📌 Invia Goal"): salva_pronostico("CASA 1-3 + OSPITE 1-3")

    # --- MERCATI ---
    st.subheader("📈 Mercati Principali")
    p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
    ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
    pg = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
    mc = st.columns(6)
    mc[0].metric("Segno 1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
    mc[1].metric("Segno X", f"{px:.1f}%", f"QF:{100/px:.2f}")
    mc[2].metric("Segno 2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
    mc[3].metric("Over 2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
    mc[4].metric("GOAL", f"{pg:.1f}%", f"QF:{100/pg:.2f}")
    mc[5].metric("NO GOAL", f"{100-pg:.1f}%", f"QF:{100/(100-pg):.2f}")

with tab2:
    st.subheader("📊 Analisi Power Rating System")
    m_gf_c, m_gs_c = c_f_s/c_g_s if c_g_s>0 else 0, c_s_s/c_g_s if c_g_s>0 else 0
    m_gf_o, m_gs_o = o_f_s/o_g_s if o_g_s>0 else 0, o_s_s/o_g_s if o_g_s>0 else 0
    t1 = ((m_gf_c + m_gs_o) / 2) * 25
    t2 = ((m_gf_o + m_gs_c) / 2) * 25
    tx = 107.05 - t1 - t2
    b1, bx, b2 = t1*(106/107.05), tx*(106/107.05), t2*(106/107.05)
    qf1, qfx, qf2 = 100/b1, 100/bx, 100/b2
    
    bv1, bvx, bv2 = st.columns(3)
    bv1.metric("SEGNO 1", f"QF: {qf1:.2f}", "VALORE ✅" if q1_b > qf1 else "NO VALUE ❌")
    bvx.metric("SEGNO X", f"QF: {qfx:.2f}", "VALORE ✅" if qx_b > qfx else "NO VALUE ❌")
    bv2.metric("SEGNO 2", f"QF: {qf2:.2f}", "VALORE ✅" if q2_b > qf2 else "NO VALUE ❌")
    
    st.markdown("---")
    bvs_df = pd.DataFrame({"Segno": ["1", "X", "2"], "Prob. Teorica": [t1, tx, t2], "Prob. BVS": [b1, bx, b2], "Quota Book": [q1_b, qx_b, q2_b]})
    st.dataframe(bvs_df.style.highlight_max(subset=["Prob. BVS"], color="#dcfce7").format({"Prob. Teorica": "{:.2f}%", "Prob. BVS": "{:.2f}%", "Quota Book": "{:.2f}"}), hide_index=True, use_container_width=True)

with tab3:
    st.subheader("📂 Database Incontri")
    if st.session_state.db_partite:
        for i, p in enumerate(st.session_state.db_partite):
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 1.5, 0.5])
                c1.write(p['Data'])
                c2.write(f"**{p['Incontro']}**")
                c3.write(f"Pronostico: {p['Pronostico']}")
                c4.write(f"Stato: {p['Esito']}")
                if c5.button("🗑️", key=f"del_{i}"):
                    st.session_state.db_partite.pop(i)
                    st.rerun()
                
                col_w, col_l = st.columns([1, 1])
                if col_w.button(f"WIN ✅", key=f"win_{i}"): st.session_state.db_partite[i]['Esito'] = '💰 VINTO'
                if col_l.button(f"LOSS ❌", key=f"loss_{i}"): st.session_state.db_partite[i]['Esito'] = '📉 PERSO'
                st.markdown("---")
    else:
        st.write("Ancora nessun pronostico inviato all'archivio.")
