import streamlit as st
import math
import pandas as pd
import numpy as np
import re

# Configurazione Pagina
st.set_page_config(page_title="SPORTS LAB PRO", page_icon="🔬", layout="wide")

# --- INIZIALIZZAZIONE MEMORIA (Per Auto-Update Sidebar) ---
if 'db' not in st.session_state: st.session_state.db = {}
if 'p1_vals' not in st.session_state: st.session_state.p1_vals = {'v':15, 'p':10, 'g':10, 'v5':9, 'p5':2}
if 'p2_vals' not in st.session_state: st.session_state.p2_vals = {'v':12, 'p':12, 'g':10, 'v5':7, 'p5':4}

# --- CSS LOOK PROFESSIONALE ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 5px; font-size: 1.2rem !important; }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid rgba(128, 128, 128, 0.1) !important;
        padding: 4px 8px !important; border-radius: 6px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 15px !important; font-weight: bold !important; }
    button[kind="primary"] {
        background-color: #28a745 !important; color: white !important;
        font-weight: bold !important; border-radius: 6px !important;
        height: 38px !important; width: 100% !important; margin-top: 25px !important;
    }
    hr { margin: 0.5em 0 !important; border: 1px solid rgba(128,128,128,0.2) !important; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

def w_avg(sf, r5, gs): 
    return ((sf / (gs if gs>0 else 1)) * 0.4) + ((r5 / 5) * 0.6)

def parse_tennis_results(raw_text):
    matches = re.findall(r'(\d+)[:\-](\d+)', raw_text)
    if not matches: return None
    recent = matches[:10]
    last5 = matches[:5]
    return {
        'v': sum(int(m[0]) for m in recent), 'p': sum(int(m[1]) for m in recent), 'g': len(recent),
        'v5': sum(int(m[0]) for m in last5), 'p5': sum(int(m[1]) for m in last5)
    }

# --- SELETTORE SPORT ---
st.sidebar.markdown("### 🔬 SELEZIONA SPORT")
sport = st.sidebar.radio("", ["⚽ CALCIO", "🏒 HOCKEY", "🎾 TENNIS"], horizontal=True)
is_calcio, is_hockey, is_tennis = sport == "⚽ CALCIO", sport == "🏒 HOCKEY", sport == "🎾 TENNIS"

# --- REGISTRAZIONE INCONTRO ---
st.write(f"### 📝 REGISTRAZIONE INCONTRO ({sport})")
c_t1, c_t2, c_btn = st.columns([3, 3, 1.5])
t_h = c_t1.text_input("Giocatore/Squadra 1", value="Sinner J." if is_tennis else "Bologna")
t_o = c_t2.text_input("Giocatore/Squadra 2", value="Alcaraz C." if is_tennis else "Cagliari")
match_name = f"{sport[0]} {t_h} - {t_o}"
if c_btn.button("💾 SALVA INCONTRO", type="primary", key="main_save"):
    if match_name not in st.session_state.db: st.session_state.db[match_name] = []; st.toast("Match creato!")

# --- SIDEBAR DINAMICA ---
st.sidebar.markdown("---")
if is_tennis:
    st.sidebar.markdown("### ⚡ OMEGA FAST PARSER")
    raw1 = st.sidebar.text_area(f"Incolla H2H {t_h}", height=80, key="tennis_raw1")
    if raw1:
        res = parse_tennis_results(raw1)
        if res: st.session_state.p1_vals = res
    raw2 = st.sidebar.text_area(f"Incolla H2H {t_o}", height=80, key="tennis_raw2")
    if raw2:
        res = parse_tennis_results(raw2)
        if res: st.session_state.p2_vals = res

    st.sidebar.header(f"🔵 DATI {t_h[:10].upper()}")
    c_f_s = st.sidebar.number_input("Set VINTI Stag.", 0, 100, st.session_state.p1_vals['v'])
    c_s_s = st.sidebar.number_input("Set PERSI Stag.", 0, 100, st.session_state.p1_vals['p'])
    c_g_s = st.sidebar.number_input("Partite Giocate ", 1, 100, st.session_state.p1_vals['g'])
    c_f_5 = st.sidebar.number_input("Set VINTI U5", 0, 50, st.session_state.p1_vals['v5'])
    c_s_5 = st.sidebar.number_input("Set PERSI U5", 0, 50, st.session_state.p1_vals['p5'])
    st.sidebar.header(f"🔴 DATI {t_o[:10].upper()}")
    o_f_s = st.sidebar.number_input("Set VINTI Stag. ", 0, 100, st.session_state.p2_vals['v'])
    o_s_s = st.sidebar.number_input("Set PERSI Stag. ", 0, 100, st.session_state.p2_vals['p'])
    o_g_s = st.sidebar.number_input("Partite Giocate G2", 1, 100, st.session_state.p2_vals['g'])
    o_f_5 = st.sidebar.number_input("Set VINTI U5 ", 0, 50, st.session_state.p2_vals['v5'])
    o_s_5 = st.sidebar.number_input("Set PERSI U5 ", 0, 50, st.session_state.p2_vals['p5'])
    ex_c, ex_o, max_g = (w_avg(c_f_s,c_f_5,c_g_s)+w_avg(o_s_s,o_s_5,o_g_s))/2, (w_avg(o_f_s,o_f_5,o_g_s)+w_avg(c_s_s,c_s_5,c_g_s))/2, 3
elif is_calcio:
    c_f_s = st.sidebar.number_input("GF Casa", 0, 100, 15); c_s_s = st.sidebar.number_input("GS Casa", 0, 100, 10); c_g_s = st.sidebar.number_input("G Casa", 1, 100, 8)
    c_f_5 = st.sidebar.number_input("GF U5 Casa", 0, 50, 8); c_s_5 = st.sidebar.number_input("GS U5 Casa", 0, 50, 4)
    o_f_s = st.sidebar.number_input("GF Osp", 0, 100, 10); o_s_s = st.sidebar.number_input("GS Osp", 0, 100, 18); o_g_s = st.sidebar.number_input("G Osp", 1, 100, 8)
    o_f_5 = st.sidebar.number_input("GF U5 Osp", 0, 50, 3); o_s_5 = st.sidebar.number_input("GS U5 Osp", 0, 50, 9)
    ex_c, ex_o, max_g = (w_avg(c_f_s,c_f_5,c_g_s)+w_avg(o_s_s,o_s_5,o_g_s))/2, (w_avg(o_f_s,o_f_5,o_g_s)+w_avg(c_s_s,c_s_5,c_g_s))/2, 6
else:
    h_pg = st.sidebar.number_input("PG 1", 1, 100, 4); h_gf = st.sidebar.number_input("GF 1", 0, 500, 18); h_gs = st.sidebar.number_input("GS 1", 0, 500, 7)
    a_pg = st.sidebar.number_input("PG 2", 1, 100, 4); a_gf = st.sidebar.number_input("GF 2", 0, 500, 11); a_gs = st.sidebar.number_input("GS 2", 0, 500, 11)
    ex_c, ex_o, max_g = ((h_gf/h_pg)+(a_gs/a_pg))/2, ((a_gf/a_pg)+(h_gs/h_pg))/2, 9

q1_b = st.sidebar.number_input("Quota 1", 1.0, 50.0, 2.0); qx_b = st.sidebar.number_input("Quota X", 1.0, 50.0, 3.2 if is_calcio else 1.0); q2_b = st.sidebar.number_input("Quota 2", 1.0, 50.0, 3.5)

# --- ENGINE ---
tab1, tab2, tab3 = st.tabs(["🎯 ENGINE MATRIX", "📊 VALUE RATING", "📂 DATABASE HUB"])

with tab1:
    if not is_tennis:
        st.info(f"📊 xG: {ex_c:.2f} | {ex_o:.2f}")
        matrix = np.zeros((max_g, max_g))
        pc, po = [poisson(ex_c, i) for i in range(max_g)], [poisson(ex_o, i) for i in range(max_g)]
        for h in range(max_g):
            for a in range(max_g): matrix[h,a] = pc[h]*po[a]
        scen = [f"{int(round(ex_c))}-{int(round(ex_o))}", f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}", f"{int(math.floor(ex_c))}-{int(math.ceil(ex_o))}"]
        c1, c2 = st.columns([2, 1.2])
        with c1: st.dataframe(pd.DataFrame(matrix*100).style.format("{:.1f}%").background_gradient(cmap='Greens'), use_container_width=True)
        with c2: 
            ris = []
            for h in range(max_g):
                for a in range(max_g): p = matrix[h,a]; ris.append({"Ris":f"{h}-{a}","Prob":p*100,"QF":1/p if p>0 else 0})
            df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
            st.dataframe(df_r.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Ris'] in scen else ['']*3, axis=1).format({"Prob":"{:.1f}%","QF":"{:.2f}"}), hide_index=True)
        
        if is_calcio:
            st.subheader("🔢 Multigol")
            cmg = st.columns(4); def gmm(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
            for i, mg in enumerate([(1,2),(1,3),(1,4),(2,3),(2,4),(2,5),(3,4),(3,5)]):
                v_m = gmm(mg[0], mg[1]); cmg[i%4].metric(f"MG {mg[0]}-{mg[1]}", f"{v_m:.1f}%")
        elif is_hockey:
            st.subheader("🎯 Margine Vittoria")
            t1_1g, t1_2g, t1_3p = sum(matrix[i,i-1] for i in range(1,max_g))*100, sum(matrix[i,i-2] for i in range(2,max_g))*100, sum(matrix[i,j] for i in range(3,max_g) for j in range(max_g) if i-j>=3)*100
            st.columns(3)[0].metric("T1 +1G",f"{t1_1g:.1f}%"); st.columns(3)[1].metric("T1 +2G",f"{t1_2g:.1f}%"); st.columns(3)[2].metric("T1 +3G",f"{t1_3p:.1f}%")

    else:
        st.info(f"📊 xS: {ex_c:.2f} | {ex_o:.2f}")
        r20, r21, r02, r12 = poisson(ex_c,2)*poisson(ex_o,0), poisson(ex_c,2)*poisson(ex_o,1), poisson(ex_c,0)*poisson(ex_o,2), poisson(ex_c,1)*poisson(ex_o,2)
        tr = r20+r21+r02+r12 if r20+r21+r02+r12>0 else 0.001
        s20, s21, s02, s12 = (r20/tr)*100, (r21/tr)*100, (r02/tr)*100, (r12/tr)*100
        p1v, p2v = s20+s21, s02+s12
        col1, col2 = st.columns([2, 1.2])
        with col1:
            st.subheader("🎯 Set Betting")
            st.dataframe(pd.DataFrame({"Ris":["2-0","2-1","0-2","1-2"],"Prob":[s20,s21,s02,s12],"QF":[100/s20,100/s21,100/s02,100/s12]}).style.format({"Prob":"{:.1f}%","QF":"{:.2f}"}), hide_index=True)
        with col2:
            st.subheader("🎾 T/T")
            st.metric(f"VITTORIA {t_h[:8]}", f"{p1v:.1f}%", f"QF:{100/p1v:.2f}"); st.metric(f"VITTORIA {t_o[:8]}", f"{p2v:.1f}%", f"QF:{100/p2v:.2f}")
        st.subheader("📈 ANALISI GAME & TIE-BREAK")
        avg_g = (s20*18.5 + s02*18.5 + s21*26.5 + s12*26.5)/100
        p_tb = ((s21+s12)*0.45) + ((s20+s02)*0.15)
        p_o22 = (s21+s12)*0.95 + (s20+s02)*0.15
        cg = st.columns(3); cg[0].metric("GAME MEDI", f"{avg_g:.1f}"); cg[1].metric("PROB. TIE-BREAK", f"{p_tb:.1f}%", f"QF:{100/p_tb:.2f}"); cg[2].metric("OVER 22.5", f"{p_o22:.1f}%", f"QF:{100/p_o22:.2f}")
        p_s1o9 = (p_tb/2)+42; p_u20 = (s20+s02)*0.75; p_set1 = p1v+s12
        st.columns(3)[0].metric("SET 1 OVER 9.5", f"{p_s1o9:.1f}%"); st.columns(3)[1].metric("UNDER 20.5", f"{p_u20:.1f}%"); st.columns(3)[2].metric("G1 VINCE SET", f"{p_set1:.1f}%")

with tab2:
    st.subheader("📊 Value Bet")
    b1, b2 = (p1v, p2v) if is_tennis else (np.sum(np.tril(matrix, -1))*100, np.sum(np.triu(matrix, 1))*100)
    qf1, qf2 = 100/b1 if b1>0 else 0, 100/b2 if b2>0 else 0
    st.columns(2)[0].metric("SEGNO 1", f"QF:{qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO")
    st.columns(2)[1].metric("SEGNO 2", f"QF:{qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")

with tab3:
    if st.session_state.db:
        for m, prs in list(st.session_state.db.items()):
            st.markdown(f"**{m}**")
            for idx, p in enumerate(prs):
                c1, c2, c3 = st.columns([4, 2, 1]); c1.write(p['scelta'])
                if c2.button(p['esito'], key=f"tog_{m}_{idx}"): st.session_state.db[m][idx]['esito'] = {'⏳':'WIN','WIN':'LOSS','LOSS':'⏳'}[p['esito']]; st.rerun()
                if c3.button("🗑️", key=f"del_{m}_{idx}"): st.session_state.db[m].pop(idx); st.rerun()
            if st.button("Elimina Incontro", key=f"rem_{m}"): del st.session_state.db[m]; st.rerun()
