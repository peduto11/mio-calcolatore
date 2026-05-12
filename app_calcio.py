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
    if lmbda <= 0: 
        return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

def w_avg(sf, r5, gs): 
    return ((sf / (gs if gs>0 else 1)) * 0.4) + ((r5 / 5) * 0.6)

# --- FUNZIONE PARSER TESTO TENNIS (Estrae i SET) ---
def analizza_testo_tennis_set(testo_incollato):
    if not testo_incollato or testo_incollato.strip() == "":
        return 0, 0, 0, 0, 0 

    # Aggiornata la regex per supportare trattini (2-0), due punti (2:0) e anche i numeri su righe separate (0 \n 2)
    punteggi = re.findall(r'\b([0-3])\b\s*[\n\r\-:]+\s*\b([0-3])\b', testo_incollato)
    match_tot = len(punteggi)
    if match_tot == 0:
        return 0, 0, 0, 0, 0

    set_vinti_tot = 0
    set_persi_tot = 0
    set_vinti_u5 = 0
    set_persi_u5 = 0

    for i, p in enumerate(punteggi):
        v = int(p[0]) 
        p_sub = int(p[1]) 
        set_vinti_tot += v
        set_persi_tot += p_sub
        if i < 5: 
            set_vinti_u5 += v
            set_persi_u5 += p_sub

    return set_vinti_tot, set_persi_tot, match_tot, set_vinti_u5, set_persi_u5

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
    st.sidebar.header("📥 INCOLLA I DATI (Diretta.it)")
    st.sidebar.info("Evidenzia la lista 'Ultimi Incontri' e incollala qui.")

    testo_t1 = st.sidebar.text_area(f"Copia-Incolla {t_h[:10]}", height=150)
    testo_t2 = st.sidebar.text_area(f"Copia-Incolla {t_o[:10]}", height=150)

    st.sidebar.markdown("---")
    st.sidebar.header("🌍 IMPOSTAZIONI MATCH")
    superficie = st.sidebar.selectbox("Superficie", ["Terra Rossa (Clay)", "Cemento (Hard)", "Erba (Grass)"])

    game_line_input = st.sidebar.number_input("Linea U/O Games (es. 21.5, 22.5)", min_value=18.5, max_value=26.5, value=21.5, step=1.0)

    v1_tot, p1_tot, mt1, v1_u5, p1_u5 = analizza_testo_tennis_set(testo_t1)
    v2_tot, p2_tot, mt2, v2_u5, p2_u5 = analizza_testo_tennis_set(testo_t2)

    if mt1 > 0 and mt2 > 0:
        # --- SIDEBAR DINAMICA ---
        ex_c = (w_avg(v1_tot, v1_u5, mt1) + w_avg(p2_tot, p2_u5, mt2)) / 2 
        ex_o = (w_avg(v2_tot, v2_u5, mt2) + w_avg(p1_tot, p1_u5, mt1)) / 2 
    else:
        ex_c = 0.001
        ex_o = 0.001

    max_g = 3

# --- QUOTE BASE COMUNI ---
st.sidebar.markdown("---")
q1_b = st.sidebar.number_input("Quota 1 Bookmaker", min_value=1.00, value=2.00, step=0.10)
if not is_tennis: 
    qx_b = st.sidebar.number_input("Quota X", min_value=1.00, value=3.20 if is_calcio else 4.50, step=0.10)
q2_b = st.sidebar.number_input("Quota 2 Bookmaker", min_value=1.00, value=3.50, step=0.10)

st.title(f"🔬 SPORTS LAB PRO - MODULE: {sport.replace('⚽ ','').replace('🏒 ','').replace('🎾 ','')}")
tab1, tab2, tab3 = st.tabs(["🎯 ENGINE MATRIX", "📊 VALUE RATING", "📂 DATABASE HUB"])

with tab1:

    # ==========================================
    # ⚽/🏒 ZONA CALCIO E HOCKEY 
    # ==========================================
    if not is_tennis:
        st.info(f"📊 Valori Attesi (xG): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")

        matrix = np.zeros((max_g, max_g))
        pc = [poisson(ex_c, i) for i in range(max_g)]
        po = [poisson(ex_o, i) for i in range(max_g)]

        for h in range(max_g):
            for a in range(max_g): 
                matrix[h, a] = pc[h] * po[a]

        scen_list = [
            f"{int(round(ex_c))}-{int(round(ex_o))}", 
            f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}", 
            f"{int(math.floor(ex_c))}-{int(math.ceil(ex_o))}"
        ]
        scen = list(dict.fromkeys(scen_list))

        c_c1, c_c2 = st.columns([2, 1.2])

        with c_c1:
            st.subheader("📊 Matrice Probabilità")
            cmap_color = 'Blues' if is_hockey else 'Greens'
            df_matrix = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)])
            st.dataframe(df_matrix.style.format("{:.1f}%").background_gradient(cmap=cmap_color, axis=None), height=300 if is_hockey else 230)

        with c_c2:
            st.subheader("🎯 Classifica Risultati")
            ris = []
            for h in range(max_g):
                for a in range(max_g):
                    p = matrix[h, a]
                    qf_val = 1/p if p > 0 else 0
                    ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": qf_val})

            df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
            st.dataframe(df_r.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in scen else ['']*3, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, height=300 if is_hockey else 230, use_container_width=True)

        st.subheader("💡 Scenari Esatti")
        cs = st.columns(4)
        for i, rn in enumerate(scen[:4]):
            try:
                h_idx = int(rn.split('-')[0])
                a_idx = int(rn.split('-')[1])
                pv = matrix[h_idx, a_idx] * 100
                qf_val = 100/pv if pv > 0 else 0
                with cs[i]:
                    st.metric("ESATTO", rn, delta=f"{pv:.1f}% (QF:{qf_val:.2f})")
                    if st.button(f"📌 Invia {rn}", key=f"s_{i}"): 
                        add_to_db(f"Esatto {rn}")
            except: 
                pass

        if is_calcio:
            st.subheader("🚀 Scenari Combo")
            def gp(cmin, cmax, omin, omax): 
                return sum(matrix[h, a] for h in range(cmin, cmax+1) for a in range(omin, omax+1) if h<max_g and a<max_g) * 100

            if ex_c < 1.2:
                rc = (0,1)
            elif ex_c < 2.2:
                rc = (1,3)
            else:
                rc = (2,4)

            if ex_o < 1.2:
                ro = (0,1)
            elif ex_o < 2.2:
                ro = (1,3)
            else:
                ro = (2,4)

            cb = st.columns(3)

            p_bi = gp(rc[0], rc[1], ro[0], ro[1])
            n_bi = f"T1 {rc[0]}-{rc[1]} + T2 {ro[0]}-{ro[1]}"
            with cb[0]:
                qf_bi = 100/p_bi if p_bi > 0 else 0
                st.metric("BILANCIATO", n_bi, delta=f"{p_bi:.1f}% (QF:{qf_bi:.2f})" if p_bi>0 else "0")

            if ex_c >= ex_o: 
                lab_d = "DOMINIO T1"
                n_d = f"T1 {rc[0]}-{rc[1]} + T2 0-1"
                p_d = gp(rc[0], rc[1], 0, 1)
            else: 
                lab_d = "DOMINIO T2"
                n_d = f"T1 0-1 + T2 {ro[0]}-{ro[1]}"
                p_d = gp(0, 1, ro[0], ro[1])

            with cb[1]:
                qf_d = 100/p_d if p_d > 0 else 0
                st.metric(lab_d, n_d, delta=f"{p_d:.1f}% (QF:{qf_d:.2f})" if p_d>0 else "0")

            p_go = gp(1, 3, 1, 3)
            with cb[2]:
                qf_go = 100/p_go if p_go > 0 else 0
                st.metric("COMBO GOAL", "T1 1-3 + T2 1-3", delta=f"{p_go:.1f}% (QF:{qf_go:.2f})" if p_go>0 else "0")

            st.subheader("📈 Mercati Principali")

            p1 = np.sum(np.tril(matrix, -1))*100
            px = np.trace(matrix)*100
            p2 = np.sum(np.triu(matrix, 1))*100

            def gmm(l, h): 
                return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100

            def over_prob(line): 
                return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if r+c > line) * 100

            mc = st.columns(6)
            mc[0].metric("1", f"{p1:.1f}%", f"QF:{100/p1:.2f}" if p1>0 else "0")
            mc[1].metric("X", f"{px:.1f}%", f"QF:{100/px:.2f}" if px>0 else "0")
            mc[2].metric("2", f"{p2:.1f}%", f"QF:{100/p2:.2f}" if p2>0 else "0")

            ov = over_prob(2.5)
            pg = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100

            mc[3].metric("O2.5", f"{ov:.1f}%", f"QF:{100/ov:.2f}" if ov>0 else "0")
            mc[4].metric("GOAL", f"{pg:.1f}%", f"QF:{100/pg:.2f}" if pg>0 else "0")
            mc[5].metric("NO G", f"{100-pg:.1f}%", f"QF:{100/(100-pg):.2f}" if (100-pg)>0 else "0")

            cmg = st.columns(4)
            mg_list = [(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]
            for i, mg in enumerate(mg_list):
                val_mg = gmm(mg[0], mg[1])
                qf_mg = 100/val_mg if val_mg > 0 else 0
                cmg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{val_mg:.1f}%", f"QF:{qf_mg:.2f}" if val_mg>0 else "0")

            st.markdown("---")
            cd1, cd2, cd3 = st.columns(3)
            with cd1:
                st.write(f"**🏠 MG T1**")
                for l, h in [(1,2), (1,3), (2,3)]:
                    pr = sum(pc[i] for i in range(l, h+1) if i < len(pc))*100
                    qf_pr = 100/pr if pr > 0 else 0
                    st.metric(f"T1 {l}-{h}", f"{pr:.1f}%", f"QF:{qf_pr:.2f}" if pr>0 else "0")
            with cd2:
                st.write(f"**🚀 MG T2**")
                for l, h in [(1,2), (1,3), (2,3)]:
                    pr = sum(po[i] for i in range(l, h+1) if i < len(po))*100
                    qf_pr = 100/pr if pr > 0 else 0
                    st.metric(f"T2 {l}-{h}", f"{pr:.1f}%", f"QF:{qf_pr:.2f}" if pr>0 else "0")
            with cd3:
                st.write("**⚖️ DOPPIA CHANCE**")
                dc_1x = p1 + px
                dc_x2 = p2 + px
                dc_12 = p1 + p2
                st.metric("1X", f"{dc_1x:.1f}%", f"QF:{100/dc_1x:.2f}" if dc_1x>0 else "0")
                st.metric("X2", f"{dc_x2:.1f}%", f"QF:{100/dc_x2:.2f}" if dc_x2>0 else "0")
                st.metric("12", f"{dc_12:.1f}%", f"QF:{100/dc_12:.2f}" if dc_12>0 else "0")

        elif is_hockey:
            p1 = np.sum(np.tril(matrix, -1))*100
            px = np.trace(matrix)*100
            p2 = np.sum(np.triu(matrix, 1))*100

            st.subheader("🎯 Margine Vittoria (Tempi Regolamentari)")
            t1_1g = sum(matrix[i, i-1] for i in range(1, max_g)) * 100
            t1_2g = sum(matrix[i, i-2] for i in range(2, max_g)) * 100
            t1_3pg = sum(matrix[i, j] for i in range(3, max_g) for j in range(max_g) if i - j >= 3) * 100

            t2_1g = sum(matrix[i-1, i] for i in range(1, max_g)) * 100
            t2_2g = sum(matrix[i-2, i] for i in range(2, max_g)) * 100
            t2_3pg = sum(matrix[i, j] for j in range(3, max_g) for i in range(max_g) if j - i >= 3) * 100

            rm1 = st.columns(4)
            rm1[0].metric(f"{t_h[:8].upper()} DI 1 GOAL", f"{t1_1g:.1f}%", f"QF:{100/t1_1g:.2f}" if t1_1g>0 else "0")
            rm1[1].metric(f"{t_h[:8].upper()} DI 2 GOAL", f"{t1_2g:.1f}%", f"QF:{100/t1_2g:.2f}" if t1_2g>0 else "0")
            rm1[2].metric(f"{t_h[:8].upper()} DI 3+ GOAL", f"{t1_3pg:.1f}%", f"QF:{100/t1_3pg:.2f}" if t1_3pg>0 else "0")
            rm1[3].metric("PAREGGIO (X)", f"{px:.1f}%", f"QF:{100/px:.2f}" if px>0 else "0")

            rm2 = st.columns(4)
            rm2[0].metric(f"{t_o[:8].upper()} DI 1 GOAL", f"{t2_1g:.1f}%", f"QF:{100/t2_1g:.2f}" if t2_1g>0 else "0")
            rm2[1].metric(f"{t_o[:8].upper()} DI 2 GOAL", f"{t2_2g:.1f}%", f"QF:{100/t2_2g:.2f}" if t2_2g>0 else "0")
            rm2[2].metric(f"{t_o[:8].upper()} DI 3+ GOAL", f"{t2_3pg:.1f}%", f"QF:{100/t2_3pg:.2f}" if t2_3pg>0 else "0")

            st.markdown("---")
            st.subheader("⚖️ Testa a Testa (Incl. OT) & Handicap (Puck Line)")
            tt_1 = p1 + (px / 2)
            tt_2 = p2 + (px / 2)
            hc_t1_minus15 = t1_2g + t1_3pg
            hc_t2_plus15 = p2 + px + t1_1g

            ctt = st.columns(4)
            ctt[0].metric(f"T/T 1 ({t_h[:8]})", f"{tt_1:.1f}%", f"QF:{100/tt_1:.2f}" if tt_1>0 else "0")
            ctt[1].metric(f"T/T 2 ({t_o[:8]})", f"{tt_2:.1f}%", f"QF:{100/tt_2:.2f}" if tt_2>0 else "0")
            ctt[2].metric(f"HANDICAP 1 (-1.5)", f"{hc_t1_minus15:.1f}%", f"QF:{100/hc_t1_minus15:.2f}" if hc_t1_minus15>0 else "0")
            ctt[3].metric(f"HANDICAP 2 (+1.5)", f"{hc_t2_plus15:.1f}%", f"QF:{100/hc_t2_plus15:.2f}" if hc_t2_plus15>0 else "0")

            st.markdown("---")
            st.subheader("🚀 Mercati Principali & Combo Hockey")
            def over_prob(line): 
                return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if r+c > line) * 100

            o45 = over_prob(4.5)
            o55 = over_prob(5.5)

            c1_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h > a and h+a > 4.5) * 100
            c1_u55 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h > a and h+a < 5.5) * 100
            c2_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if a > h and h+a > 4.5) * 100
            cx_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h == a and h+a > 4.5) * 100

            mch = st.columns(6)
            mch[0].metric("1 (Reg Time)", f"{p1:.1f}%", f"QF:{100/p1:.2f}" if p1>0 else "0")
            mch[1].metric("X (Reg Time)", f"{px:.1f}%", f"QF:{100/px:.2f}" if px>0 else "0")
            mch[2].metric("2 (Reg Time)", f"{p2:.1f}%", f"QF:{100/p2:.2f}" if p2>0 else "0")
            mch[3].metric("OVER 4.5", f"{o45:.1f}%", f"QF:{100/o45:.2f}" if o45>0 else "0")
            mch[4].metric("OVER 5.5", f"{o55:.1f}%", f"QF:{100/o55:.2f}" if o55>0 else "0")
            mch[5].metric("UNDER 5.5", f"{(100-o55):.1f}%", f"QF:{100/(100-o55):.2f}" if (100-o55)>0 else "0")

            c_combo = st.columns(4)
            c_combo[0].metric("1 + Over 4.5", f"{c1_o45:.1f}%", f"QF:{100/c1_o45:.2f}" if c1_o45>0 else "0")
            c_combo[1].metric("1 + Under 5.5", f"{c1_u55:.1f}%", f"QF:{100/c1_u55:.2f}" if c1_u55>0 else "0")
            c_combo[2].metric("2 + Over 4.5", f"{c2_o45:.1f}%", f"QF:{100/c2_o45:.2f}" if c2_o45>0 else "0")
            c_combo[3].metric("X + Over 4.5", f"{cx_o45:.1f}%", f"QF:{100/cx_o45:.2f}" if cx_o45>0 else "0")

    # ==========================================
    # 🎾 ZONA TENNIS (POISSON SUI SET CON PARSER)
    # ==========================================
    elif is_tennis:
        st.info("🧠 **ENGINE: POISSON SET MATRIX** | Il motore estrae in automatico i Set dai punteggi incollati.")

        if mt1 == 0 and mt2 == 0:
            st.warning("👈 Incolla i dati 'Ultimi Incontri' nella barra laterale per avviare l'algoritmo.")
            st.stop()

        st.write(f"📊 Dati Rilevati: **{t_h}** ({v1_tot} Set Vinti, {p1_tot} Persi su {mt1} Match) | **{t_o}** ({v2_tot} Set Vinti, {p2_tot} Persi su {mt2} Match)")

        raw_20 = poisson(ex_c, 2) * poisson(ex_o, 0)
        raw_21 = poisson(ex_c, 2) * poisson(ex_o, 1)
        raw_02 = poisson(ex_c, 0) * poisson(ex_o, 2)
        raw_12 = poisson(ex_c, 1) * poisson(ex_o, 2)

        tot_raw = raw_20 + raw_21 + raw_02 + raw_12
        if tot_raw == 0: tot_raw = 0.0001

        s_20 = (raw_20 / tot_raw) * 100
        s_21 = (raw_21 / tot_raw) * 100
        s_02 = (raw_02 / tot_raw) * 100
        s_12 = (raw_12 / tot_raw) * 100

        p1_vincente = s_20 + s_21
        p2_vincente = s_02 + s_12
        over_25_set = s_21 + s_12
        under_25_set = s_20 + s_02

        # --- RISULTATO ESATTO 1° SET E GAMES ---
        p_game_1 = 0.5 + ((p1_vincente/100) - 0.5) * 0.4
        p_game_2 = 1 - p_game_1
        equilibrio = 1 - abs(p_game_1 - p_game_2)

        set_60 = (p_game_1 ** 6) * 100
        set_61 = 6 * (p_game_1 ** 6) * p_game_2 * 100
        set_62 = 21 * (p_game_1 ** 6) * (p_game_2 ** 2) * 100
        set_63 = 56 * (p_game_1 ** 6) * (p_game_2 ** 3) * 100
        set_64 = 126 * (p_game_1 ** 6) * (p_game_2 ** 4) * 100
        set_75 = 252 * (p_game_1 ** 7) * (p_game_2 ** 5) * 100

        set_06 = (p_game_2 ** 6) * 100
        set_16 = 6 * (p_game_2 ** 6) * p_game_1 * 100
        set_26 = 21 * (p_game_2 ** 6) * (p_game_1 ** 2) * 100
        set_36 = 56 * (p_game_2 ** 6) * (p_game_1 ** 3) * 100
        set_46 = 126 * (p_game_2 ** 6) * (p_game_1 ** 4) * 100
        set_57 = 252 * (p_game_2 ** 7) * (p_game_1 ** 5) * 100

        base_tb = 0.15 
        if superficie == "Cemento (Hard)": 
            base_tb = 0.20
        elif superficie == "Erba (Grass)": 
            base_tb = 0.26

        prob_tb_totale = (base_tb * equilibrio * 1.5) * 100
        set_76 = prob_tb_totale * (p_game_1)
        set_67 = prob_tb_totale * (p_game_2)

        tot_1st_set = set_60 + set_61 + set_62 + set_63 + set_64 + set_75 + set_76 + set_06 + set_16 + set_26 + set_36 + set_46 + set_57 + set_67

        ris_1set = [
            ("6-0", t_h, (set_60/tot_1st_set)*100), 
            ("6-1", t_h, (set_61/tot_1st_set)*100),
            ("6-2", t_h, (set_62/tot_1st_set)*100), 
            ("6-3", t_h, (set_63/tot_1st_set)*100),
            ("6-4", t_h, (set_64/tot_1st_set)*100), 
            ("7-5", t_h, (set_75/tot_1st_set)*100),
            ("7-6", t_h, (set_76/tot_1st_set)*100), 
            ("0-6", t_o, (set_06/tot_1st_set)*100),
            ("1-6", t_o, (set_16/tot_1st_set)*100), 
            ("2-6", t_o, (set_26/tot_1st_set)*100),
            ("3-6", t_o, (set_36/tot_1st_set)*100), 
            ("4-6", t_o, (set_46/tot_1st_set)*100),
            ("5-7", t_o, (set_57/tot_1st_set)*100), 
            ("6-7", t_o, (set_67/tot_1st_set)*100)
        ]

        col_t1, col_t2 = st.columns([1.5, 2])

        with col_t1:
            st.subheader("🎯 Set Betting (Risultato Match)")
            df_sets = pd.DataFrame({
                "Risultato": ["2-0", "2-1", "0-2", "1-2"],
                "Vincitore": [t_h, t_h, t_o, t_o],
                "Probabilità": [f"{s_20:.1f}%", f"{s_21:.1f}%", f"{s_02:.1f}%", f"{s_12:.1f}%"],
                "Quota Fiera": [f"{100/s_20:.2f}" if s_20>0 else "0", f"{100/s_21:.2f}" if s_21>0 else "0", f"{100/s_02:.2f}" if s_02>0 else "0", f"{100/s_12:.2f}" if s_12>0 else "0"]
            }).sort_values(by="Probabilità", ascending=False)
            st.dataframe(df_sets.style.apply(lambda r: ['background-color: #ffeb3b; color: black; font-weight: bold']*4 if r.name == df_sets.index[0] else ['']*4, axis=1), hide_index=True, use_container_width=True)

            st.subheader("🎾 Risultato Esatto 1° Set")
            df_1set = pd.DataFrame(ris_1set, columns=["Risultato", "Vincitore", "Prob"]).sort_values(by="Prob", ascending=False).head(5)
            df_1set["Probabilità"] = df_1set["Prob"].apply(lambda x: f"{x:.1f}%")
            df_1set["Quota Fiera"] = df_1set["Prob"].apply(lambda x: f"{100/x:.2f}" if x>0 else "0")
            df_1set = df_1set.drop(columns=["Prob"])
            st.dataframe(df_1set, hide_index=True, use_container_width=True)

        with col_t2:
            st.subheader("🎾 Testa a Testa (Match)")
            tm1 = st.columns(2)
            tm1[0].metric(f"Vittoria {t_h[:8].upper()}", f"{p1_vincente:.1f}%", f"QF:{100/p1_vincente:.2f}" if p1_vincente>0 else "0")
            tm1[1].metric(f"Vittoria {t_o[:8].upper()}", f"{p2_vincente:.1f}%", f"QF:{100/p2_vincente:.2f}" if p2_vincente>0 else "0")

            prob_over = (40 + (equilibrio * 25) + (base_tb * 50))
            if game_line_input > 21.5: 
                prob_over -= (game_line_input - 21.5) * 5
            if game_line_input < 21.5: 
                prob_over += (21.5 - game_line_input) * 5

            if prob_over > 85: prob_over = 85
            if prob_over < 15: prob_over = 15
            prob_under = 100 - prob_over

            st.markdown("---")
            st.subheader("⏱️ Under/Over Games & Tie-Break")
            tm2 = st.columns(3)
            tm2[0].metric("TIE-BREAK NEL MATCH (Sì)", f"{prob_tb_totale:.1f}%", f"QF:{100/prob_tb_totale:.2f}" if prob_tb_totale>0 else "0")
            tm2[1].metric(f"OVER {game_line_input} Games", f"{prob_over:.1f}%", f"QF:{100/prob_over:.2f}" if prob_over>0 else "0")
            tm2[2].metric(f"UNDER {game_line_input} Games", f"{prob_under:.1f}%", f"QF:{100/prob_under:.2f}" if prob_under>0 else "0")

        st.markdown("---")
        st.subheader("⚖️ Set Totali & Handicap Set")
        tc1 = st.columns(4)
        tc1[0].metric("UNDER 2.5 SET (Finisce in 2 Set)", f"{under_25_set:.1f}%", f"QF:{100/under_25_set:.2f}" if under_25_set>0 else "0")
        tc1[1].metric("OVER 2.5 SET (Si va al 3° Set)", f"{over_25_set:.1f}%", f"QF:{100/over_25_set:.2f}" if over_25_set>0 else "0")
        
        # Handicap Set Dinamico (Intelligente)
        if p1_vincente >= p2_vincente:
            # T1 è favorito
            tc1[2].metric(f"HC {t_h[:8]} (-1.5)", f"{s_20:.1f}%", f"QF:{100/s_20:.2f}" if s_20>0 else "0")
            tc1[3].metric(f"HC {t_o[:8]} (+1.5)", f"{(s_02 + s_12 + s_21):.1f}%", f"QF:{100/(s_02 + s_12 + s_21):.2f}" if (s_02 + s_12 + s_21)>0 else "0")
        else:
            # T2 è favorito
            tc1[2].metric(f"HC {t_o[:8]} (-1.5)", f"{s_02:.1f}%", f"QF:{100/s_02:.2f}" if s_02>0 else "0")
            tc1[3].metric(f"HC {t_h[:8]} (+1.5)", f"{(s_20 + s_21 + s_12):.1f}%", f"QF:{100/(s_20 + s_21 + s_12):.2f}" if (s_20 + s_21 + s_12)>0 else "0")

# ==========================================
with tab2:
    if is_tennis:
        st.subheader("📊 Ricerca Value Bet Tennis (T/T)")
        b1 = p1_vincente
        b2 = p2_vincente
        bx = 0
        qf1 = 100/b1 if b1>0 else 0
        qf2 = 100/b2 if b2>0 else 0

        v1, v2 = st.columns(2)
        v1.metric("SEGNO 1", f"QF: {qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO")
        v2.metric("SEGNO 2", f"QF: {qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")
    else:
        st.subheader("📊 Ricerca Value Bet (Power Rating)")
        vH = ex_c * 10
        vA = ex_o * 10
        tot_v = vH + vA + (8 if is_hockey else 12) 

        b1 = (vH / tot_v) * 100
        b2 = (vA / tot_v) * 100
        bx = 100 - b1 - b2

        qf1 = 100/b1 if b1>0 else 0
        qfx = 100/bx if bx>0 else 0
        qf2 = 100/b2 if b2>0 else 0

        v1, vx, v2 = st.columns(3)
        v1.metric("SEGNO 1", f"QF: {qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO")
        vx.metric("SEGNO X", f"QF: {qfx:.2f}", "✅ VALUE" if qx_b > qfx else "❌ NO")
        v2.metric("SEGNO 2", f"QF: {qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")

        df_val = pd.DataFrame({"Segno":["1","X","2"],"Prob Algoritmo":[b1,bx,b2],"Q Book":[q1_b,qx_b,q2_b]})
        st.dataframe(df_val.style.highlight_max(subset=["Prob Algoritmo"], color="#dcfce7").format({"Prob Algoritmo":"{:.2f}%"}), use_container_width=True)

with tab3:
    st.subheader("📂 Tabella Database")
    st.markdown("<span style='color:gray; font-size:14px;'>Database unificato. I tasti WIN/LOSS salvano automaticamente.</span>", unsafe_allow_html=True)
    if st.session_state.db:
        for m, prs in list(st.session_state.db.items()):
            st.markdown("---") 
            if not prs:
                col_m, col_m_del, _ = st.columns([2, 1, 7])
                col_m.markdown(f"<div class='table-text'><b>{m}</b></div>", unsafe_allow_html=True)
                if col_m_del.button("🗑️ Rimuovi Partita", key=f"del_match_{m}"):
                    del st.session_state.db[m]
                    st.rerun()
            else:
                cols = st.columns([2] + [3] * len(prs))
                with cols[0]:
                    c_name, c_del = st.columns([3, 1])
                    c_name.markdown(f"<div class='table-text'><b>{m}</b></div>", unsafe_allow_html=True)
                    if c_del.button("🗑️", key=f"del_m_{m}"):
                        del st.session_state.db[m]
                        st.rerun()
                for idx, p in enumerate(prs):
                    with cols[idx + 1]:
                        cp_testo, cp_toggle, cp_cestino = st.columns([4, 3, 1.5])
                        cp_testo.markdown(f"<div class='table-text'>{p['scelta']}</div>", unsafe_allow_html=True)
                        esito = p['esito']
                        if esito == '⏳':
                            if cp_toggle.button("⚪ WAIT", key=f"tog_{m}_{idx}"): 
                                st.session_state.db[m][idx]['esito'] = 'WIN'
                                st.rerun()
                        elif esito == 'WIN':
                            if cp_toggle.button("🟢 WIN", key=f"tog_{m}_{idx}"): 
                                st.session_state.db[m][idx]['esito'] = 'LOSS'
                                st.rerun()
                        elif esito == 'LOSS':
                            if cp_toggle.button("🔴 LOSS", key=f"tog_{m}_{idx}"): 
                                st.session_state.db[m][idx]['esito'] = '⏳'
                                st.rerun()
                        if cp_cestino.button("🗑️", key=f"del_p_{m}_{idx}"):
                            st.session_state.db[m].pop(idx)
                            st.rerun()
    else:
        st.info("Database vuoto. Salva un incontro e invia dei pronostici per iniziare.")
