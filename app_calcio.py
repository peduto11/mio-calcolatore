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
    .table-text { margin-top: 8px; font-size: 14px; font-weight: 500; }
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
    v_tot = sum(int(m[0]) for m in recent); p_tot = sum(int(m[1]) for m in recent)
    v_5 = sum(int(m[0]) for m in last5); p_5 = sum(int(m[1]) for m in last5)
    return {'v_tot': v_tot, 'p_tot': p_tot, 'count_tot': len(recent), 'v_5': v_5, 'p_5': p_5, 'count_5': len(last5)}

# --- SELETTORE SPORT (SIDEBAR) ---
st.sidebar.markdown("### 🔬 SELEZIONA SPORT")
sport = st.sidebar.radio("", ["⚽ CALCIO", "🏒 HOCKEY", "🎾 TENNIS"], horizontal=True)

is_calcio = sport == "⚽ CALCIO"
is_hockey = sport == "🏒 HOCKEY"
is_tennis = sport == "🎾 TENNIS"

# --- REGISTRAZIONE INCONTRO ---
st.write(f"### 📝 REGISTRAZIONE INCONTRO ({sport})")
c_t1, c_t2, c_btn = st.columns([3, 3, 1.5])
if is_calcio:
    t_h = c_t1.text_input("Squadra Casa", value="Bologna")
    t_o = c_t2.text_input("Squadra Ospite", value="Cagliari")
    icona = "⚽"
elif is_hockey:
    t_h = c_t1.text_input("Squadra 1 (Casa/Pref)", value="Kazakistan")
    t_o = c_t2.text_input("Squadra 2 (Ospite/Sfav)", value="Ucraina")
    icona = "🏒"
else:
    t_h = c_t1.text_input("Giocatore 1", value="Sinner J.")
    t_o = c_t2.text_input("Giocatore 2", value="Alcaraz C.")
    icona = "🎾"

match_name = f"{icona} {t_h} - {t_o}"

if c_btn.button("💾 SALVA INCONTRO", key="save_match_btn", type="primary"):
    if match_name not in st.session_state.db:
        st.session_state.db[match_name] = []
        st.toast(f"Match di {sport} creato!")

def add_to_db(pron):
    if match_name in st.session_state.db:
        st.session_state.db[match_name].append({'scelta': pron, 'esito': '⏳'})
        st.toast(f"Inviato: {pron}")
    else: 
        st.error("Clicca prima su SALVA INCONTRO!")

# --- SIDEBAR DINAMICA ---
st.sidebar.markdown("---")
if is_calcio:
    st.sidebar.header("🏠 DATI CASA")
    c_f_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", 0, 100, 15)
    c_s_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", 0, 100, 10)
    c_g_s = st.sidebar.number_input("Partite Casa (Stagione)", 1, 100, 8)
    c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", 0, 50, 8)
    c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", 0, 50, 4)
    st.sidebar.header("🚀 DATI OSPITE")
    o_f_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", 0, 100, 10)
    o_s_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", 0, 100, 18)
    o_g_s = st.sidebar.number_input("Partite Ospite (Stagione)", 1, 100, 8)
    o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", 0, 50, 3)
    o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", 0, 50, 9)
    ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_g = 6
elif is_hockey:
    tipo_dati_hockey = st.sidebar.radio("", ["📊 Semplice", "🔥 Avanzata"])
    if tipo_dati_hockey == "📊 Semplice":
        h_pg = st.sidebar.number_input("PG 1", 1, 100, 4); h_gf = st.sidebar.number_input("GF 1", 0, 500, 18); h_gs = st.sidebar.number_input("GS 1", 0, 500, 7)
        a_pg = st.sidebar.number_input("PG 2", 1, 100, 4); a_gf = st.sidebar.number_input("GF 2", 0, 500, 11); a_gs = st.sidebar.number_input("GS 2", 0, 500, 11)
        ex_c = ((h_gf/h_pg)+(a_gs/a_pg))/2; ex_o = ((a_gf/a_pg)+(h_gs/h_pg))/2
    else:
        c_f_s, c_s_s, c_g_s = st.sidebar.number_input("GF Casa",0,100,15), st.sidebar.number_input("GS Casa",0,100,10), st.sidebar.number_input("G Casa",1,100,5)
        c_f_5, c_s_5 = st.sidebar.number_input("GF U5 Casa",0,50,12), st.sidebar.number_input("GS U5 Casa",0,50,8)
        o_f_s, o_s_s, o_g_s = st.sidebar.number_input("GF Osp",0,100,10), st.sidebar.number_input("GS Osp",0,100,18), st.sidebar.number_input("G Osp",1,100,5)
        o_f_5, o_s_5 = st.sidebar.number_input("GF U5 Osp",0,50,9), st.sidebar.number_input("GS U5 Osp",0,50,14)
        ex_c, ex_o = (w_avg(c_f_s,c_f_5,c_g_s)+w_avg(o_s_s,o_s_5,o_g_s))/2, (w_avg(o_f_s,o_f_5,o_g_s)+w_avg(c_s_s,c_s_5,c_g_s))/2
    max_g = 9 
elif is_tennis:
    st.sidebar.markdown("### ⚡ OMEGA FAST PARSER")
    raw1, raw2 = st.sidebar.text_area(f"H2H {t_h}"), st.sidebar.text_area(f"H2H {t_o}")
    p1d, p2d = {'v_tot':15,'p_tot':10,'v_5':9,'p_5':2,'count_tot':10}, {'v_tot':12,'p_tot':12,'v_5':7,'p_5':4,'count_tot':10}
    if raw1: res = parse_tennis_results(raw1); p1d = res if res else p1d
    if raw2: res = parse_tennis_results(raw2); p2d = res if res else p2d
    c_f_s, c_s_s, c_g_s = st.sidebar.number_input("Set V S",0,100,p1d['v_tot']), st.sidebar.number_input("Set P S",0,100,p1d['p_tot']), st.sidebar.number_input("G S",1,100,p1d['count_tot'])
    c_f_5, c_s_5 = st.sidebar.number_input("Set V U5",0,50,p1d['v_5']), st.sidebar.number_input("Set P U5",0,50,p1d['p_5'])
    o_f_s, o_s_s, o_g_s = st.sidebar.number_input("Set V S ",0,100,p2d['v_tot']), st.sidebar.number_input("Set P S ",0,100,p2d['p_tot']), st.sidebar.number_input("G S ",1,100,p2d['count_tot'])
    o_f_5, o_s_5 = st.sidebar.number_input("Set V U5 ",0,50,p2d['v_5']), st.sidebar.number_input("Set P U5 ",0,50,p2d['p_5'])
    ex_c, ex_o, max_g = (w_avg(c_f_s,c_f_5,c_g_s)+w_avg(o_s_s,o_s_5,o_g_s))/2, (w_avg(o_f_s,o_f_5,o_g_s)+w_avg(c_s_s,c_s_5,c_g_s))/2, 3

q1_b = st.sidebar.number_input("Quota 1", 1.0, 50.0, 2.0)
qx_b = st.sidebar.number_input("Quota X", 1.0, 50.0, 3.2 if is_calcio else 1.0)
q2_b = st.sidebar.number_input("Quota 2", 1.0, 50.0, 3.5)

# --- MATRICE E TABS ---
st.title(f"🔬 SPORTS LAB PRO - MODULE: {sport}")
tab1, tab2, tab3 = st.tabs(["🎯 ENGINE MATRIX", "📊 VALUE RATING", "📂 DATABASE HUB"])

with tab1:
    if not is_tennis:
        st.info(f"📊 Valori Attesi (xG): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
        matrix = np.zeros((max_g, max_g))
        pc, po = [poisson(ex_c, i) for i in range(max_g)], [poisson(ex_o, i) for i in range(max_g)]
        for h in range(max_g):
            for a in range(max_g): matrix[h, a] = pc[h] * po[a]
        scen = [f"{int(round(ex_c))}-{int(round(ex_o))}", f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}", f"{int(math.floor(ex_c))}-{int(math.ceil(ex_o))}"]
        
        c1, c2 = st.columns([2, 1.2])
        with c1:
            st.subheader("📊 Matrice Probabilità")
            st.dataframe(pd.DataFrame(matrix*100).style.format("{:.1f}%").background_gradient(cmap='Greens'), use_container_width=True)
        with c2:
            st.subheader("🎯 Classifica Risultati")
            ris = []
            for h in range(max_g):
                for a in range(max_g): p = matrix[h, a]; ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
            st.dataframe(pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10).style.format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, use_container_width=True)

        st.subheader("💡 Scenari Esatti")
        cs = st.columns(4)
        for i, rn in enumerate(list(dict.fromkeys(scen))[:4]):
            try:
                pv = matrix[int(rn.split('-')[0]), int(rn.split('-')[1])] * 100
                with cs[i]:
                    st.metric("ESATTO", rn, f"{pv:.1f}% (QF:{100/pv:.2f})")
                    if st.button(f"📌 {rn}", key=f"s_{i}"): add_to_db(f"Esatto {rn}")
            except: pass

        if is_calcio:
            st.subheader("🚀 Scenari Combo")
            def gp(cmin, cmax, omin, omax): return sum(matrix[h, a] for h in range(cmin, cmax+1) for a in range(omin, omax+1) if h<max_g and a<max_g) * 100
            cb = st.columns(3)
            with cb[0]: 
                p_bi = gp(1,3,1,3); st.metric("BILANCIATO", "T1 1-3 + T2 1-3", f"{p_bi:.1f}%"); 
                if st.button("📌 Bil"): add_to_db("Bil: 1-3+1-3")
            with cb[1]: 
                p_dom = gp(2,4,0,1); st.metric("DOMINIO", "T1 2-4 + T2 0-1", f"{p_dom:.1f}%");
                if st.button("📌 Dom"): add_to_db("Dom: 2-4+0-1")
            with cb[2]: 
                p_goal = gp(1,3,1,3); st.metric("GOAL", "GOAL Combo", f"{p_goal:.1f}%");
                if st.button("📌 Goal"): add_to_db("Goal Combo")

            st.subheader("📈 Mercati Principali")
            p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
            ov25 = sum(matrix[r,c] for r in range(max_g) for c in range(max_g) if r+c > 2.5)*100
            mc = st.columns(6)
            mc[0].metric("1", f"{p1:.1f}%", f"QF:{100/p1:.2f}"); mc[1].metric("X", f"{px:.1f}%", f"QF:{100/px:.2f}"); mc[2].metric("2", f"{p2:.1f}%", f"QF:{100/p2:.2f}");
            mc[3].metric("O2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}"); mc[4].metric("G", "50%", "2.00"); mc[5].metric("NG", "50%", "2.00")
            
            st.subheader("🔢 Multigol")
            def gmm(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
            cmg = st.columns(4)
            for i, mg in enumerate([(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]):
                v = gmm(mg[0], mg[1]); cmg[i%4].metric(f"MG {mg[0]}-{mg[1]}", f"{v:.1f}%", f"QF:{100/v:.2f}")

    elif is_tennis:
        st.info(f"📊 Set Attesi (xS): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
        r20, r21, r02, r12 = poisson(ex_c,2)*poisson(ex_o,0), poisson(ex_c,2)*poisson(ex_o,1), poisson(ex_c,0)*poisson(ex_o,2), poisson(ex_c,1)*poisson(ex_o,2)
        tr = r20+r21+r02+r12 if r20+r21+r02+r12>0 else 0.001
        s20, s21, s02, s12 = (r20/tr)*100, (r21/tr)*100, (r02/tr)*100, (r12/tr)*100
        p1v, p2v = s20+s21, s02+s12
        col1, col2 = st.columns([2, 1.2])
        with col1: st.dataframe(pd.DataFrame({"Ris":["2-0","2-1","0-2","1-2"],"Vinc":[t_h,t_h,t_o,t_o],"Prob":[s20,s21,s02,s12]}).style.format({"Prob":"{:.1f}%"}), hide_index=True)
        with col2: st.metric(f"VITTORIA {t_h[:8]}", f"{p1v:.1f}%", f"QF:{100/p1v:.2f}"); st.metric(f"VITTORIA {t_o[:8]}", f"{p2v:.1f}%", f"QF:{100/p2v:.2f}")
        
        st.subheader("📈 ANALISI GAME & TIE-BREAK (STIMA)")
        avg_g = (s20*18.5 + s02*18.5 + s21*26.5 + s12*26.5)/100
        p_tb = ((s21+s12)*0.45) + ((s20+s02)*0.15)
        cg = st.columns(3)
        cg[0].metric("GAME MEDI", f"{avg_g:.1f}"); cg[1].metric("PROB. TIE-BREAK", f"{p_tb:.1f}%", f"QF:{100/p_tb:.2f}"); cg[2].metric("OVER 22.5", f"{(s21+s12+s20*0.2):.1f}%")

with tab2:
    st.subheader("📊 Ricerca Value Bet")
    b1, b2 = (p1v, p2v) if is_tennis else (p1, p2)
    qf1, qf2 = 100/b1 if b1>0 else 0, 100/b2 if b2>0 else 0
    v1, v2 = st.columns(2); v1.metric("SEGNO 1", f"QF:{qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO"); v2.metric("SEGNO 2", f"QF:{qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")

with tab3:
    st.subheader("📂 Database")
    if st.session_state.db:
        for m, prs in list(st.session_state.db.items()):
            st.markdown(f"**{m}**")
            if prs:
                for idx, p in enumerate(prs):
                    c1, c2, c3 = st.columns([4, 2, 1])
                    c1.write(p['scelta']); c2.write(p['esito'])
                    if c3.button("🗑️", key=f"dp_{m}_{idx}"): st.session_state.db[m].pop(idx); st.rerun()
            if st.button("Rimuovi Match", key=f"rm_{m}"): del st.session_state.db[m]; st.rerun()
    else: st.info("DB Vuoto")
