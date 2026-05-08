import streamlit as st
import math
import pandas as pd
import numpy as np

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

# --- SELETTORE SPORT (SIDEBAR) ---
st.sidebar.markdown("### 🔬 SELEZIONA SPORT")
sport = st.sidebar.radio("", ["⚽ CALCIO", "🏒 HOCKEY GHIACCIO"], horizontal=True)
is_hockey = sport == "🏒 HOCKEY GHIACCIO"

# --- REGISTRAZIONE INCONTRO ---
st.write(f"### 📝 REGISTRAZIONE INCONTRO ({sport})")
c_t1, c_t2, c_btn = st.columns([3, 3, 1.5])
t_h = c_t1.text_input("Squadra 1 (Casa/Preferita)", value="Kazakistan" if is_hockey else "Bologna")
t_o = c_t2.text_input("Squadra 2 (Ospite/Sfavorita)", value="Ucraina" if is_hockey else "Cagliari")

icona = "🏒" if is_hockey else "⚽"
match_name = f"{icona} {t_h} - {t_o}"

if c_btn.button("💾 SALVA INCONTRO", type="primary"):
    if match_name not in st.session_state.db:
        st.session_state.db[match_name] = []
        st.toast(f"Partita di {sport} creata!")

def add_to_db(pron):
    if match_name in st.session_state.db:
        st.session_state.db[match_name].append({'scelta': pron, 'esito': '⏳'})
        st.toast(f"Inviato: {pron}")
    else: 
        st.error("Clicca prima su SALVA INCONTRO per creare la riga!")

# --- SIDEBAR DINAMICA ---
st.sidebar.markdown("---")

if not is_hockey:
    # ⚽ INPUT CALCIO (INTATTO)
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
    
    def w_avg(sf, r5, gs): return ((sf / (gs if gs>0 else 1)) * 0.4) + ((r5 / 5) * 0.6)
    ex_c = (w_avg(c_f_s, c_f_5, c_g_s) + w_avg(o_s_s, o_s_5, o_g_s)) / 2
    ex_o = (w_avg(o_f_s, o_f_5, o_g_s) + w_avg(c_s_s, c_s_5, c_g_s)) / 2
    max_g = 6
else:
    # 🏒 INPUT HOCKEY
    st.sidebar.header(f"🔵 DATI {t_h[:10].upper()}")
    h_pg = st.sidebar.number_input("Partite Giocate (PG)", min_value=1, value=4)
    h_gf = st.sidebar.number_input("Reti Fatte (R - Prima)", min_value=0, value=18)
    h_gs = st.sidebar.number_input("Reti Subite (R - Dopo)", min_value=0, value=7)
    
    st.sidebar.markdown("---")
    st.sidebar.header(f"🔴 DATI {t_o[:10].upper()}")
    a_pg = st.sidebar.number_input("Partite Giocate (PG) ", min_value=1, value=4)
    a_gf = st.sidebar.number_input("Reti Fatte (R - Prima) ", min_value=0, value=11)
    a_gs = st.sidebar.number_input("Reti Subite (R - Dopo) ", min_value=0, value=11)
    
    avg_h_scored = h_gf / h_pg
    avg_h_conceded = h_gs / h_pg
    avg_a_scored = a_gf / a_pg
    avg_a_conceded = a_gs / a_pg
    
    ex_c = (avg_h_scored + avg_a_conceded) / 2
    ex_o = (avg_a_scored + avg_h_conceded) / 2
    max_g = 9

st.sidebar.markdown("---")
q1_b = st.sidebar.number_input("Quota 1", min_value=1.00, value=2.00, step=0.10)
qx_b = st.sidebar.number_input("Quota X", min_value=1.00, value=3.20 if not is_hockey else 4.50, step=0.10)
q2_b = st.sidebar.number_input("Quota 2", min_value=1.00, value=3.50, step=0.10)

# --- MATRICE E TABS ---
st.title(f"🔬 SPORTS LAB PRO - {'HOCKEY MODULE' if is_hockey else 'SOCCER MODULE'}")
tab1, tab2, tab3 = st.tabs(["🎯 SCORE MATRIX", "📊 POWER RATING", "📂 DATABASE HUB"])

with tab1:
    st.info(f"📊 Valori Attesi (xG): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
    matrix = np.zeros((max_g, max_g))
    pc = [poisson(ex_c, i) for i in range(max_g)]; po = [poisson(ex_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g): matrix[h, a] = pc[h] * po[a]
    scen = list(dict.fromkeys([f"{int(round(ex_c))}-{int(round(ex_o))}", f"{int(math.ceil(ex_c))}-{int(math.floor(ex_o))}", f"{int(math.floor(ex_c))}-{int(math.ceil(ex_o))}"]))

    c_c1, c_c2 = st.columns([2, 1.2])
    with c_c1:
        st.subheader("📊 Matrice Probabilità")
        cmap_color = 'Blues' if is_hockey else 'Greens'
        st.dataframe(pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)]).style.format("{:.1f}%").background_gradient(cmap=cmap_color, axis=None), height=300 if is_hockey else 230)
    with c_c2:
        st.subheader("🎯 Classifica Risultati")
        ris = []
        for h in range(max_g):
            for a in range(max_g):
                p = matrix[h, a]
                ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
        df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
        st.dataframe(df_r.style.apply(lambda r: ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in scen else ['']*3, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, height=300 if is_hockey else 230, use_container_width=True)

    st.subheader("💡 Scenari Esatti")
    cs = st.columns(4)
    for i, rn in enumerate(scen[:4]):
        try:
            pv = matrix[int(rn.split('-')[0]), int(rn.split('-')[1])] * 100
            with cs[i]:
                st.metric("ESATTO", rn, delta=f"{pv:.1f}% (QF:{100/pv:.2f})")
                if st.button(f"📌 Invia {rn}", key=f"s_{i}"): add_to_db(f"Esatto {rn}")
        except: pass

    # --- ZONA DIVISA: CALCIO vs HOCKEY ---
    if not is_hockey:
        # ==========================================
        # ⚽ ZONA CALCIO (INTATTA AL 100%)
        # ==========================================
        st.subheader("🚀 Scenari Combo")
        def gp(cmin, cmax, omin, omax): return sum(matrix[h, a] for h in range(cmin, cmax+1) for a in range(omin, omax+1) if h<max_g and a<max_g) * 100
        rc = (0,1) if ex_c < 1.2 else (1,3) if ex_c < 2.2 else (2,4)
        ro = (0,1) if ex_o < 1.2 else (1,3) if ex_o < 2.2 else (2,4)
        cb = st.columns(3)
        p_bi, n_bi = gp(rc[0], rc[1], ro[0], ro[1]), f"T1 {rc[0]}-{rc[1]} + T2 {ro[0]}-{ro[1]}"
        with cb[0]:
            st.metric("BILANCIATO", n_bi, delta=f"{p_bi:.1f}% (QF:{100/p_bi:.2f})" if p_bi>0 else "0")
            if st.button("📌 Invia Bil"): add_to_db(f"Bil: {n_bi}")
        if ex_c >= ex_o: lab_d, n_d, p_d = "DOMINIO T1", f"T1 {rc[0]}-{rc[1]} + T2 0-1", gp(rc[0], rc[1], 0, 1)
        else: lab_d, n_d, p_d = "DOMINIO T2", f"T1 0-1 + T2 {ro[0]}-{ro[1]}", gp(0, 1, ro[0], ro[1])
        with cb[1]:
            st.metric(lab_d, n_d, delta=f"{p_d:.1f}% (QF:{100/p_d:.2f})" if p_d>0 else "0")
            if st.button(f"📌 Invia Dom"): add_to_db(f"Dom: {n_d}")
        p_go = gp(1, 3, 1, 3)
        with cb[2]:
            st.metric("COMBO GOAL", "T1 1-3 + T2 1-3", delta=f"{p_go:.1f}% (QF:{100/p_go:.2f})" if p_go>0 else "0")
            if st.button("📌 Invia Combo Goal"): add_to_db(f"Combo Goal: T1 1-3 + T2 1-3")

        st.subheader("📈 Mercati Principali")
        p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
        def gmm(l, h): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if l <= r+c <= h) * 100
        def over_prob(line): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if r+c > line) * 100
        
        mc = st.columns(6)
        mc[0].metric("1", f"{p1:.1f}%", f"QF:{100/p1:.2f}"); mc[1].metric("X", f"{px:.1f}%", f"QF:{100/px:.2f}"); mc[2].metric("2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
        ov, pg = over_prob(2.5), sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
        mc[3].metric("O2.5", f"{ov:.1f}%", f"QF:{100/ov:.2f}"); mc[4].metric("GOAL", f"{pg:.1f}%", f"QF:{100/pg:.2f}"); mc[5].metric("NO G", f"{100-pg:.1f}%", f"QF:{100/(100-pg):.2f}")
        
        cmg = st.columns(4)
        for i, mg in enumerate([(1,2), (1,3), (1,4), (2,3), (2,4), (2,5), (3,4), (3,5)]):
            val_mg = gmm(mg[0], mg[1])
            cmg[i % 4].metric(f"MG {mg[0]}-{mg[1]}", f"{val_mg:.1f}%", f"QF:{100/val_mg:.2f}" if val_mg>0 else "0")

        st.markdown("---")
        cd1, cd2, cd3 = st.columns(3)
        with cd1:
            st.write(f"**🏠 MG {t_h[:8].upper()}**")
            for l, h in [(1,2), (1,3), (2,3)]:
                pr = sum(pc[i] for i in range(l, h+1) if i < len(pc))*100
                st.metric(f"T1 {l}-{h}", f"{pr:.1f}%", f"QF:{100/pr*100:.2f}" if pr>0 else "0")
        with cd2:
            st.write(f"**🚀 MG {t_o[:8].upper()}**")
            for l, h in [(1,2), (1,3), (2,3)]:
                pr = sum(po[i] for i in range(l, h+1) if i < len(po))*100
                st.metric(f"T2 {l}-{h}", f"{pr:.1f}%", f"QF:{100/pr*100:.2f}" if pr>0 else "0")
        with cd3:
            st.write("**⚖️ DOPPIA CHANCE**")
            st.metric("1X", f"{(p1+px):.1f}%", f"QF:{100/(p1+px):.2f}"); st.metric("X2", f"{(p2+px):.1f}%", f"QF:{100/(p2+px):.2f}"); st.metric("12", f"{(p1+p2):.1f}%", f"QF:{100/(p1+p2):.2f}")

    else:
        # ==========================================
        # 🏒 ZONA HOCKEY (NUOVA - MARGINE, T/T, COMBO)
        # ==========================================
        p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
        
        st.subheader("🎯 Margine Vittoria (Tempi Regolamentari)")
        # Calcolo Matematico dei Margini (Somma delle diagonali)
        t1_1g = sum(matrix[i, i-1] for i in range(1, max_g)) * 100
        t1_2g = sum(matrix[i, i-2] for i in range(2, max_g)) * 100
        t1_3pg = sum(matrix[i, j] for i in range(3, max_g) for j in range(max_g) if i - j >= 3) * 100
        
        t2_1g = sum(matrix[i-1, i] for i in range(1, max_g)) * 100
        t2_2g = sum(matrix[i-2, i] for i in range(2, max_g)) * 100
        t2_3pg = sum(matrix[i, j] for j in range(3, max_g) for i in range(max_g) if j - i >= 3) * 100

        # RIGA 1: Team 1 e Pareggio
        rm1 = st.columns(4)
        rm1[0].metric(f"{t_h[:8].upper()} DI 1 GOAL", f"{t1_1g:.1f}%", f"QF:{100/t1_1g:.2f}" if t1_1g>0 else "0")
        rm1[1].metric(f"{t_h[:8].upper()} DI 2 GOAL", f"{t1_2g:.1f}%", f"QF:{100/t1_2g:.2f}" if t1_2g>0 else "0")
        rm1[2].metric(f"{t_h[:8].upper()} DI 3+ GOAL", f"{t1_3pg:.1f}%", f"QF:{100/t1_3pg:.2f}" if t1_3pg>0 else "0")
        rm1[3].metric("PAREGGIO (X)", f"{px:.1f}%", f"QF:{100/px:.2f}" if px>0 else "0")
        
        # RIGA 2: Team 2
        rm2 = st.columns(4)
        rm2[0].metric(f"{t_o[:8].upper()} DI 1 GOAL", f"{t2_1g:.1f}%", f"QF:{100/t2_1g:.2f}" if t2_1g>0 else "0")
        rm2[1].metric(f"{t_o[:8].upper()} DI 2 GOAL", f"{t2_2g:.1f}%", f"QF:{100/t2_2g:.2f}" if t2_2g>0 else "0")
        rm2[2].metric(f"{t_o[:8].upper()} DI 3+ GOAL", f"{t2_3pg:.1f}%", f"QF:{100/t2_3pg:.2f}" if t2_3pg>0 else "0")

        st.markdown("---")
        
        st.subheader("⚖️ Testa a Testa (Incl. OT) & Handicap (Puck Line)")
        # Calcolo T/T (Spalmo il pareggio 50/50)
        tt_1 = p1 + (px / 2)
        tt_2 = p2 + (px / 2)
        # Calcolo Handicap -1.5 / +1.5
        hc_t1_minus15 = t1_2g + t1_3pg
        hc_t2_plus15 = p2 + px + t1_1g
        
        ctt = st.columns(4)
        ctt[0].metric(f"T/T 1 ({t_h[:8]})", f"{tt_1:.1f}%", f"QF:{100/tt_1:.2f}" if tt_1>0 else "0")
        ctt[1].metric(f"T/T 2 ({t_o[:8]})", f"{tt_2:.1f}%", f"QF:{100/tt_2:.2f}" if tt_2>0 else "0")
        ctt[2].metric(f"HANDICAP 1 (-1.5)", f"{hc_t1_minus15:.1f}%", f"QF:{100/hc_t1_minus15:.2f}" if hc_t1_minus15>0 else "0")
        ctt[3].metric(f"HANDICAP 2 (+1.5)", f"{hc_t2_plus15:.1f}%", f"QF:{100/hc_t2_plus15:.2f}" if hc_t2_plus15>0 else "0")

        st.markdown("---")
        
        st.subheader("🚀 Mercati Principali & Combo Hockey")
        def over_prob(line): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if r+c > line) * 100
        o45, o55, o65 = over_prob(4.5), over_prob(5.5), over_prob(6.5)
        
        # Calcolo Combo Base
        c1_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h > a and h+a > 4.5) * 100
        c1_u55 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h > a and h+a < 5.5) * 100
        c2_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if a > h and h+a > 4.5) * 100
        cx_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h == a and h+a > 4.5) * 100

        mch = st.columns(6)
        mch[0].metric("1 (Reg Time)", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
        mch[1].metric("X (Reg Time)", f"{px:.1f}%", f"QF:{100/px:.2f}")
        mch[2].metric("2 (Reg Time)", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
        mch[3].metric("OVER 4.5", f"{o45:.1f}%", f"QF:{100/o45:.2f}" if o45>0 else "0")
        mch[4].metric("OVER 5.5", f"{o55:.1f}%", f"QF:{100/o55:.2f}" if o55>0 else "0")
        mch[5].metric("UNDER 5.5", f"{(100-o55):.1f}%", f"QF:{100/(100-o55):.2f}" if (100-o55)>0 else "0")
        
        c_combo = st.columns(4)
        c_combo[0].metric("1 + Over 4.5", f"{c1_o45:.1f}%", f"QF:{100/c1_o45:.2f}" if c1_o45>0 else "0")
        c_combo[1].metric("1 + Under 5.5", f"{c1_u55:.1f}%", f"QF:{100/c1_u55:.2f}" if c1_u55>0 else "0")
        c_combo[2].metric("2 + Over 4.5", f"{c2_o45:.1f}%", f"QF:{100/c2_o45:.2f}" if c2_o45>0 else "0")
        c_combo[3].metric("X + Over 4.5", f"{cx_o45:.1f}%", f"QF:{100/cx_o45:.2f}" if cx_o45>0 else "0")

with tab2:
    st.subheader("📊 Ricerca Value Bet (Power Rating)")
    # Calcolo BVS
    vH = ex_c * 10; vA = ex_o * 10
    tot_v = vH + vA + (8 if is_hockey else 12) # Peso del pareggio
    b1 = (vH / tot_v) * 100; b2 = (vA / tot_v) * 100; bx = 100 - b1 - b2
    qf1, qfx, qf2 = 100/b1, 100/bx, 100/b2
    v1, vx, v2 = st.columns(3)
    v1.metric("SEGNO 1", f"QF: {qf1:.2f}", "✅ VALUE" if q1_b > qf1 else "❌ NO")
    vx.metric("SEGNO X", f"QF: {qfx:.2f}", "✅ VALUE" if qx_b > qfx else "❌ NO")
    v2.metric("SEGNO 2", f"QF: {qf2:.2f}", "✅ VALUE" if q2_b > qf2 else "❌ NO")
    st.dataframe(pd.DataFrame({"Segno":["1","X","2"],"Prob Algoritmo":[b1,bx,b2],"Q Book":[q1_b,qx_b,q2_b]}).style.highlight_max(subset=["Prob Algoritmo"], color="#dcfce7").format({"Prob Algoritmo":"{:.2f}%"}), use_container_width=True)

with tab3:
    st.subheader("📂 Tabella Database")
    st.markdown("<span style='color:gray; font-size:14px;'>Ogni partita e i suoi pronostici sono disposti in riga orizzontale. Usa i tasti WAIT, WIN o LOSS per gestirli.</span>", unsafe_allow_html=True)
    
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
                            if cp_toggle.button("⚪ WAIT", key=f"tog_{m}_{idx}"): st.session_state.db[m][idx]['esito'] = 'WIN'; st.rerun()
                        elif esito == 'WIN':
                            if cp_toggle.button("🟢 WIN", key=f"tog_{m}_{idx}"): st.session_state.db[m][idx]['esito'] = 'LOSS'; st.rerun()
                        elif esito == 'LOSS':
                            if cp_toggle.button("🔴 LOSS", key=f"tog_{m}_{idx}"): st.session_state.db[m][idx]['esito'] = '⏳'; st.rerun()
                        if cp_cestino.button("🗑️", key=f"del_p_{m}_{idx}"):
                            st.session_state.db[m].pop(idx); st.rerun()
    else:
        st.info("Database vuoto. Salva un incontro e invia dei pronostici per iniziare.")
