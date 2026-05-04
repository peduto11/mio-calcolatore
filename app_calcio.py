import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE DETECTOR PRO", page_icon="⚽", layout="wide")

# --- MEMORIA DATABASE ---
if 'db' not in st.session_state:
    st.session_state.db = {}

# --- CSS LOOK PROFESSIONALE E FIX BOTTONI ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 5px; font-size: 1.2rem !important; }
    
    /* Stile Metriche */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid rgba(128, 128, 128, 0.1) !important;
        padding: 4px 8px !important; border-radius: 6px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 15px !important; font-weight: bold !important; }
    
    /* TASTO SALVA GREEN (Applicato SOLO al tasto Primary) */
    button[kind="primary"] {
        background-color: #28a745 !important; color: white !important;
        font-weight: bold !important; border-radius: 6px !important;
        height: 38px !important; width: 100% !important; margin-top: 25px !important;
    }
    
    /* Divisori più compatti */
    hr { margin: 0.5em 0 !important; border: 1px solid rgba(128,128,128,0.2) !important; }
    
    /* Allineamento verticale per il testo nella tabella */
    .table-text { margin-top: 8px; font-size: 14px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

# --- REGISTRAZIONE INCONTRO ---
st.write("### 📝 REGISTRAZIONE INCONTRO")
c_t1, c_t2, c_btn = st.columns([3, 3, 1.5])
t_h = c_t1.text_input("Squadra Casa", value="Bologna")
t_o = c_t2.text_input("Squadra Ospite", value="Cagliari")
match_name = f"{t_h} - {t_o}"

if c_btn.button("💾 SALVA INCONTRO", type="primary"):
    if match_name not in st.session_state.db:
        st.session_state.db[match_name] = []
        st.toast("Partita creata nel Database!")

def add_to_db(pron):
    if match_name in st.session_state.db:
        st.session_state.db[match_name].append({'scelta': pron, 'esito': '⏳'})
        st.toast(f"Inviato: {pron}")
    else: 
        st.error("Clicca prima su SALVA INCONTRO per creare la riga!")

# --- SIDEBAR (CORRETTA) ---
st.sidebar.header("🏠 DATI CASA")
c_f_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", min_value=0, value=15)
c_s_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", min_value=0, value=10)
c_g_s = st.sidebar.number_input("Partite Casa (Stagione)", min_value=1, value=8)
st.sidebar.subheader("🔥 Forma (U5)")
c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", min_value=0, value=8)
c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", min_value=0, value=4)
st.sidebar.markdown("---")
st.sidebar.header("🚀 DATI OSPITE")
o_f_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", min_value=0, value=10)
o_s_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", min_value=0, value=18)
o_g_s = st.sidebar.number_input("Partite Ospite (Stagione)", min_value=1, value=8)
st.sidebar.subheader("🔥 Forma (U5)")
o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", min_value=0, value=3)
o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", min_value=0, value=9)
st.sidebar.markdown("---")
q1_b = st.sidebar.number_input("Quota 1", min_value=1.00, value=2.00, step=0.10)
qx_b = st.sidebar.number_input("Quota X", min_value=1.00, value=3.20, step=0.10)
q2_b = st.sidebar.number_input("Quota 2", min_value=1.00, value=3.50, step=0.10)

# --- CALCOLI ---
def w_avg(sf, r5, gs): return ((sf / (gs if gs>0 else 1)) * 0.4) + ((r5 / 5) * 0.6)
ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2

st.title("⚽ FT SCORE DETECTOR & MULTIGOL PRO")
tab1, tab2, tab3 = st.tabs(["🎯 FT SCORE", "📊 POWER RATING", "📂 DATABASE"])

with tab1:
    st.info(f"📊 Baricentro: Casa {ex_c:.2f} | Ospite {ex_o:.2f}")
    max_g = 6; matrix = np.zeros((max_g, max_g))
    pc = [poisson(ex_c, i) for i in range(max_g)]; po = [poisson(ex_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g): matrix[h, a] = pc[h] * po[a]
    scen = list(dict.fromkeys([f"{int(round(ex_c))}-{int(round(ex_o))}", f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}", f"{int(math.floor(ex_c))}-{int(math.ceil(ex_o))}"]))

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
    cs = st.columns(4)
    for i, rn in enumerate(scen):
        pv = matrix[int(rn.split('-')[0]), int(rn.split('-')[1])] * 100
        with cs[i]:
            st.metric("ESATTO", rn, delta=f"{pv:.1f}% (QF:{100/pv:.2f})")
            if st.button(f"📌 Invia {rn}", key=f"s_{i}"): add_to_db(f"Esatto {rn}")

    st.subheader("🚀 Scenari Combo")
    def gp(cmin, cmax, omin, omax): return sum(matrix[h, a] for h in range(cmin, cmax+1) for a in range(omin, omax+1) if h<max_g and a<max_g) * 100
    rc = (0,1) if ex_c < 1.2 else (1,3) if ex_c < 2.2 else (2,4)
    ro = (0,1) if ex_o < 1.2 else (1,3) if ex_o < 2.2 else (2,4)
    cb = st.columns(3)
    p_bi, n_bi = gp(rc[0], rc[1], ro[0], ro[1]), f"CASA {rc[0]}-{rc[1]} + OSPITE {ro[0]}-{ro[1]}"
    with cb[0]:
        st.metric("BILANCIATO", n_bi, delta=f"{p_bi:.1f}% (QF:{100/p_bi:.2f})")
        if st.button("📌 Invia Bil"): add_to_db(f"Bil: {n_bi}")
    if ex_c >= ex_o: lab_d, n_d, p_d = "DOMINIO CASA", f"CASA {rc[0]}-{rc[1]} + OSPITE 0-1", gp(rc[0], rc[1], 0, 1)
    else: lab_d, n_d, p_d = "DOMINIO OSPITE", f"CASA 0-1 + OSPITE {ro[0]}-{ro[1]}", gp(0, 1, ro[0], ro[1])
    with cb[1]:
        st.metric(lab_d, n_d, delta=f"{p_d:.1f}% (QF:{100/p_d:.2f})")
        if st.button(f"📌 Invia Dom"): add_to_db(f"Dom: {n_d}")
    p_go = gp(1,3,1,3)
    with cb[2]:
        st.metric("COMBO GOAL", "CASA 1-3 + OSPITE 1-3", delta=f"{p_go:.1f}% (QF:{100/p_go:.2f})")
        if st.button("📌 Invia Goal"): add_to_db("Goal: CASA 1-3 + OSPITE 1-3")

    st.subheader("📈 Mercati")
    p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
    ov, pg = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100, sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
    mc = st.columns(6)
    mc[0].metric("1", f"{p1:.1f}%", f"QF:{100/p1:.2f}"); mc[1].metric("X", f"{px:.1f}%", f"QF:{100/px:.2f}"); mc[2].metric("2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
    mc[3].metric("O2.5", f"{ov:.1f}%", f"QF:{100/ov:.2f}"); mc[4].metric("GOAL", f"{pg:.1f}%", f"QF:{100/pg:.2f}"); mc[5].metric("NO G", f"{100-pg:.1f}%", f"QF:{100/(100-pg):.2f}")
    cmg = st.columns(4)
    def gmm(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
    for i, mg in enumerate([(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]):
        val_mg = gmm(mg[0], mg[1])
        cmg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{val_mg:.1f}%", f"QF:{100/val_mg:.2f}")

    st.markdown("---")
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.write("**🏠 MG CASA**")
        for l, h in [(1,2), (1,3), (2,3)]:
            pr = sum(pc[i] for i in range(l, h+1))*100
            st.metric(f"Casa {l}-{h}", f"{pr:.1f}%", f"QF:{100/pr*100:.2f}" if pr>0 else "0")
    with cd2:
        st.write("**🚀 MG OSPITE**")
        for l, h in [(1,2), (1,3), (2,3)]:
            pr = sum(po[i] for i in range(l, h+1))*100
            st.metric(f"Ospite {l}-{h}", f"{pr:.1f}%", f"QF:{100/pr*100:.2f}" if pr>0 else "0")
    with cd3:
        st.write("**⚖️ DC**")
        st.metric("1X", f"{(p1+px):.1f}%", f"QF:{100/(p1+px):.2f}"); st.metric("X2", f"{(p2+px):.1f}%", f"QF:{100/(p2+px):.2f}"); st.metric("12", f"{(p1+p2):.1f}%", f"QF:{100/(p1+p2):.2f}")

with tab2:
    st.subheader("📊 Power Rating System")
    t1 = ((c_f_s/c_g_s + o_s_s/o_g_s)/2)*25; t2 = ((o_f_s/o_g_s + c_s_s/c_g_s)/2)*25; tx = 107.05 - t1 - t2
    b1, bx, b2 = t1*(106/107.05), tx*(106/107.05), t2*(106/107.05)
    qf1, qfx, qf2 = 100/b1, 100/bx, 100/b2
    v1, vx, v2 = st.columns(3)
    v1.metric("SEGNO 1", f"QF: {qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO")
    vx.metric("SEGNO X", f"QF: {qfx:.2f}", "✅ VALUE" if qx_b > qfx else "❌ NO")
    v2.metric("SEGNO 2", f"QF: {qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")
    st.dataframe(pd.DataFrame({"Segno":["1","X","2"],"Prob BVS":[b1,bx,b2],"Q Book":[q1_b,qx_b,q2_b]}).style.highlight_max(subset=["Prob BVS"], color="#dcfce7").format({"Prob BVS":"{:.2f}%"}), use_container_width=True)

with tab3:
    st.subheader("📂 Tabella Database")
    
    if st.session_state.db:
        for m, prs in list(st.session_state.db.items()):
            st.markdown("---") 
            
            if not prs:
                col_m, col_m_del, _ = st.columns([2, 1, 7])
                col_m.markdown(f"<div class='table-text'><b>{m}</b></div>", unsafe_allow_html=True)
                if col_m_del.button("🗑️ Rimuovi Partita", key=f"del_match_{m}"):
                    del st.session_state.db[m]; st.rerun()
            else:
                cols = st.columns([2] + [3] * len(prs))
                
                with cols[0]:
                    c_name, c_del = st.columns([3, 1])
                    c_name.markdown(f"<div class='table-text'><b>{m}</b></div>", unsafe_allow_html=True)
                    if c_del.button("🗑️", key=f"del_m_{m}", help="Elimina l'intera partita"):
                        del st.session_state.db[m]; st.rerun()
                
                for idx, p in enumerate(prs):
                    with cols[idx + 1]:
                        cp_testo, cp_toggle, cp_cestino = st.columns([4, 3, 1.5])
                        
                        cp_testo.markdown(f"<div class='table-text'>{p['scelta']}</div>", unsafe_allow_html=True)
                        
                        esito = p['esito']
                        if esito == '⏳':
                            if cp_toggle.button("⚪ WAIT", key=f"tog_{m}_{idx}", help="Clicca per mettere WIN"):
                                st.session_state.db[m][idx]['esito'] = 'WIN'; st.rerun()
                        elif esito == 'WIN':
                            if cp_toggle.button("🟢 WIN", key=f"tog_{m}_{idx}", help="Clicca per mettere LOSS"):
                                st.session_state.db[m][idx]['esito'] = 'LOSS'; st.rerun()
                        elif esito == 'LOSS':
                            if cp_toggle.button("🔴 LOSS", key=f"tog_{m}_{idx}", help="Clicca per tornare a WAIT"):
                                st.session_state.db[m][idx]['esito'] = '⏳'; st.rerun()
                        
                        if cp_cestino.button("🗑️", key=f"del_p_{m}_{idx}", help="Elimina solo questo pronostico"):
                            st.session_state.db[m].pop(idx); st.rerun()
    else:
        st.info("Database vuoto. Salva un incontro e invia dei pronostici per iniziare.")
