import streamlit as st
import math
import pandas as pd
import numpy as np
import re

# Configurazione Pagina
st.set_page_config(page_title="SPORTS LAB PRO", page_icon="🔬", layout="wide")

# --- INIZIALIZZAZIONE SESSION STATE (VERBOSE - COME ORIGINALE) ---
if 'db' not in st.session_state:
    st.session_state.db = {}

# Inizializzazione manuale per evitare tagli e garantire l'auto-update
if 'p1_v' not in st.session_state: st.session_state.p1_v = 15
if 'p1_p' not in st.session_state: st.session_state.p1_p = 10
if 'p1_g' not in st.session_state: st.session_state.p1_g = 10
if 'p1_v5' not in st.session_state: st.session_state.p1_v5 = 9
if 'p1_p5' not in st.session_state: st.session_state.p1_p5 = 2

if 'p2_v' not in st.session_state: st.session_state.p2_v = 12
if 'p2_p' not in st.session_state: st.session_state.p2_p = 12
if 'p2_g' not in st.session_state: st.session_state.p2_g = 10
if 'p2_v5' not in st.session_state: st.session_state.p2_v5 = 7
if 'p2_p5' not in st.session_state: st.session_state.p2_p5 = 4

# --- CSS LOOK PROFESSIONALE INTEGRALE (TUTTE LE RIGHE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    
    h1, h2, h3 { 
        font-family: 'Inter', sans-serif; 
        margin-top: -20px; 
        padding-bottom: 5px; 
        font-size: 1.2rem !important; 
        font-weight: 900 !important;
        color: #1a1a1a;
    }
    
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.05) !important;
        border: 1px solid rgba(128, 128, 128, 0.12) !important;
        padding: 12px 15px !important; 
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
    }
    
    div[data-testid="stMetricValue"] { 
        font-size: 17px !important; 
        font-weight: 800 !important; 
        color: #2e7d32 !important; 
    }
    
    button[kind="primary"] {
        background-color: #28a745 !important; 
        color: white !important;
        font-weight: bold !important; 
        border-radius: 8px !important;
        height: 44px !important; 
        width: 100% !important; 
        margin-top: 25px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(40, 167, 69, 0.25) !important;
    }
    
    hr { 
        margin: 1.5em 0 !important; 
        border: 1px solid rgba(128,128,128,0.1) !important; 
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
    # Cattura punteggi tipo "2 : 0", "2-1", "2 : 1"
    matches = re.findall(r'(\d+)\s*[:\-]\s*(\d+)', raw_text)
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
sport = st.sidebar.radio("Seleziona Disciplina", ["⚽ CALCIO", "🏒 HOCKEY", "🎾 TENNIS"], horizontal=True)

is_calcio = (sport == "⚽ CALCIO")
is_hockey = (sport == "🏒 HOCKEY")
is_tennis = (sport == "🎾 TENNIS")

st.sidebar.markdown("---")

# --- REGISTRAZIONE INCONTRO ---
st.write(f"### 📝 REGISTRAZIONE INCONTRO ({sport})")
col_reg1, col_reg2, col_reg3 = st.columns([3, 3, 1.5])

if is_calcio:
    team_h = col_reg1.text_input("Squadra Casa", value="Bologna")
    team_o = col_reg2.text_input("Squadra Ospite", value="Cagliari")
    icona = "⚽"
elif is_hockey:
    team_h = col_reg1.text_input("Team 1 (Casa/Preferito)", value="Kazakistan")
    team_o = col_reg2.text_input("Team 2 (Ospite/Sfavore)", value="Ucraina")
    icona = "🏒"
else:
    team_h = col_reg1.text_input("Giocatore 1 (Casa)", value="Sinner J.")
    team_o = col_reg2.text_input("Giocatore 2 (Ospite)", value="Alcaraz C.")
    icona = "🎾"

match_id = f"{icona} {team_h} - {team_o}"

if col_reg3.button("💾 SALVA INCONTRO", key="btn_save_master", type="primary"):
    if match_id not in st.session_state.db:
        st.session_state.db[match_id] = []
        st.toast("Match aggiunto al database!")

def add_to_db(pron):
    if match_id in st.session_state.db:
        st.session_state.db[match_id].append({'scelta': pron, 'esito': '⏳'})
        st.toast(f"Pronostico Inviato: {pron}")
    else:
        st.error("ERRORE: Devi prima salvare l'incontro!")

# --- LOGICA SIDEBAR (VERBOSE - NESSUN TAGLIO) ---
if is_calcio:
    st.sidebar.header("🏠 DATI CASA")
    c_f_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", 0, 200, 15)
    c_s_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", 0, 200, 10)
    c_g_s = st.sidebar.number_input("Partite Casa (Stagione)", 1, 100, 8)
    st.sidebar.subheader("🔥 Forma (Ultime 5)")
    c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", 0, 50, 8)
    c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", 0, 50, 4)
    
    st.sidebar.markdown("---")
    st.sidebar.header("🚀 DATI OSPITE")
    o_f_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", 0, 200, 10)
    o_s_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", 0, 200, 18)
    o_g_s = st.sidebar.number_input("Partite Ospite (Stagione)", 1, 100, 8)
    st.sidebar.subheader("🔥 Forma (Ultime 5) ")
    o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", 0, 50, 3)
    o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", 0, 50, 9)
    
    valore_atteso_casa = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    valore_atteso_ospite = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_goals = 6

elif is_hockey:
    st.sidebar.markdown("### ⚙️ OPZIONI HOCKEY")
    mod_hockey = st.sidebar.radio("Seleziona Formato", ["Semplice (PG/GF/GS)", "Avanzata (Campionati)"])
    if mod_hockey == "Semplice (PG/GF/GS)":
        h_pg = st.sidebar.number_input("Partite Giocate T1", 1, 100, 4)
        h_gf = st.sidebar.number_input("Reti Fatte T1", 0, 500, 18)
        h_gs = st.sidebar.number_input("Reti Subite T1", 0, 500, 7)
        st.sidebar.markdown("---")
        a_pg = st.sidebar.number_input("Partite Giocate T2", 1, 100, 4)
        a_gf = st.sidebar.number_input("Reti Fatte T2", 0, 500, 11)
        a_gs = st.sidebar.number_input("Reti Subite T2", 0, 500, 11)
        valore_atteso_casa = ((h_gf/h_pg) + (a_gs/a_pg)) / 2
        valore_atteso_ospite = ((a_gf/a_pg) + (h_gs/h_pg)) / 2
    else:
        st.sidebar.header(f"🔵 {team_h.upper()}")
        hc_f_s = st.sidebar.number_input("GF Casa", 0, 200, 15)
        hc_s_s = st.sidebar.number_input("GS Casa", 0, 200, 10)
        hc_g_s = st.sidebar.number_input("G Casa", 1, 100, 5)
        st.sidebar.header(f"🔴 {team_o.upper()}")
        ho_f_s = st.sidebar.number_input("GF Ospite", 0, 200, 10)
        ho_s_s = st.sidebar.number_input("GS Ospite", 0, 200, 18)
        ho_g_s = st.sidebar.number_input("G Ospite", 1, 100, 5)
        valore_atteso_casa = (w_avg(hc_f_s, 12, hc_g_s) + w_avg(ho_s_s, 14, ho_g_s)) / 2
        valore_atteso_ospite = (w_avg(ho_f_s, 9, ho_g_s) + w_avg(hc_s_s, 8, hc_g_s)) / 2
    max_goals = 9

elif is_tennis:
    st.sidebar.markdown("### ⚡ OMEGA FAST PARSER")
    raw_input1 = st.sidebar.text_area(f"Incolla qui H2H {team_h}", height=80, key="txt_t1")
    if raw_input1:
        res_t = parse_tennis_results(raw_input1)
        if res_t:
            st.session_state.p1_v = res_t['v']
            st.session_state.p1_p = res_t['p']
            st.session_state.p1_g = res_t['g']
            st.session_state.p1_v5 = res_t['v5']
            st.session_state.p1_p5 = res_t['p5']
    
    raw_input2 = st.sidebar.text_area(f"Incolla qui H2H {team_o}", height=80, key="txt_t2")
    if raw_input2:
        res_t = parse_tennis_results(raw_input2)
        if res_t:
            st.session_state.p2_v = res_t['v']
            st.session_state.p2_p = res_t['p']
            st.session_state.p2_g = res_t['g']
            st.session_state.p2_v5 = res_t['v5']
            st.session_state.p2_p5 = res_t['p5']

    st.sidebar.header(f"🔵 {team_h.upper()}")
    c_f_s = st.sidebar.number_input("Set Vinti Stagione", 0, 100, key="p1_v")
    c_s_s = st.sidebar.number_input("Set Persi Stagione", 0, 100, key="p1_p")
    c_g_s = st.sidebar.number_input("Partite Giocate Casa", 1, 100, key="p1_g")
    c_f_5 = st.sidebar.number_input("Set Vinti U5", 0, 50, key="p1_v5")
    c_s_5 = st.sidebar.number_input("Set Persi U5", 0, 50, key="p1_p5")
    
    st.sidebar.header(f"🔴 {team_o.upper()}")
    o_f_s = st.sidebar.number_input("Set Vinti Stagione ", 0, 100, key="p2_v")
    o_s_s = st.sidebar.number_input("Set Persi Stagione ", 0, 100, key="p2_p")
    o_g_s = st.sidebar.number_input("Partite Giocate Ospite", 1, 100, key="p2_g")
    o_f_5 = st.sidebar.number_input("Set Vinti U5 ", 0, 50, key="p2_v5")
    o_s_5 = st.sidebar.number_input("Set Persi U5 ", 0, 50, key="p2_p5")
    
    valore_atteso_casa = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    valore_atteso_ospite = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_goals = 3

st.sidebar.markdown("---")
qu_1 = st.sidebar.number_input("Quota 1", 1.0, 50.0, 2.0)
qu_x = st.sidebar.number_input("Quota X", 1.0, 50.0, 3.2 if is_calcio else 1.0)
qu_2 = st.sidebar.number_input("Quota 2", 1.0, 50.0, 3.5)

# --- MATRICE E TABS ---
tab_matrix, tab_value, tab_db = st.tabs(["🎯 ENGINE MATRIX", "📊 VALUE RATING", "📂 DATABASE HUB"])

with tab_matrix:
    if not is_tennis:
        st.info(f"📊 Valori Attesi (xG/Reti): **{team_h} {valore_atteso_casa:.2f}** | **{team_o} {valore_atteso_ospite:.2f}**")
        
        # Generazione Matrice Poisson
        matrice_p = np.zeros((max_goals, max_goals))
        dist_c = [poisson(valore_atteso_casa, i) for i in range(max_goals)]
        dist_o = [poisson(valore_atteso_ospite, j) for j in range(max_goals)]
        
        for h in range(max_goals):
            for a in range(max_goals):
                matrice_p[h, a] = dist_c[h] * dist_o[a]
        
        scenari_top = [
            f"{int(round(valore_atteso_casa))}-{int(round(valore_atteso_ospite))}",
            f"{int(math.ceil(valore_atteso_casa))}-{int(math.floor(valore_atteso_ospite))}",
            f"{int(math.floor(valore_atteso_casa))}-{int(math.ceil(valore_atteso_ospite))}"
        ]
        
        col_m1, col_m2 = st.columns([2, 1.2])
        
        with col_m1:
            st.subheader("📊 Matrice Probabilità")
            df_m = pd.DataFrame(matrice_p * 100, 
                                index=[f"C{i}" for i in range(max_goals)], 
                                columns=[f"O{i}" for i in range(max_goals)])
            st.dataframe(df_m.style.format("{:.1f}%").background_gradient(cmap='Greens'), use_container_width=True)
            
        with col_m2:
            st.subheader("🎯 Classifica Risultati")
            lista_final = []
            for h in range(max_goals):
                for a in range(max_goals):
                    prob_ris = matrice_p[h, a]
                    lista_final.append({"Risultato": f"{h}-{a}", "Prob": prob_ris * 100, "QF": 1/prob_ris if prob_ris > 0 else 0})
            
            df_ris = pd.DataFrame(lista_final).sort_values(by="Prob", ascending=False).head(10)
            # EVIDENZIAZIONE GIALLA
            st.dataframe(df_ris.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in scenari_top else ['']*3, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True)

        st.subheader("💡 Scenari Esatti Consigliati")
        cols_scen = st.columns(4)
        scen_list = list(dict.fromkeys(scenari_top))
        for i, nome_r in enumerate(scen_list[:4]):
            try:
                g_casa, g_ospite = map(int, nome_r.split('-'))
                pv = matrice_p[g_casa, g_ospite] * 100
                with cols_scen[i]:
                    st.metric("ESATTO", nome_r, f"{pv:.1f}% (QF:{100/pv:.2f})")
                    if st.button(f"📌 {nome_r}", key=f"btn_r_{i}"):
                        add_to_db(f"Esatto {nome_r}")
            except: pass

        if is_calcio:
            st.subheader("🚀 Scenari Combo & Strategie")
            def get_prob_range(c_l, c_h, o_l, o_h):
                return sum(matrice_p[h, a] for h in range(c_l, c_h+1) for a in range(o_l, o_h+1) if h < max_goals and a < max_goals) * 100
            
            c_combo = st.columns(3)
            p_bil = get_prob_range(1, 3, 1, 3)
            with c_combo[0]:
                st.metric("BILANCIATO", "T1 1-3 + T2 1-3", f"{p_bil:.1f}%")
                if st.button("📌 Invia Bilanciato"): add_to_db("Combo: T1 1-3 + T2 1-3")
                
            p_dom = get_prob_range(2, 4, 0, 1)
            with c_combo[1]:
                st.metric("DOMINIO", "T1 2-4 + T2 0-1", f"{p_dom:.1f}%")
                if st.button("📌 Invia Dominio"): add_to_db("Combo: T1 2-4 + T2 0-1")
                
            p_goal = get_prob_range(1, 3, 1, 3)
            with c_combo[2]:
                st.metric("COMBO GOAL", "T1 1-3 + T2 1-3", f"{p_goal:.1f}%")
                if st.button("📌 Invia Goal"): add_to_db("Combo Goal: T1 1-3 + T2 1-3")

            st.subheader("📈 Mercati Principali Calcio")
            prob_1 = np.sum(np.tril(matrice_p, -1)) * 100
            prob_x = np.trace(matrice_p) * 100
            prob_2 = np.sum(np.triu(matrice_p, 1)) * 100
            prob_ov25 = sum(matrice_p[r, c] for r in range(max_goals) for c in range(max_goals) if r+c > 2.5) * 100
            prob_goal = sum(matrice_p[h, a] for h in range(1, max_goals) for a in range(1, max_goals)) * 100
            
            m_cols = st.columns(6)
            m_cols[0].metric("1", f"{prob_1:.1f}%", f"QF:{100/prob_1:.2f}")
            m_cols[1].metric("X", f"{prob_x:.1f}%", f"QF:{100/prob_x:.2f}")
            m_cols[2].metric("2", f"{prob_2:.1f}%", f"QF:{100/prob_2:.2f}")
            m_cols[3].metric("O2.5", f"{prob_ov25:.1f}%", f"QF:{100/prob_ov25:.2f}")
            m_cols[4].metric("GOAL", f"{prob_goal:.1f}%", f"QF:{100/prob_goal:.2f}")
            m_cols[5].metric("NO GOAL", f"{100-prob_goal:.1f}%", f"QF:{100/(100-prob_goal):.2f}")
            
            st.subheader("🔢 Multigol (Dettaglio)")
            def sum_mg(low, high):
                return sum(matrice_p[r, c] for r in range(max_goals) for c in range(max_goals) if low <= r+c <= high) * 100
            
            col_mg1, col_mg2, col_mg3, col_mg4 = st.columns(4)
            mg12 = sum_mg(1, 2); col_mg1.metric("MG 1-2", f"{mg12:.1f}%", f"QF:{100/mg12:.2f}")
            mg13 = sum_mg(1, 3); col_mg2.metric("MG 1-3", f"{mg13:.1f}%", f"QF:{100/mg13:.2f}")
            mg14 = sum_mg(1, 4); col_mg3.metric("MG 1-4", f"{mg14:.1f}%", f"QF:{100/mg14:.2f}")
            mg23 = sum_mg(2, 3); col_mg4.metric("MG 2-3", f"{mg23:.1f}%", f"QF:{100/mg23:.2f}")
            
            mg24 = sum_mg(2, 4); col_mg1.metric("MG 2-4", f"{mg24:.1f}%", f"QF:{100/mg24:.2f}")
            mg25 = sum_mg(2, 5); col_mg2.metric("MG 2-5", f"{mg25:.1f}%", f"QF:{100/mg25:.2f}")
            mg34 = sum_mg(3, 4); col_mg3.metric("MG 3-4", f"{mg34:.1f}%", f"QF:{100/mg34:.2f}")
            mg35 = sum_mg(3, 5); col_mg4.metric("MG 3-5", f"{mg35:.1f}%", f"QF:{100/mg35:.2f}")

            st.markdown("---")
            col_team1, col_team2, col_dc = st.columns(3)
            with col_team1:
                st.write("**🏠 MULTIGOL CASA**")
                p1_mg12 = sum(dist_c[1:3]) * 100
                st.metric("CASA 1-2", f"{p1_mg12:.1f}%", f"QF:{100/p1_mg12:.2f}")
                p1_mg13 = sum(dist_c[1:4]) * 100
                st.metric("CASA 1-3", f"{p1_mg13:.1f}%", f"QF:{100/p1_mg13:.2f}")
                p1_mg23 = sum(dist_c[2:4]) * 100
                st.metric("CASA 2-3", f"{p1_mg23:.1f}%", f"QF:{100/p1_mg23:.2f}")
            
            with col_team2:
                st.write("**🚀 MULTIGOL OSPITE**")
                p2_mg12 = sum(dist_o[1:3]) * 100
                st.metric("OSPITE 1-2", f"{p2_mg12:.1f}%", f"QF:{100/p2_mg12:.2f}")
                p2_mg13 = sum(dist_o[1:4]) * 100
                st.metric("OSPITE 1-3", f"{p2_mg13:.1f}%", f"QF:{100/p2_mg13:.2f}")
                p2_mg23 = sum(dist_o[2:4]) * 100
                st.metric("OSPITE 2-3", f"{p2_mg23:.1f}%", f"QF:{100/p2_mg23:.2f}")
            
            with col_dc:
                st.write("**⚖️ DOPPIA CHANCE**")
                st.metric("1X", f"{prob_1+prob_x:.1f}%")
                st.metric("X2", f"{prob_2+prob_x:.1f}%")
                st.metric("12", f"{prob_1+prob_2:.1f}%")

        elif is_hockey:
            p_1 = np.sum(np.tril(matrice_p, -1)) * 100
            p_x = np.trace(matrice_p) * 100
            p_2 = np.sum(np.triu(matrice_p, 1)) * 100
            
            st.subheader("🎯 Margine Vittoria Hockey")
            m1_1g = sum(matrice_p[i, i-1] for i in range(1, max_goals)) * 100
            m1_2g = sum(matrice_p[i, i-2] for i in range(2, max_goals)) * 100
            m1_3p = sum(matrice_p[i, j] for i in range(3, max_goals) for j in range(max_goals) if i-j >= 3) * 100
            
            m2_1g = sum(matrice_p[i-1, i] for i in range(1, max_goals)) * 100
            m2_2g = sum(matrice_p[i-2, i] for i in range(2, max_goals)) * 100
            m2_3p = sum(matrice_p[i, j] for j in range(3, max_goals) for i in range(max_goals) if j-i >= 3) * 100
            
            c_rm1 = st.columns(4)
            c_rm1[0].metric("T1 +1 GOL", f"{m1_1g:.1f}%")
            c_rm1[1].metric("T1 +2 GOL", f"{m1_2g:.1f}%")
            c_rm1[2].metric("T1 +3+ GOL", f"{m1_3p:.1f}%")
            c_rm1[3].metric("X (PAR)", f"{p_x:.1f}%")
            
            c_rm2 = st.columns(3)
            c_rm2[0].metric("T2 +1 GOL", f"{m2_1g:.1f}%")
            c_rm2[1].metric("T2 +2 GOL", f"{m2_2g:.1f}%")
            c_rm2[2].metric("T2 +3+ GOL", f"{m2_3p:.1f}%")
            
            st.subheader("⚖️ Testa a Testa & Puck Line")
            c_hdp = st.columns(4)
            c_hdp[0].metric("T/T 1", f"{p_1 + (p_x/2):.1f}%")
            c_hdp[1].metric("T/T 2", f"{p_2 + (p_x/2):.1f}%")
            c_hdp[2].metric("Puck Line 1 (-1.5)", f"{m1_2g + m1_3p:.1f}%")
            c_hdp[3].metric("Puck Line 2 (+1.5)", f"{p_2 + p_x + m1_1g:.1f}%")

    elif is_tennis:
        st.info(f"📊 Valori Attesi (Set): **{team_h} {valore_atteso_casa:.2f}** | **{team_o} {valore_atteso_ospite:.2f}**")
        
        # Calcolo Set Betting
        p20 = poisson(valore_atteso_casa, 2) * poisson(valore_atteso_ospite, 0)
        p21 = poisson(valore_atteso_casa, 2) * poisson(valore_atteso_ospite, 1)
        p02 = poisson(valore_atteso_casa, 0) * poisson(valore_atteso_ospite, 2)
        p12 = poisson(valore_atteso_casa, 1) * poisson(valore_atteso_ospite, 2)
        t_p = p20 + p21 + p02 + p12 if (p20+p21+p02+p12) > 0 else 0.001
        
        s_20, s_21, s_02, s_12 = (p20/t_p)*100, (p21/t_p)*100, (p02/t_p)*100, (p12/t_p)*100
        tennis_p1v, tennis_p2v = s_20 + s_21, s_02 + s_12
        
        c_s1, c_s2 = st.columns([2, 1.2])
        with c_s1:
            st.subheader("🎯 Set Betting (Risultati)")
            df_ten = pd.DataFrame({
                "Risultato": ["2-0", "2-1", "0-2", "1-2"],
                "Probabilità": [s_20, s_21, s_02, s_12],
                "Quota Fiera": [100/s_20, 100/s_21, 100/s_02, 100/s_12]
            })
            # EVIDENZIAZIONE GIALLA TENNIS
            st.dataframe(df_ten.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Probabilità'] == df_ten['Probabilità'].max() else ['']*3, axis=1).format({"Probabilità": "{:.1f}%", "Quota Fiera": "{:.2f}"}), hide_index=True)
            
        with c_s2:
            st.subheader("🎾 Testa a Testa")
            st.metric(f"VINCITORE: {team_h[:10]}", f"{tennis_p1v:.1f}%", f"QF: {100/tennis_p1v:.2f}")
            st.metric(f"VINCITORE: {team_o[:10]}", f"{tennis_p2v:.1f}%", f"QF: {100/tennis_p2v:.2f}")
            
        st.subheader("⚖️ Set Totali & Handicap Set")
        c_set_tot = st.columns(4)
        c_set_tot[0].metric("UNDER 2.5 SET", f"{s_20 + s_02:.1f}%", f"QF: {100/(s_20+s_02):.2f}")
        c_set_tot[1].metric("OVER 2.5 SET", f"{s_21 + s_12:.1f}%", f"QF: {100/(s_21+s_12):.2f}")
        c_set_tot[2].metric("HDP SET 1 (-1.5)", f"{s_20:.1f}%", f"QF: {100/s_20:.2f}")
        c_set_tot[3].metric("HDP SET 2 (+1.5)", f"{s_02 + s_12 + s_21:.1f}%", f"QF: {100/(s_02+s_12+s_21):.2f}")
        
        st.subheader("📈 ANALISI GAME & TIE-BREAK (STIMA)")
        avg_game = (s_20 * 18.5 + s_02 * 18.5 + s_21 * 26.5 + s_12 * 26.5) / 100
        p_tiebreak = ((s_21 + s_12) * 0.45) + ((s_20 + s_02) * 0.15)
        p_over225 = ((s_21 + s_12) * 0.95) + ((s_20 + s_02) * 0.15)
        
        c_game1, c_game2, c_game3 = st.columns(3)
        c_game1.metric("GAME MEDI ATTESI", f"{avg_game:.1f}")
        c_game2.metric("PROB. TIE-BREAK", f"{p_tiebreak:.1f}%", f"QF: {100/p_tiebreak:.2f}")
        c_game3.metric("OVER 22.5 GAME", f"{p_over225:.1f}%", f"QF: {100/p_over225:.2f}")
        
        st.write("**📊 ALTRI MERCATI GAME TENNIS**")
        c_game_alt1, c_game_alt2, c_game_alt3 = st.columns(3)
        p_s1o95 = (p_tiebreak / 2) + 42
        p_u205 = (s_20 + s_02) * 0.75
        p_g1set = tennis_p1v + s_12
        c_game_alt1.metric("SET 1 OVER 9.5", f"{p_s1o95:.1f}%", f"QF: {100/p_s1o95:.2f}")
        c_game_alt2.metric("UNDER 20.5 GAME", f"{p_u205:.1f}%", f"QF: {100/p_u205:.2f}")
        c_game_alt3.metric("G1 VINCE ALMENO 1 SET", f"{p_g1set:.1f}%", f"QF: {100/p_g1set:.2f}")

with tab_value:
    st.subheader("📊 Ricerca Value Bet")
    if is_tennis:
        b_1, b_2 = tennis_p1v, tennis_p2v
    else:
        v_h, v_o = valore_atteso_casa * 10, valore_atteso_ospite * 10
        t_v = v_h + v_o + (8 if is_hockey else 12)
        b_1, b_2 = (v_h / t_v) * 100, (v_o / t_v) * 100
        
    qf_1, qf_2 = 100/b_1 if b_1 > 0 else 0, 100/b_2 if b_2 > 0 else 0
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.metric("SEGNO 1", f"QF: {qf_1:.2f}", "✅ VALUE" if qu_1 > qf_1 else "❌ NO")
    with col_v2:
        st.metric("SEGNO 2", f"QF: {qf_2:.2f}", "✅ VALUE" if qu_2 > qf_2 else "❌ NO")

with tab_db:
    st.subheader("📂 DATABASE HUB")
    if st.session_state.db:
        for match, entries in list(st.session_state.db.items()):
            st.markdown(f"🚩 **{match}**")
            if entries:
                for index, entry in enumerate(entries):
                    db1, db2, db3 = st.columns([4, 2, 1])
                    db1.write(entry['scelta'])
                    esito = entry['esito']
                    if db2.button(esito, key=f"t_{match}_{index}"):
                        nuovo_esito = {'⏳': 'WIN', 'WIN': 'LOSS', 'LOSS': '⏳'}[esito]
                        st.session_state.db[match][index]['esito'] = nuovo_esito
                        st.rerun()
                    if db3.button("🗑️", key=f"d_{match}_{index}"):
                        st.session_state.db[match].pop(index)
                        st.rerun()
            if st.button("Elimina Match Intero", key=f"rem_{match}"):
                del st.session_state.db[match]
                st.rerun()
            st.markdown("---")
    else:
        st.info("Database vuoto.")
