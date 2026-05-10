import streamlit as st
import math
import pandas as pd
import numpy as np
import re

# Configurazione Pagina
st.set_page_config(page_title="SPORTS LAB PRO", page_icon="🔬", layout="wide")

# --- MEMORIA DATABASE E AUTO-UPDATE ---
if 'db' not in st.session_state:
    st.session_state.db = {}

if 'p1_vals' not in st.session_state:
    st.session_state.p1_vals = {'v': 15, 'p': 10, 'g': 10, 'v5': 9, 'p5': 2}

if 'p2_vals' not in st.session_state:
    st.session_state.p2_vals = {'v': 12, 'p': 12, 'g': 10, 'v5': 7, 'p5': 4}

# --- CSS LOOK PROFESSIONALE INTEGRALE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { 
        font-family: 'Roboto', sans-serif; 
        margin-top: -20px; 
        padding-bottom: 5px; 
        font-size: 1.2rem !important; 
        color: #1E1E1E;
    }
    
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid rgba(128, 128, 128, 0.1) !important;
        padding: 10px 15px !important; 
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    div[data-testid="stMetricValue"] { 
        font-size: 16px !important; 
        font-weight: 900 !important; 
        color: #2E7D32 !important;
    }
    
    button[kind="primary"] {
        background-color: #28a745 !important; 
        color: white !important;
        font-weight: bold !important; 
        border-radius: 6px !important;
        height: 45px !important; 
        width: 100% !important; 
        margin-top: 25px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(40, 167, 69, 0.2) !important;
    }
    
    hr { 
        margin: 1.2em 0 !important; 
        border: 1px solid rgba(128,128,128,0.15) !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI MATEMATICHE ---
def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

def w_avg(sf, r5, gs): 
    return ((sf / (gs if gs > 0 else 1)) * 0.4) + ((r5 / 5) * 0.6)

def parse_tennis_results(raw_text):
    matches = re.findall(r'(\d+)[:\-](\d+)', raw_text)
    if not matches: return None
    recent = matches[:10]
    last5 = matches[:5]
    return {
        'v': sum(int(m[0]) for m in recent),
        'p': sum(int(m[1]) for m in recent),
        'g': len(recent),
        'v5': sum(int(m[0]) for m in last5),
        'p5': sum(int(m[1]) for m in last5)
    }

# --- SELETTORE SPORT (SIDEBAR) ---
st.sidebar.markdown("### 🔬 SPORTS LAB PRO")
sport = st.sidebar.radio("Scegli Disciplina", ["⚽ CALCIO", "🏒 HOCKEY", "🎾 TENNIS"], horizontal=True)

is_calcio = sport == "⚽ CALCIO"
is_hockey = sport == "🏒 HOCKEY"
is_tennis = sport == "🎾 TENNIS"

# --- REGISTRAZIONE INCONTRO ---
st.write(f"### 📝 REGISTRAZIONE INCONTRO ({sport})")
col_t1, col_t2, col_btn = st.columns([3, 3, 1.5])

if is_calcio:
    t_h = col_t1.text_input("Squadra Casa", value="Bologna")
    t_o = col_t2.text_input("Squadra Ospite", value="Cagliari")
    icona = "⚽"
elif is_hockey:
    t_h = col_t1.text_input("Team 1 (Casa/Pref)", value="Kazakistan")
    t_o = col_t2.text_input("Team 2 (Ospite/Sfav)", value="Ucraina")
    icona = "🏒"
else:
    t_h = col_t1.text_input("Giocatore 1", value="Sinner J.")
    t_o = col_t2.text_input("Giocatore 2", value="Alcaraz C.")
    icona = "🎾"

match_name = f"{icona} {t_h} - {t_o}"

if col_btn.button("💾 SALVA INCONTRO", key="save_btn_reale", type="primary"):
    if match_name not in st.session_state.db:
        st.session_state.db[match_name] = []
        st.toast("Incontro registrato correttamente!")

def add_to_db(pron):
    if match_name in st.session_state.db:
        st.session_state.db[match_name].append({'scelta': pron, 'esito': '⏳'})
        st.toast(f"Pronostico inviato: {pron}")
    else:
        st.error("ERRORE: Devi prima salvare l'incontro!")

st.sidebar.markdown("---")

# --- SIDEBAR DINAMICA (LOGICA INTEGRALE) ---
if is_calcio:
    st.sidebar.header("🏠 DATI CASA")
    c_f_s = st.sidebar.number_input("Gol Fatti Stagione", 0, 200, 15)
    c_s_s = st.sidebar.number_input("Gol Subiti Stagione", 0, 200, 10)
    c_g_s = st.sidebar.number_input("Partite Giocate Casa", 1, 100, 8)
    st.sidebar.subheader("🔥 Forma (U5)")
    c_f_5 = st.sidebar.number_input("Gol Fatti (U5)", 0, 50, 8)
    c_s_5 = st.sidebar.number_input("Gol Subiti (U5)", 0, 50, 4)
    
    st.sidebar.markdown("---")
    st.sidebar.header("🚀 DATI OSPITE")
    o_f_s = st.sidebar.number_input("Gol Fatti Stagione ", 0, 200, 10)
    o_s_s = st.sidebar.number_input("Gol Subiti Stagione ", 0, 200, 18)
    o_g_s = st.sidebar.number_input("Partite Giocate Ospite ", 1, 100, 8)
    st.sidebar.subheader("🔥 Forma (U5) ")
    o_f_5 = st.sidebar.number_input("Gol Fatti (U5) ", 0, 50, 3)
    o_s_5 = st.sidebar.number_input("Gol Subiti (U5) ", 0, 50, 9)
    
    ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_g = 6

elif is_hockey:
    formato_h = st.sidebar.radio("FORMATO DATI", ["📊 Semplice (Mondiali)", "🔥 Avanzata (Campionati)"])
    if formato_h == "📊 Semplice (Mondiali)":
        h_pg = st.sidebar.number_input("Partite Giocate T1", 1, 100, 4)
        h_gf = st.sidebar.number_input("Reti Fatte T1", 0, 500, 18)
        h_gs = st.sidebar.number_input("Reti Subite T1", 0, 500, 7)
        st.sidebar.markdown("---")
        a_pg = st.sidebar.number_input("Partite Giocate T2", 1, 100, 4)
        a_gf = st.sidebar.number_input("Reti Fatte T2", 0, 500, 11)
        a_gs = st.sidebar.number_input("Reti Subite T2", 0, 500, 11)
        ex_c = ((h_gf/h_pg) + (a_gs/a_pg)) / 2
        ex_o = ((a_gf/a_pg) + (h_gs/h_pg)) / 2
    else:
        st.sidebar.header(f"🔵 {t_h[:10].upper()}")
        c_f_s = st.sidebar.number_input("GF Casa", 0, 200, 15)
        c_s_s = st.sidebar.number_input("GS Casa", 0, 200, 10)
        c_g_s = st.sidebar.number_input("Partite Casa", 1, 100, 5)
        st.sidebar.header(f"🔴 {t_o[:10].upper()}")
        o_f_s = st.sidebar.number_input("GF Ospite", 0, 200, 10)
        o_s_s = st.sidebar.number_input("GS Ospite", 0, 200, 18)
        o_g_s = st.sidebar.number_input("Partite Ospite", 1, 100, 5)
        ex_c = (w_avg(c_f_s, 12, c_g_s) + w_avg(o_s_s, 14, o_g_s)) / 2
        ex_o = (w_avg(o_f_s, 9, o_g_s) + w_avg(c_s_s, 8, c_g_s)) / 2
    max_g = 9

elif is_tennis:
    st.sidebar.markdown("### ⚡ OMEGA FAST PARSER")
    raw1 = st.sidebar.text_area(f"Incolla H2H {t_h}", height=80, key="tennis_raw1")
    if raw1:
        res = parse_tennis_results(raw1)
        if res: st.session_state.p1_vals = res
    
    raw2 = st.sidebar.text_area(f"Incolla H2H {t_o}", height=80, key="tennis_raw2")
    if raw2:
        res = parse_tennis_results(raw2)
        if res: st.session_state.p2_vals = res

    st.sidebar.header(f"🔵 {t_h.upper()}")
    c_f_s = st.sidebar.number_input("Set Vinti Stagione", 0, 200, st.session_state.p1_vals['v'])
    c_s_s = st.sidebar.number_input("Set Persi Stagione", 0, 200, st.session_state.p1_vals['p'])
    c_g_s = st.sidebar.number_input("Partite Giocate G1", 1, 100, st.session_state.p1_vals['g'])
    c_f_5 = st.sidebar.number_input("Set Vinti U5", 0, 50, st.session_state.p1_vals['v5'])
    c_s_5 = st.sidebar.number_input("Set Persi U5", 0, 50, st.session_state.p1_vals['p5'])
    
    st.sidebar.header(f"🔴 {t_o.upper()}")
    o_f_s = st.sidebar.number_input("Set Vinti Stagione Osp", 0, 200, st.session_state.p2_vals['v'])
    o_s_s = st.sidebar.number_input("Set Persi Stagione Osp", 0, 200, st.session_state.p2_vals['p'])
    o_g_s = st.sidebar.number_input("Partite Giocate G2 ", 1, 100, st.session_state.p2_vals['g'])
    o_f_5 = st.sidebar.number_input("Set Vinti U5 Osp", 0, 50, st.session_state.p2_vals['v5'])
    o_s_5 = st.sidebar.number_input("Set Persi U5 Osp", 0, 50, st.session_state.p2_vals['p5'])
    
    ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_g = 3

st.sidebar.markdown("---")
q1_p = st.sidebar.number_input("Quota 1", 1.0, 50.0, 2.0)
qx_p = st.sidebar.number_input("Quota X", 1.0, 50.0, 3.2 if is_calcio else 1.0)
q2_p = st.sidebar.number_input("Quota 2", 1.0, 50.0, 3.5)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🎯 ENGINE MATRIX", "📊 VALUE RATING", "📂 DATABASE HUB"])

with tab1:
    if not is_tennis:
        st.info(f"📊 Valori Attesi (xG): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
        
        matrix = np.zeros((max_g, max_g))
        prob_casa = [poisson(ex_c, i) for i in range(max_g)]
        prob_ospite = [poisson(ex_o, i) for i in range(max_g)]
        
        for h in range(max_g):
            for a in range(max_g):
                matrix[h, a] = prob_casa[h] * prob_ospite[a]
        
        scenari = [
            f"{int(round(ex_c))}-{int(round(ex_o))}",
            f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}",
            f"{int(math.floor(ex_c))}-{int(math.ceil(ex_o))}"
        ]
        
        col_m1, col_m2 = st.columns([2, 1.2])
        
        with col_m1:
            st.subheader("📊 Matrice Probabilità")
            df_matrix = pd.DataFrame(matrix * 100, 
                                     index=[f"C{i}" for i in range(max_g)], 
                                     columns=[f"O{i}" for i in range(max_g)])
            st.dataframe(df_matrix.style.format("{:.1f}%").background_gradient(cmap='Greens'), use_container_width=True)
            
        with col_m2:
            st.subheader("🎯 Classifica Risultati")
            lista_ris = []
            for h in range(max_g):
                for a in range(max_g):
                    p = matrix[h, a]
                    lista_ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
            
            df_classifica = pd.DataFrame(lista_ris).sort_values(by="Prob", ascending=False).head(10)
            st.dataframe(df_classifica.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in scenari else ['']*3, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True)

        st.subheader("💡 Scenari Esatti")
        cols_scen = st.columns(4)
        scen_unici = list(dict.fromkeys(scenari))
        for i, ris_nome in enumerate(scen_unici[:4]):
            try:
                g_c, g_o = map(int, ris_nome.split('-'))
                p_ris = matrix[g_c, g_o] * 100
                with cols_scen[i]:
                    st.metric("ESATTO", ris_nome, f"{p_ris:.1f}% (QF:{100/p_ris:.2f})")
                    if st.button(f"📌 {ris_nome}", key=f"btn_s_{i}"):
                        add_to_db(f"Esatto {ris_nome}")
            except: pass

        if is_calcio:
            st.subheader("🚀 Scenari Combo")
            def get_p(c_min, c_max, o_min, o_max):
                return sum(matrix[h, a] for h in range(c_min, c_max+1) for a in range(o_min, o_max+1) if h < max_g and a < max_g) * 100
            
            cols_combo = st.columns(3)
            p_bil = get_p(1, 3, 1, 3)
            with cols_combo[0]:
                st.metric("BILANCIATO", "T1 1-3 + T2 1-3", f"{p_bil:.1f}% (QF:{100/p_bil:.2f})")
                if st.button("📌 Invia Bilanciato"): add_to_db("Bilanciato: T1 1-3 + T2 1-3")
            
            p_dom = get_p(2, 4, 0, 1)
            with cols_combo[1]:
                st.metric("DOMINIO", "T1 2-4 + T2 0-1", f"{p_dom:.1f}% (QF:{100/p_dom:.2f})")
                if st.button("📌 Invia Dominio"): add_to_db("Dominio: T1 2-4 + T2 0-1")
            
            p_goal = get_p(1, 3, 1, 3)
            with cols_combo[2]:
                st.metric("COMBO GOAL", "T1 1-3 + T2 1-3", f"{p_goal:.1f}% (QF:{100/p_goal:.2f})")
                if st.button("📌 Invia Goal"): add_to_db("Combo Goal: T1 1-3 + T2 1-3")

            st.subheader("📈 Mercati Principali")
            p1 = np.sum(np.tril(matrix, -1)) * 100
            px = np.trace(matrix) * 100
            p2 = np.sum(np.triu(matrix, 1)) * 100
            ov25 = sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if r+c > 2.5) * 100
            p_goal_s = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
            
            mc = st.columns(6)
            mc[0].metric("1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
            mc[1].metric("X", f"{px:.1f}%", f"QF:{100/px:.2f}")
            mc[2].metric("2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
            mc[3].metric("OVER 2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
            mc[4].metric("GOAL", f"{p_goal_s:.1f}%", f"QF:{100/p_goal_s:.2f}")
            mc[5].metric("NO GOAL", f"{100-p_goal_s:.1f}%", f"QF:{100/(100-p_goal_s):.2f}")
            
            st.subheader("🔢 Multigol")
            def calc_mg(l, h):
                return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
            
            mg_cols = st.columns(4)
            m12 = calc_mg(1, 2); mg_cols[0].metric("MULTIGOL 1-2", f"{m12:.1f}%", f"QF:{100/m12:.2f}")
            m13 = calc_mg(1, 3); mg_cols[1].metric("MULTIGOL 1-3", f"{m13:.1f}%", f"QF:{100/m13:.2f}")
            m14 = calc_mg(1, 4); mg_cols[2].metric("MULTIGOL 1-4", f"{m14:.1f}%", f"QF:{100/m14:.2f}")
            m23 = calc_mg(2, 3); mg_cols[3].metric("MULTIGOL 2-3", f"{m23:.1f}%", f"QF:{100/m23:.2f}")
            
            m24 = calc_mg(2, 4); mg_cols[0].metric("MULTIGOL 2-4", f"{m24:.1f}%", f"QF:{100/m24:.2f}")
            m25 = calc_mg(2, 5); mg_cols[1].metric("MULTIGOL 2-5", f"{m25:.1f}%", f"QF:{100/m25:.2f}")
            m34 = calc_mg(3, 4); mg_cols[2].metric("MULTIGOL 3-4", f"{m34:.1f}%", f"QF:{100/m34:.2f}")
            m35 = calc_mg(3, 5); mg_cols[3].metric("MULTIGOL 3-5", f"{m35:.1f}%", f"QF:{100/m35:.2f}")

            st.markdown("---")
            col_t1, col_t2, col_dc = st.columns(3)
            with col_t1:
                st.write("**🏠 MULTIGOL TEAM 1**")
                p1_12 = sum(prob_casa[i] for i in range(1, 3)) * 100
                st.metric("T1 1-2", f"{p1_12:.1f}%", f"QF:{100/p1_12:.2f}")
                p1_13 = sum(prob_casa[i] for i in range(1, 4)) * 100
                st.metric("T1 1-3", f"{p1_13:.1f}%", f"QF:{100/p1_13:.2f}")
                p1_23 = sum(prob_casa[i] for i in range(2, 4)) * 100
                st.metric("T1 2-3", f"{p1_23:.1f}%", f"QF:{100/p1_23:.2f}")
            
            with col_t2:
                st.write("**🚀 MULTIGOL TEAM 2**")
                p2_12 = sum(prob_ospite[i] for i in range(1, 3)) * 100
                st.metric("T2 1-2", f"{p2_12:.1f}%", f"QF:{100/p2_12:.2f}")
                p2_13 = sum(prob_ospite[i] for i in range(1, 4)) * 100
                st.metric("T2 1-3", f"{p2_13:.1f}%", f"QF:{100/p2_13:.2f}")
                p2_23 = sum(prob_ospite[i] for i in range(2, 4)) * 100
                st.metric("T2 2-3", f"{p2_23:.1f}%", f"QF:{100/p2_23:.2f}")
            
            with col_dc:
                st.write("**⚖️ DOPPIA CHANCE**")
                st.metric("1X", f"{p1+px:.1f}%", f"QF:{100/(p1+px):.2f}")
                st.metric("X2", f"{p2+px:.1f}%", f"QF:{100/(p2+px):.2f}")
                st.metric("12", f"{p1+p2:.1f}%", f"QF:{100/(p1+p2):.2f}")

        elif is_hockey:
            p1 = np.sum(np.tril(matrix, -1)) * 100
            px = np.trace(matrix) * 100
            p2 = np.sum(np.triu(matrix, 1)) * 100
            
            st.subheader("🎯 Margine Vittoria")
            t1_1g = sum(matrix[i, i-1] for i in range(1, max_g)) * 100
            t1_2g = sum(matrix[i, i-2] for i in range(2, max_g)) * 100
            t1_3p = sum(matrix[i, j] for i in range(3, max_g) for j in range(max_g) if i-j >= 3) * 100
            
            t2_1g = sum(matrix[i-1, i] for i in range(1, max_g)) * 100
            t2_2g = sum(matrix[i-2, i] for i in range(2, max_g)) * 100
            t2_3p = sum(matrix[i, j] for j in range(3, max_g) for i in range(max_g) if j-i >= 3) * 100
            
            rm1 = st.columns(4)
            rm1[0].metric("T1 +1 GOL", f"{t1_1g:.1f}%")
            rm1[1].metric("T1 +2 GOL", f"{t1_2g:.1f}%")
            rm1[2].metric("T1 +3+ GOL", f"{t1_3p:.1f}%")
            rm1[3].metric("X (PAREGGIO)", f"{px:.1f}%")
            
            rm2 = st.columns(3)
            rm2[0].metric("T2 +1 GOL", f"{t2_1g:.1f}%")
            rm2[1].metric("T2 +2 GOL", f"{t2_2g:.1f}%")
            rm2[2].metric("T2 +3+ GOL", f"{t2_3p:.1f}%")
            
            st.subheader("⚖️ Testa a Testa & Handicap")
            ctt = st.columns(4)
            ctt[0].metric("T/T 1", f"{p1 + (px/2):.1f}%")
            ctt[1].metric("T/T 2", f"{p2 + (px/2):.1f}%")
            ctt[2].metric("Puck Line 1 (-1.5)", f"{t1_2g + t1_3p:.1f}%")
            ctt[3].metric("Puck Line 2 (+1.5)", f"{p2 + px + t1_1g:.1f}%")

    elif is_tennis:
        st.info(f"📊 xS (Set Attesi): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
        
        # Calcolo Set Betting Poisson (Normalizzato)
        r20 = poisson(ex_c, 2) * poisson(ex_o, 0)
        r21 = poisson(ex_c, 2) * poisson(ex_o, 1)
        r02 = poisson(ex_c, 0) * poisson(ex_o, 2)
        r12 = poisson(ex_c, 1) * poisson(ex_o, 2)
        tot_r = r20 + r21 + r02 + r12 if (r20+r21+r02+r12) > 0 else 0.001
        
        s20, s21, s02, s12 = (r20/tot_r)*100, (r21/tot_r)*100, (r02/tot_r)*100, (r12/tot_r)*100
        p1_v, p2_v = s20 + s21, s02 + s12
        
        col_s1, col_s2 = st.columns([2, 1.2])
        with col_s1:
            st.subheader("🎯 Set Betting (Risultato Esatto)")
            df_set = pd.DataFrame({
                "Risultato": ["2-0", "2-1", "0-2", "1-2"],
                "Probabilità": [s20, s21, s02, s12],
                "Quota Fiera": [100/s20, 100/s21, 100/s02, 100/s12]
            })
            st.dataframe(df_set.style.format({"Probabilità": "{:.1f}%", "Quota Fiera": "{:.2f}"}), hide_index=True)
            
        with col_s2:
            st.subheader("🎾 Testa a Testa")
            st.metric(f"VINCITORE: {t_h[:10]}", f"{p1_v:.1f}%", f"QF: {100/p1_v:.2f}")
            st.metric(f"VINCITORE: {t_o[:10]}", f"{p2_v:.1f}%", f"QF: {100/p2_v:.2f}")
            
        st.subheader("⚖️ Set Totali & Handicap Set")
        st_cols = st.columns(4)
        st_cols[0].metric("UNDER 2.5 SET", f"{s20 + s02:.1f}%", f"QF: {100/(s20+s02):.2f}")
        st_cols[1].metric("OVER 2.5 SET", f"{s21 + s12:.1f}%", f"QF: {100/(s21+s12):.2f}")
        st_cols[2].metric("HDP SET 1 (-1.5)", f"{s20:.1f}%", f"QF: {100/s20:.2f}")
        st_cols[3].metric("HDP SET 2 (+1.5)", f"{s02 + s12 + s21:.1f}%", f"QF: {100/(s02+s12+s21):.2f}")
        
        st.subheader("📈 ANALISI GAME & TIE-BREAK (STIMA)")
        avg_g = (s20 * 18.5 + s02 * 18.5 + s21 * 26.5 + s12 * 26.5) / 100
        p_tb = ((s21 + s12) * 0.45) + ((s20 + s02) * 0.15)
        p_o22 = ((s21 + s12) * 0.95) + ((s20 + s02) * 0.15)
        
        cg_cols = st.columns(3)
        cg_cols[0].metric("GAME MEDI ATTESI", f"{avg_g:.1f}")
        cg_cols[1].metric("PROB. TIE-BREAK", f"{p_tb:.1f}%", f"QF: {100/p_tb:.2f}")
        cg_cols[2].metric("OVER 22.5 GAME", f"{p_o22:.1f}%", f"QF: {100/p_o22:.2f}")
        
        st.write("**📊 ALTRI MERCATI GAME**")
        cga_cols = st.columns(3)
        p_s1o9 = (p_tb / 2) + 42
        p_u20 = (s20 + s02) * 0.75
        p_g1_set = p1_v + s12
        cga_cols[0].metric("SET 1 OVER 9.5", f"{p_s1o9:.1f}%", f"QF: {100/p_s1o9:.2f}")
        cga_cols[1].metric("UNDER 20.5 GAME", f"{p_u20:.1f}%", f"QF: {100/p_u20:.2f}")
        cga_cols[2].metric("G1 VINCE ALMENO 1 SET", f"{p_g1_set:.1f}%", f"QF: {100/p_g1_set:.2f}")

with tab2:
    st.subheader("📊 Ricerca Value Bet")
    if is_tennis:
        b1, b2 = p1_v, p2_v
    else:
        vH, vA = ex_c * 10, ex_o * 10
        tot_val = vH + vA + (8 if is_hockey else 12)
        b1, b2 = (vH / tot_val) * 100, (vA / tot_val) * 100
        
    qf1, qf2 = 100/b1 if b1 > 0 else 0, 100/b2 if b2 > 0 else 0
    
    val_c1, val_c2 = st.columns(2)
    with val_c1:
        st.metric("SEGNO 1", f"QF: {qf1:.2f}", "✅ VALUE" if q1_p > qf1 else "❌ NO")
    with val_c2:
        st.metric("SEGNO 2", f"QF: {qf2:.2f}", "✅ VALUE" if q2_p > qf2 else "❌ NO")

with tab3:
    st.subheader("📂 DATABASE HUB")
    if st.session_state.db:
        for m_name, prons in list(st.session_state.db.items()):
            st.markdown(f"🚩 **{m_name}**")
            if prons:
                for idx, p_item in enumerate(prons):
                    db_c1, db_c2, db_c3 = st.columns([4, 2, 1])
                    db_c1.write(p_item['scelta'])
                    esito_curr = p_item['esito']
                    if db_c2.button(esito_curr, key=f"togg_{m_name}_{idx}"):
                        nuovo = {'⏳': 'WIN', 'WIN': 'LOSS', 'LOSS': '⏳'}[esito_curr]
                        st.session_state.db[m_name][idx]['esito'] = nuovo
                        st.rerun()
                    if db_c3.button("🗑️", key=f"delp_{m_name}_{idx}"):
                        st.session_state.db[m_name].pop(idx)
                        st.rerun()
            if st.button("Elimina Intero Match", key=f"rem_{m_name}"):
                del st.session_state.db[m_name]
                st.rerun()
            st.markdown("---")
    else:
        st.info("Il database è attualmente vuoto. Salva un incontro per iniziare.")
