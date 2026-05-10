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

if c_btn.button("💾 SALVA INCONTRO", type="primary"):
    if match_name not in st.session_state.db:
        st.session_state.db[match_name] = []
        st.toast(f"Match di {sport} creato!")

def add_to_db(pron):
    if match_name in st.session_state.db:
        st.session_state.db[match_name].append({'scelta': pron, 'esito': '⏳'})
        st.toast(f"Inviato: {pron}")
    else: 
        st.error("Clicca prima su SALVA INCONTRO per creare la riga!")

# --- SIDEBAR DINAMICA ---
st.sidebar.markdown("---")

if is_calcio:
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
    
    ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_g = 6

elif is_hockey:
    st.sidebar.markdown("### ⚙️ FORMATO CLASSIFICA HOCKEY")
    tipo_dati_hockey = st.sidebar.radio("", ["📊 Semplice (Mondiali/Coppe)", "🔥 Avanzata (Campionati)"])
    if tipo_dati_hockey == "📊 Semplice (Mondiali/Coppe)":
        st.sidebar.header(f"🔵 DATI {t_h[:10].upper()}")
        h_pg = st.sidebar.number_input("Partite Giocate (PG)", min_value=1, value=4)
        h_gf = st.sidebar.number_input("Reti Fatte (R - Prima)", min_value=0, value=18)
        h_gs = st.sidebar.number_input("Reti Subite (R - Dopo)", min_value=0, value=7)
        st.sidebar.markdown("---")
        st.sidebar.header(f"🔴 DATI {t_o[:10].upper()}")
        a_pg = st.sidebar.number_input("Partite Giocate (PG) ", min_value=1, value=4)
        a_gf = st.sidebar.number_input("Reti Fatte (R - Prima) ", min_value=0, value=11)
        a_gs = st.sidebar.number_input("Reti Subite (R - Dopo) ", min_value=0, value=11)
        ex_c = ((h_gf / h_pg) + (a_gs / a_pg)) / 2
        ex_o = ((a_gf / a_pg) + (h_gs / h_pg)) / 2
    else:
        st.sidebar.header(f"🔵 {t_h[:10].upper()} (In Casa)")
        c_f_s = st.sidebar.number_input("Gol Fatti Casa", min_value=0, value=15)
        c_s_s = st.sidebar.number_input("Gol Subiti Casa", min_value=0, value=10)
        c_g_s = st.sidebar.number_input("Partite Casa", min_value=1, value=5)
        st.sidebar.subheader("🔥 Forma (U5)")
        c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", min_value=0, value=12)
        c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", min_value=0, value=8)
        st.sidebar.markdown("---")
        st.sidebar.header(f"🔴 {t_o[:10].upper()} (In Trasferta)")
        o_f_s = st.sidebar.number_input("Gol Fatti Ospite", min_value=0, value=10)
        o_s_s = st.sidebar.number_input("Gol Subiti Ospite", min_value=0, value=18)
        o_g_s = st.sidebar.number_input("Partite Ospite", min_value=1, value=5)
        st.sidebar.subheader("🔥 Forma (U5)")
        o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", min_value=0, value=9)
        o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", min_value=0, value=14)
        ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
        ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_g = 9 

elif is_tennis:
    st.sidebar.markdown("### ⚡ OMEGA FAST PARSER")
    raw_p1 = st.sidebar.text_area(f"Incolla qui H2H {t_h}", height=80)
    raw_p2 = st.sidebar.text_area(f"Incolla qui H2H {t_o}", height=80)
    p1_def = {'v_tot':15, 'p_tot':10, 'v_5':9, 'p_5':2, 'count_tot':10}
    p2_def = {'v_tot':12, 'p_tot':12, 'v_5':7, 'p_5':4, 'count_tot':10}
    if raw_p1: 
        res = parse_tennis_results(raw_p1)
        if res: p1_def = res
    if raw_p2:
        res = parse_tennis_results(raw_p2)
        if res: p2_def = res
    st.sidebar.header(f"🔵 DATI {t_h[:10].upper()}")
    c_f_s = st.sidebar.number_input("Set VINTI (Stagione)", 0, 100, p1_def['v_tot'])
    c_s_s = st.sidebar.number_input("Set PERSI (Stagione)", 0, 100, p1_def['p_tot'])
    c_g_s = st.sidebar.number_input("Partite Giocate", 1, 100, p1_def['count_tot'])
    c_f_5 = st.sidebar.number_input("Set VINTI (U5)", 0, 50, p1_def['v_5']) 
    c_s_5 = st.sidebar.number_input("Set PERSI (U5)", 0, 50, p1_def['p_5'])
    st.sidebar.markdown("---")
    st.sidebar.header(f"🔴 DATI {t_o[:10].upper()}")
    o_f_s = st.sidebar.number_input("Set VINTI (Stagione Ospite)", 0, 100, p2_def['v_tot'])
    o_s_s = st.sidebar.number_input("Set PERSI (Stagione Ospite)", 0, 100, p2_def['p_tot'])
    o_g_s = st.sidebar.number_input("Partite Giocate Ospite", 1, 100, p2_def['count_tot'])
    o_f_5 = st.sidebar.number_input("Set VINTI (U5 Ospite)", 0, 50, p2_def['v_5'])
    o_s_5 = st.sidebar.number_input("Set PERSI (U5 Ospite)", 0, 50, p2_def['p_5'])
    ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_g = 3

st.sidebar.markdown("---")
q1_b = st.sidebar.number_input("Quota 1", 1.00, 50.0, 2.00)
qx_b = st.sidebar.number_input("Quota X", 1.00, 50.0, 3.20 if is_calcio else (4.50 if is_hockey else 1.00))
q2_b = st.sidebar.number_input("Quota 2", 1.00, 50.0, 3.50)

st.title(f"🔬 SPORTS LAB PRO - MODULE: {sport}")
tab1, tab2, tab3 = st.tabs(["🎯 ENGINE MATRIX", "📊 VALUE RATING", "📂 DATABASE HUB"])

with tab1:
    if not is_tennis:
        st.info(f"📊 Valori Attesi (xG): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
        matrix = np.zeros((max_g, max_g))
        pc, po = [poisson(ex_c, i) for i in range(max_g)], [poisson(ex_o, i) for i in range(max_g)]
        for h in range(max_g):
            for a in range(max_g): matrix[h, a] = pc[h] * po[a]
        scen = list(dict.fromkeys([f"{int(round(ex_c))}-{int(round(ex_o))}", f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}", f"{int(math.floor(ex_c))}-{int(math.ceil(ex_o))}"]))
        c_c1, c_c2 = st.columns([2, 1.2])
        with c_c1:
            st.subheader("📊 Matrice Probabilità")
            st.dataframe(pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)]).style.format("{:.1f}%").background_gradient(cmap='Blues' if is_hockey else 'Greens', axis=None), height=230)
        with c_c2:
            st.subheader("🎯 Classifica Risultati")
            ris = []
            for h in range(max_g):
                for a in range(max_g):
                    p = matrix[h, a]; ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
            df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
            st.dataframe(df_r.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in scen else ['']*3, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, height=230, use_container_width=True)

        st.subheader("💡 Scenari Esatti")
        cs = st.columns(4)
        for i, rn in enumerate(scen[:4]):
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
            p_bi = gp(1,3,1,3); cb[0].metric("BILANCIATO", "T1 1-3 + T2 1-3", f"{p_bi:.1f}%"); 
            if cb[0].button("📌 Bil"): add_to_db("Bil: 1-3+1-3")
            p_dom = gp(2,4,0,1); cb[1].metric("DOMINIO", "T1 2-4 + T2 0-1", f"{p_dom:.1f}%");
            if cb[1].button("📌 Dom"): add_to_db("Dom: 2-4+0-1")
            p_goal = gp(1,3,1,3); cb[2].metric("GOAL", "GOAL Combo", f"{p_goal:.1f}%");
            if cb[2].button("📌 Goal"): add_to_db("Goal Combo")

            st.subheader("📈 Mercati Principali")
            p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
            ov25 = sum(matrix[r,c] for r in range(max_g) for c in range(max_g) if r+c > 2.5)*100
            mc = st.columns(6)
            mc[0].metric("1",f"{p1:.1f}%",f"QF:{100/p1:.2f}"); mc[1].metric("X",f"{px:.1f}%",f"QF:{100/px:.2f}"); mc[2].metric("2",f"{p2:.1f}%",f"QF:{100/p2:.2f}");
            mc[3].metric("O2.5",f"{ov25:.1f}%",f"QF:{100/ov25:.2f}"); mc[4].metric("G","50%","2.00"); mc[5].metric("NG","50%","2.00")
            
            st.subheader("🔢 Multigol")
            def gmm(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
            cmg = st.columns(4)
            for i, mg in enumerate([(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]):
                v = gmm(mg[0], mg[1]); cmg[i%4].metric(f"MG {mg[0]}-{mg[1]}", f"{v:.1f}%", f"QF:{100/v:.2f}")

        elif is_hockey:
            p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
            st.subheader("🎯 Margine Vittoria")
            t1_1g, t1_2g, t1_3p = sum(matrix[i,i-1] for i in range(1,max_g))*100, sum(matrix[i,i-2] for i in range(2,max_g))*100, sum(matrix[i,j] for i in range(3,max_g) for j in range(max_g) if i-j>=3)*100
            t2_1g, t2_2g, t2_3p = sum(matrix[i-1,i] for i in range(1,max_g))*100, sum(matrix[i-2,i] for i in range(2,max_g))*100, sum(matrix[i,j] for j in range(3,max_g) for i in range(max_g) if j-i>=3)*100
            rm1 = st.columns(4)
            rm1[0].metric("T1 +1G", f"{t1_1g:.1f}%"); rm1[1].metric("T1 +2G", f"{t1_2g:.1f}%"); rm1[2].metric("T1 +3G", f"{t1_3p:.1f}%"); rm1[3].metric("PAREGGIO", f"{px:.1f}%")
            rm2 = st.columns(3)
            rm2[0].metric("T2 +1G", f"{t2_1g:.1f}%"); rm2[1].metric("T2 +2G", f"{t2_2g:.1f}%"); rm2[2].metric("T2 +3G", f"{t2_3p:.1f}%")
            st.subheader("⚖️ TT & Handicap")
            tt1, tt2 = p1+(px/2), p2+(px/2)
            ctt = st.columns(4)
            ctt[0].metric("T/T 1", f"{tt1:.1f}%"); ctt[1].metric("T/T 2", f"{tt2:.1f}%"); ctt[2].metric("HDP 1(-1.5)", f"{(t1_2g+t1_3p):.1f}%"); ctt[3].metric("HDP 2(+1.5)", f"{(p2+px+t1_1g):.1f}%")

    elif is_tennis:
        st.info(f"📊 Set Attesi (xS): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
        r20, r21, r02, r12 = poisson(ex_c,2)*poisson(ex_o,0), poisson(ex_c,2)*poisson(ex_o,1), poisson(ex_c,0)*poisson(ex_o,2), poisson(ex_c,1)*poisson(ex_o,2)
        tr = r20+r21+r02+r12 if r20+r21+r02+r12>0 else 0.001
        s20, s21, s02, s12 = (r20/tr)*100, (r21/tr)*100, (r02/tr)*100, (r12/tr)*100
        p1_vincente, p2_vincente = s20+s21, s02+s12
        col1, col2 = st.columns([2, 1.2])
        with col1:
            st.subheader("🎯 Set Betting")
            st.dataframe(pd.DataFrame({"Ris":["2-0","2-1","0-2","1-2"],"Prob":[s20,s21,s02,s12],"QF":[100/s20,100/s21,100/s02,100/s12]}).style.format({"Prob":"{:.1f}%","QF":"{:.2f}"}), hide_index=True)
        with col2:
            st.subheader("🎾 T/T")
            st.metric(f"VITTORIA {t_h[:8]}", f"{p1_vincente:.1f}%", f"QF:{100/p1_vincente:.2f}"); st.metric(f"VITTORIA {t_o[:8]}", f"{p2_vincente:.1f}%", f"QF:{100/p2_vincente:.2f}")
        st.subheader("📈 ANALISI GAME & TIE-BREAK (STIMA)")
        avg_g = (s20*18.5 + s02*18.5 + s21*26.5 + s12*26.5)/100
        p_tb = ((s21+s12)*0.45) + ((s20+s02)*0.15)
        cg = st.columns(3)
        cg[0].metric("GAME MEDI", f"{avg_g:.1f}"); cg[1].metric("PROB. TIE-BREAK", f"{p_tb:.1f}%", f"QF:{100/p_tb:.2f}"); cg[2].metric("OVER 22.5", f"{(s21+s12+s20*0.2):.1f}%")

with tab2:
    st.subheader("📊 Ricerca Value Bet")
    if is_tennis:
        b1, b2 = p1_vincente, p2_vincente
    else:
        vH, vA = ex_c*10, ex_o*10; tot_v = vH+vA+(8 if is_hockey else 12)
        b1, b2 = (vH/tot_v)*100, (vA/tot_v)*100
    qf1, qf2 = 100/b1 if b1>0 else 0, 100/b2 if b2>0 else 0
    v1, v2 = st.columns(2); v1.metric("SEGNO 1", f"QF:{qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO"); v2.metric("SEGNO 2", f"QF:{qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")

with tab3:
    st.subheader("📂 Database Hub")
    if st.session_state.db:
        for m, prs in list(st.session_state.db.items()):
            st.markdown(f"**{m}**")
            if prs:
                for idx, p in enumerate(prs):
                    c1, c2, c3 = st.columns([4, 2, 1])
                    c1.write(p['scelta']); c2.write(p['esito'])
                    if c3.button("🗑️", key=f"dp_{m}_{idx}"): st.session_state.db[m].pop(idx); st.rerun()
            if st.button("Rimuovi Incontro", key=f"rm_{m}"): del st.session_state.db[m]; st.rerun()
