import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE DETECTOR PRO", page_icon="⚽", layout="wide")

# --- DATABASE IN MEMORIA ---
if 'db' not in st.session_state:
    st.session_state.db = {} # Struttura: {'SquadraA-SquadraB': [{'scelta': '2-0', 'esito': '⏳'}, ...]}

# --- CSS PER TABELLA ORIZZONTALE E TASTI MINI ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 5px; font-size: 1.2rem !important; }
    
    /* Rimpicciolisce le schede */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid rgba(128, 128, 128, 0.1) !important;
        padding: 2px 5px !important;
        border-radius: 4px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 14px !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { font-size: 11px !important; }
    
    /* TASTO SALVA GREEN */
    div.stButton > button:first-child {
        background-color: #28a745 !important; color: white !important;
        font-weight: bold !important; border-radius: 5px !important;
        height: 35px !important; width: 100% !important; margin-top: 25px !important;
    }

    /* TASTI DATABASE MINI */
    .mini-btn button {
        height: 20px !important; width: 40px !important; font-size: 9px !important;
        padding: 0px !important; margin: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

# --- BLOCCO SALVATAGGIO ---
st.write("### 📝 REGISTRAZIONE INCONTRO")
c_t1, c_t2, c_btn = st.columns([3, 3, 1.5])
t_h = c_t1.text_input("Casa", value="Bologna")
t_o = c_t2.text_input("Ospite", value="Cagliari")
current_match = f"{t_h} - {t_o}"

if c_btn.button("💾 CREA RIGA"):
    if current_match not in st.session_state.db:
        st.session_state.db[current_match] = []
        st.success(f"Riga creata per {current_match}")

def add_to_db(match, pron):
    if match in st.session_state.db:
        st.session_state.db[match].append({'scelta': pron, 'esito': '⏳'})
        st.toast(f"Inviato: {pron}")
    else:
        st.error("Clicca prima su 'CREA RIGA' in alto!")

# --- SIDEBAR E CALCOLI ---
st.sidebar.header("🏠 DATI CASA")
c_f_s = st.sidebar.number_input("Gol Fatti Casa", value=15)
c_s_s = st.sidebar.number_input("Gol Subiti Casa", value=10)
c_g_s = st.sidebar.number_input("Partite Casa", value=8)
c_f_5 = st.sidebar.number_input("Gol Fatti (U5)", value=8)
c_s_5 = st.sidebar.number_input("Gol Subiti (U5)", value=4)
st.sidebar.markdown("---")
st.sidebar.header("🚀 DATI OSPITE")
o_f_s = st.sidebar.number_input("Gol Fatti Ospite", value=10)
o_s_s = st.sidebar.number_input("Gol Subiti Ospite", value=18)
o_g_s = st.sidebar.number_input("Partite Ospite", value=8)
o_f_5 = st.sidebar.number_input("Gol Fatti (U5)", value=3)
o_s_5 = st.sidebar.number_input("Gol Subiti (U5)", value=9)
st.sidebar.markdown("---")
q1_b, qx_b, q2_b = st.sidebar.number_input("Q1", 2.0), st.sidebar.number_input("QX", 3.0), st.sidebar.number_input("Q2", 4.0)

def weighted(s_f, r_5, g_s): return ((s_f / (g_s if g_s>0 else 1)) * 0.4) + ((r_5 / 5) * 0.6)
exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2

tab1, tab2, tab3 = st.tabs(["🎯 FT SCORE", "📊 POWER RATING", "📂 DATABASE"])

with tab1:
    st.info(f"📊 Baricentro: C {exp_c:.2f} | O {exp_o:.2f}")
    max_g = 6 
    matrix = np.zeros((max_g, max_g))
    prob_c_l = [poisson(exp_c, i) for i in range(max_g)]
    prob_o_l = [poisson(exp_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g): matrix[h, a] = prob_c_l[h] * prob_o_l[a]
    scen = list(dict.fromkeys([f"{int(round(exp_c))}-{int(round(exp_o))}", f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}", f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"]))

    c_c1, c_c2 = st.columns([2, 1.2])
    with c_c1:
        st.subheader("📊 Matrice")
        st.dataframe(pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)]).style.format("{:.1f}%").background_gradient(cmap='Greens', axis=None), height=230)
    with c_c2:
        st.subheader("🎯 Classifica")
        ris = []
        for h in range(max_g):
            for a in range(max_g):
                p = matrix[h, a]
                ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
        df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
        st.dataframe(df_r.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in scen else ['']*3, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, height=230, use_container_width=True)

    st.subheader("💡 Scenari Esatti")
    cols_s = st.columns(4)
    for i, r_n in enumerate(scen):
        p_val = matrix[int(r_n.split('-')[0]), int(r_n.split('-')[1])] * 100
        with cols_s[i]:
            st.metric("ESATTO", r_n, delta=f"{p_val:.1f}% (QF:{100/p_val:.2f})")
            if st.button(f"📌 Invia {r_n}"): add_to_db(current_match, f"Esatto {r_n}")

    st.subheader("🚀 Scenari Combo")
    def gp(cr, orr): return sum(matrix[h, a] for h in range(cr[0], cr[1]+1) for a in range(orr[0], orr[1]+1) if h<max_g and a<max_g) * 100
    rc = (0,1) if exp_c < 1.2 else (1,3) if exp_c < 2.2 else (2,4)
    ro = (0,1) if exp_o < 1.2 else (1,3) if exp_o < 2.2 else (2,4)
    
    cb = st.columns(3)
    p_bil, n_bil = gp(rc, ro), f"CASA {rc[0]}-{rc[1]} + OSPITE {ro[0]}-{ro[1]}"
    with cb[0]:
        st.metric("BILANCIATO", n_bil, delta=f"{p_bil:.1f}%")
        if st.button("📌 Invia Bil"): add_to_db(current_match, f"Bil: {n_bil}")
    if exp_c >= exp_o: lab_d, n_d, p_d = "DOMINIO CASA", f"CASA {rc[0]}-{rc[1]} + OSPITE 0-1", gp(rc, 0, 1)
    else: lab_d, n_d, p_d = "DOMINIO OSPITE", f"CASA 0-1 + OSPITE {ro[0]}-{ro[1]}", gp(0, 1, ro)
    with cb[1]:
        st.metric(lab_d, n_d, delta=f"{p_d:.1f}%")
        if st.button(f"📌 Invia {lab_d}"): add_to_db(current_match, f"Dom: {n_d}")
    p_go = gp(1,3,1,3)
    with cb[2]:
        st.metric("COMBO GOAL", "CASA 1-3 + OSPITE 1-3", delta=f"{p_go:.1f}%")
        if st.button("📌 Invia Goal"): add_to_db(current_match, "Combo Goal: 1-3 + 1-3")

    st.subheader("📈 Mercati")
    p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
    ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
    pg = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
    mc = st.columns(6)
    mc[0].metric("1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
    mc[1].metric("X", f"{px:.1f}%", f"QF:{100/px:.2f}")
    mc[2].metric("2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
    mc[3].metric("O2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
    mc[4].metric("GOAL", f"{pg:.1f}%", f"QF:{100/pg:.2f}")
    mc[5].metric("NO G", f"{100-pg:.1f}%", f"QF:{100/(100-pg):.2f}")

    def gmm(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
    mg_l = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
    cmg = st.columns(4)
    for i, mg in enumerate(mg_l): cmg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{gmm(mg[0], mg[1]):.1f}%")

    st.markdown("---")
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.write("**🏠 MG CASA**")
        for l, h in [(1,2), (1,3), (2,3)]: st.metric(f"Casa {l}-{h}", f"{sum(prob_c_l[i] for i in range(l, h+1))*100:.1f}%")
    with cd2:
        st.write("**🚀 MG OSPITE**")
        for l, h in [(1,2), (1,3), (2,3)]: st.metric(f"Ospite {l}-{h}", f"{sum(prob_o_l[i] for i in range(l, h+1))*100:.1f}%")
    with cd3:
        st.write("**⚖️ DC**")
        st.metric("1X", f"{(p1+px):.1f}%"); st.metric("X2", f"{(p2+px):.1f}%"); st.metric("12", f"{(p1+p2):.1f}%")

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
    v1.metric("SEGNO 1", f"QF: {qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO")
    vx.metric("SEGNO X", f"QF: {qfx:.2f}", "✅ VALUE" if qx_b > qfx else "❌ NO")
    v2.metric("SEGNO 2", f"QF: {qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")
    st.dataframe(pd.DataFrame({"Segno": ["1", "X", "2"], "Prob. BVS": [b1, bx, b2], "Quota Book": [q1_b, qx_b, q2_b]}).style.format({"Prob. BVS": "{:.2f}%"}), use_container_width=True)

with tab3:
    st.subheader("📂 Tabella Database")
    if st.session_state.db:
        # Intestazione Tabella
        h1, h2, h3 = st.columns([2, 5, 1])
        h1.write("**PARTITA**")
        h2.write("**PRONOSTICI E ESITI**")
        h3.write("**CANC**")
        st.markdown("---")
        
        for match_name, pronostici in list(st.session_state.db.items()):
            r1, r2, r3 = st.columns([2, 5, 1])
            r1.write(f"**{match_name}**")
            
            with r2:
                # Mostra i pronostici della partita in orizzontale
                for j, p in enumerate(pronostici):
                    c_p, c_w, c_l = st.columns([3, 1, 1])
                    color = "🟢" if p['esito'] == 'WIN' else "🔴" if p['esito'] == 'LOSS' else "⏳"
                    c_p.write(f"{color} {p['scelta']}")
                    if c_w.button("W", key=f"w_{match_name}_{j}"): 
                        st.session_state.db[match_name][j]['esito'] = 'WIN'; st.rerun()
                    if c_l.button("L", key=f"l_{match_name}_{j}"): 
                        st.session_state.db[match_name][j]['esito'] = 'LOSS'; st.rerun()
            
            if r3.button("🗑️", key=f"del_{match_name}"):
                del st.session_state.db[match_name]
                st.rerun()
            st.markdown("---")
    else:
        st.write("Nessun incontro in database.")
