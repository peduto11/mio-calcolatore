import streamlit as st
import math
import pandas as pd
import numpy as np
import re

# Configurazione Pagina
st.set_page_config(page_title="SPORTS LAB PRO", page_icon="🔬", layout="wide")

# --- MEMORIA DATABASE ---
if 'db' not in st.session_state:
    st.session_state.db = {}

# --- CSS LOOK PROFESSIONALE E FIX BOTTONI ---
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
    v_t = sum(int(m[0]) for m in recent); p_t = sum(int(m[1]) for m in recent)
    v_5 = sum(int(m[0]) for m in last5); p_5 = sum(int(m[1]) for m in last5)
    return {'v_t': v_t, 'p_t': p_t, 'c_t': len(recent), 'v_5': v_5, 'p_5': p_5, 'c_5': len(last5)}

# --- SELETTORE SPORT ---
st.sidebar.markdown("### 🔬 SELEZIONA SPORT")
sport = st.sidebar.radio("", ["⚽ CALCIO", "🏒 HOCKEY", "🎾 TENNIS"], horizontal=True)
is_calcio, is_hockey, is_tennis = sport == "⚽ CALCIO", sport == "🏒 HOCKEY", sport == "🎾 TENNIS"

# --- REGISTRAZIONE INCONTRO ---
st.write(f"### 📝 REGISTRAZIONE INCONTRO ({sport})")
c_t1, c_t2, c_btn = st.columns([3, 3, 1.5])
t_h = c_t1.text_input("Sogg. 1", value="Sinner J." if is_tennis else "Bologna")
t_o = c_t2.text_input("Sogg. 2", value="Alcaraz C." if is_tennis else "Cagliari")
match_name = f"{sport[0]} {t_h} - {t_o}"
if c_btn.button("💾 SALVA INCONTRO", key="master_save", type="primary"):
    if match_name not in st.session_state.db: st.session_state.db[match_name] = []; st.toast("Match creato!")

# --- SIDEBAR ---
st.sidebar.markdown("---")
if is_calcio:
    st.sidebar.header("🏠 DATI CASA")
    c_f_s, c_s_s, c_g_s = st.sidebar.number_input("Gol Fatti S", 0, 100, 15), st.sidebar.number_input("Gol Subiti S", 0, 100, 10), st.sidebar.number_input("Partite S", 1, 50, 8)
    c_f_5, c_s_5 = st.sidebar.number_input("Fatti U5", 0, 50, 8), st.sidebar.number_input("Subiti U5", 0, 50, 4)
    st.sidebar.header("🚀 DATI OSPITE")
    o_f_s, o_s_s, o_g_s = st.sidebar.number_input("Gol Fatti S ", 0, 100, 10), st.sidebar.number_input("Gol Subiti S ", 0, 100, 18), st.sidebar.number_input("Partite S ", 1, 50, 8)
    o_f_5, o_s_5 = st.sidebar.number_input("Fatti U5 ", 0, 50, 3), st.sidebar.number_input("Subiti U5 ", 0, 50, 9)
    ex_c, ex_o, max_g = (w_avg(c_f_s,c_f_5,c_g_s)+w_avg(o_s_s,o_s_5,o_g_s))/2, (w_avg(o_f_s,o_f_5,o_g_s)+w_avg(c_s_s,c_s_5,c_g_s))/2, 6
elif is_hockey:
    st.sidebar.header("📊 DATI HOCKEY")
    h_pg, h_gf, h_gs = st.sidebar.number_input("PG 1", 1, 80, 4), st.sidebar.number_input("GF 1", 0, 300, 18), st.sidebar.number_input("GS 1", 0, 300, 7)
    a_pg, a_gf, a_gs = st.sidebar.number_input("PG 2", 1, 80, 4), st.sidebar.number_input("GF 2", 0, 300, 11), st.sidebar.number_input("GS 2", 0, 300, 11)
    ex_c, ex_o, max_g = ((h_gf/h_pg)+(a_gs/a_pg))/2, ((a_gf/a_pg)+(h_gs/h_pg))/2, 9
elif is_tennis:
    st.sidebar.markdown("### ⚡ OMEGA FAST PARSER")
    raw1, raw2 = st.sidebar.text_area(f"Incolla H2H {t_h}", height=70), st.sidebar.text_area(f"Incolla H2H {t_o}", height=70)
    p1d, p2d = {'v_t':15,'p_t':10,'v_5':9,'p_5':2,'c_t':10}, {'v_t':12,'p_t':12,'v_5':7,'p_5':4,'c_t':10}
    if raw1: r = parse_tennis_results(raw1); p1d = r if r else p1d
    if raw2: r = parse_tennis_results(raw2); p2d = r if r else p2d
    st.sidebar.header("🔵 G1"); c_f_s, c_s_s, c_g_s = st.sidebar.number_input("Set V S", 0, 100, p1d['v_t']), st.sidebar.number_input("Set P S", 0, 100, p1d['p_t']), st.sidebar.number_input("Partite S", 1, 50, p1d['c_t'])
    c_f_5, c_s_5 = st.sidebar.number_input("Set V U5", 0, 50, p1d['v_5']), st.sidebar.number_input("Set P U5", 0, 50, p1d['p_5'])
    st.sidebar.header("🔴 G2"); o_f_s, o_s_s, o_g_s = st.sidebar.number_input("Set V S ", 0, 100, p2d['v_t']), st.sidebar.number_input("Set P S ", 0, 100, p2d['p_t']), st.sidebar.number_input("Partite S ", 1, 50, p2d['c_t'])
    o_f_5, o_s_5 = st.sidebar.number_input("Set V U5 ", 0, 50, p2d['v_5']), st.sidebar.number_input("Set P U5 ", 0, 50, p2d['p_5'])
    ex_c, ex_o, max_g = (w_avg(c_f_s,c_f_5,c_g_s)+w_avg(o_s_s,o_s_5,o_g_s))/2, (w_avg(o_f_s,o_f_5,o_g_s)+w_avg(c_s_s,c_s_5,c_g_s))/2, 3

q1_b, qx_b, q2_b = st.sidebar.number_input("Quota 1", 1.0, 50.0, 2.0), st.sidebar.number_input("Quota X", 1.0, 50.0, 3.2 if is_calcio else 1.0), st.sidebar.number_input("Quota 2", 1.0, 50.0, 3.5)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🎯 ENGINE MATRIX", "📊 VALUE RATING", "📂 DATABASE HUB"])

with tab1:
    if not is_tennis:
        st.info(f"📊 xG: {t_h} {ex_c:.2f} | {t_o} {ex_o:.2f}")
        matrix = np.zeros((max_g, max_g))
        pc, po = [poisson(ex_c, i) for i in range(max_g)], [poisson(ex_o, i) for i in range(max_g)]
        for h in range(max_g):
            for a in range(max_g): matrix[h,a] = pc[h]*po[a]
        c1, c2 = st.columns([2, 1.2])
        with c1: st.dataframe(pd.DataFrame(matrix*100).style.format("{:.1f}%").background_gradient(cmap='Greens'), use_container_width=True)
        with c2: 
            ris = []
            for h in range(max_g):
                for a in range(max_g): p = matrix[h,a]; ris.append({"Ris":f"{h}-{a}","Prob":p*100,"QF":1/p if p>0 else 0})
            st.dataframe(pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10).style.format({"Prob":"{:.1f}%","QF":"{:.2f}"}), hide_index=True)
        st.subheader("💡 Scenari Esatti")
        cs = st.columns(4)
        for i, rn in enumerate(list(dict.fromkeys([f"{int(round(ex_c))}-{int(round(ex_o))}", f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}"]))[:4]):
            try:
                p_v = matrix[int(rn.split('-')[0]), int(rn.split('-')[1])]*100
                with cs[i]: st.metric("ESATTO", rn, f"{p_v:.1f}% (QF:{100/p_v:.2f})")
            except: pass
        if is_calcio:
            st.subheader("📈 Mercati Principali")
            p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
            ov = sum(matrix[r,c] for r in range(max_g) for c in range(max_g) if r+c > 2.5)*100
            mc = st.columns(6); mc[0].metric("1",f"{p1:.1f}%",f"QF:{100/p1:.2f}"); mc[1].metric("X",f"{px:.1f}%",f"QF:{100/px:.2f}"); mc[2].metric("2",f"{p2:.1f}%",f"QF:{100/p2:.2f}"); mc[3].metric("O2.5",f"{ov:.1f}%",f"QF:{100/ov:.2f}"); mc[4].metric("GOAL",f"50.0%",f"QF:2.00"); mc[5].metric("NO G",f"50.0%",f"QF:2.00")
    else:
        st.info(f"📊 xS: {t_h} {ex_c:.2f} | {t_o} {ex_o:.2f}")
        r20, r21, r02, r12 = poisson(ex_c,2)*poisson(ex_o,0), poisson(ex_c,2)*poisson(ex_o,1), poisson(ex_c,0)*poisson(ex_o,2), poisson(ex_c,1)*poisson(ex_o,2)
        tr = r20+r21+r02+r12 if r20+r21+r02+r12>0 else 0.001
        s20, s21, s02, s12 = (r20/tr)*100, (r21/tr)*100, (r02/tr)*100, (r12/tr)*100
        p1v, p2v = s20+s21, s02+s12
        col1, col2 = st.columns([2, 1.2])
        with col1: st.dataframe(pd.DataFrame({"Ris":["2-0","2-1","0-2","1-2"],"V":["G1","G1","G2","G2"],"Prob":[s20,s21,s02,s12],"QF":[100/s20,100/s21,100/s02,100/s12]}).style.format({"Prob":"{:.1f}%","QF":"{:.2f}"}), hide_index=True)
        with col2: st.metric(f"VITTORIA {t_h[:8]}", f"{p1v:.1f}%", f"QF:{100/p1v:.2f}"); st.metric(f"VITTORIA {t_o[:8]}", f"{p2v:.1f}%", f"QF:{100/p2v:.2f}")
        st.subheader("📈 ANALISI GAME & TIE-BREAK (STIMA MATEMATICA)")
        avg_g = (s20*18.5 + s02*18.5 + s21*26.5 + s12*26.5)/100
        p_tb = ((s21+s12)*0.45) + ((s20+s02)*0.15); p_o22 = (s21+s12+(s20*0.2))
        cg = st.columns(4); cg[0].metric("GAME MEDI", f"{avg_g:.1f}"); cg[1].metric("PROB. TIE-BREAK", f"{p_tb:.1f}%", f"QF:{100/p_tb:.2f}"); cg[2].metric("OVER 22.5 GAME", f"{p_o22:.1f}%", f"QF:{100/p_o22:.2f}"); cg[3].metric("UNDER 20.5", f"{(100-p_o22-10):.1f}%", f"QF:{100/(100-p_o22-10):.2f}")

with tab2:
    st.subheader("📊 Ricerca Value Bet")
    b1, b2 = (p1v, p2v) if is_tennis else (p1, p2)
    qf1, qf2 = 100/b1 if b1>0 else 0, 100/b2 if b2>0 else 0
    v1, v2 = st.columns(2); v1.metric("SEGNO 1", f"QF:{qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO"); v2.metric("SEGNO 2", f"QF:{qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")

with tab3:
    if st.session_state.db:
        for m, prs in list(st.session_state.db.items()):
            st.markdown("---")
            cols = st.columns([2] + [3]*len(prs)) if prs else st.columns([2, 8])
            with cols[0]:
                if st.button("🗑️", key=f"dm_{m}"): del st.session_state.db[m]; st.rerun()
                st.write(f"**{m}**")
            for idx, p in enumerate(prs):
                with cols[idx+1]:
                    if st.button(f"{p['scelta']} {p['esito']}", key=f"tp_{m}_{idx}"):
                        st.session_state.db[m][idx]['esito'] = {'⏳':'WIN','WIN':'LOSS','LOSS':'⏳'}[p['esito']]; st.rerun()
    else: st.info("DB Vuoto")
