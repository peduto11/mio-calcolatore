import streamlit as st
import math
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="FT SCORE & DATABASE PRO", page_icon="⚽", layout="wide")

# --- INIZIALIZZAZIONE DATABASE IN MEMORIA ---
if 'db_partite' not in st.session_state:
    st.session_state.db_partite = pd.DataFrame(columns=['Incontro', 'Data', 'Dati_Input', 'Esito'])

# --- CSS PER LOOK PROFESSIONALE ---
st.markdown("""
    <style>
    .element-container h1 a, .element-container h2 a, .element-container h3 a { display: none; }
    h1, h2, h3 { margin-top: -20px; padding-bottom: 10px; }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 5px 10px !important;
        border-radius: 8px !important;
    }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

def poisson(lmbda, x):
    if lmbda <= 0: return 1 if x == 0 else 0
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

# --- SIDEBAR SUPERIORE A SCOMPARSA ---
with st.expander("📝 REGISTRAZIONE INCONTRO (Clicca per espandere)", expanded=False):
    col_name1, col_name2, col_save = st.columns([3, 3, 1])
    team_home = col_name1.text_input("Squadra Casa", placeholder="es. Udinese")
    team_away = col_name2.text_input("Squadra Ospite", placeholder="es. Torino")
    
# --- SIDEBAR LATERALE (DATI) ---
st.sidebar.header("🏠 DATI CASA")
c_f_s = st.sidebar.number_input("Gol Fatti Casa (Stagione)", value=15, key='cfs')
c_s_s = st.sidebar.number_input("Gol Subiti Casa (Stagione)", value=10, key='css')
c_g_s = st.sidebar.number_input("Partite Casa (Stagione)", value=8, key='cgs')
c_f_5 = st.sidebar.number_input("Gol Fatti (U5 Casa)", value=8, key='cf5')
c_s_5 = st.sidebar.number_input("Gol Subiti (U5 Casa)", value=4, key='cs5')

st.sidebar.markdown("---")
st.sidebar.header("🚀 DATI OSPITE")
o_f_s = st.sidebar.number_input("Gol Fatti Ospite (Stagione)", value=10, key='ofs')
o_s_s = st.sidebar.number_input("Gol Subiti Ospite (Stagione)", value=18, key='oss')
o_g_s = st.sidebar.number_input("Partite Ospite (Stagione)", value=8, key='ogs')
o_f_5 = st.sidebar.number_input("Gol Fatti (U5 Ospite)", value=3, key='of5')
o_s_5 = st.sidebar.number_input("Gol Subiti (U5 Ospite)", value=9, key='os5')

st.sidebar.markdown("---")
st.sidebar.header("💰 QUOTE BOOKMAKER")
q1_b = st.sidebar.number_input("Quota 1", value=2.00, key='q1')
qx_b = st.sidebar.number_input("Quota X", value=3.20, key='qx')
q2_b = st.sidebar.number_input("Quota 2", value=3.50, key='q2')

# --- LOGICA SALVATAGGIO ---
if col_save.button("💾 SALVA"):
    if team_home and team_away:
        nuova_partita = {
            'Incontro': f"{team_home} vs {team_away}",
            'Data': pd.Timestamp.now().strftime("%d/%m %H:%M"),
            'Dati_Input': {
                'cfs': c_f_s, 'css': c_s_s, 'cgs': c_g_s, 'cf5': c_f_5, 'cs5': c_s_5,
                'ofs': o_f_s, 'oss': o_s_s, 'ogs': o_g_s, 'of5': o_f_5, 'os5': o_s_5,
                'q1': q1_b, 'qx': qx_b, 'q2': q2_b
            },
            'Esito': '⏳ In corso'
        }
        st.session_state.db_partite = pd.concat([st.session_state.db_partite, pd.DataFrame([nuova_partita])], ignore_index=True)
        st.success(f"Gara {team_home}-{team_away} salvata!")
    else:
        st.error("Inserisci i nomi delle squadre!")

# --- CALCOLO MEDIE ---
def weighted(s_f, r_5, g_s):
    return ((s_f / (g_s if g_s>0 else 1)) * 0.4) + ((r_5 / 5) * 0.6)

exp_c = (weighted(c_f_s, c_f_5, c_g_s) + weighted(o_s_s, o_s_5, o_g_s)) / 2
exp_o = (weighted(o_f_s, o_f_5, o_g_s) + weighted(c_s_s, c_s_5, c_g_s)) / 2

st.title("⚽ FT SCORE DETECTOR & DATABASE PRO")

tab1, tab2, tab3 = st.tabs(["🎯 FT SCORE & MULTIGOL", "📊 POWER RATING SYSTEM", "📂 ARCHIVIO DATABASE"])

with tab1:
    st.info(f"📊 **Baricentro Match:** Casa **{exp_c:.2f}** | Ospite **{exp_o:.2f}**")
    max_g = 6 
    matrix = np.zeros((max_g, max_g))
    prob_c_l = [poisson(exp_c, i) for i in range(max_g)]
    prob_o_l = [poisson(exp_o, i) for i in range(max_g)]
    for h in range(max_g):
        for a in range(max_g):
            matrix[h, a] = prob_c_l[h] * prob_o_l[a]

    s1, s2, s3 = f"{int(round(exp_c))}-{int(round(exp_o))}", f"{int(math.ceil(exp_c))}-{int(math.floor(exp_o))}", f"{int(math.floor(exp_c))}-{int(math.ceil(exp_o))}"
    top_scen = list(dict.fromkeys([s1, s2, s3]))

    col_m1, col_m2 = st.columns([2, 1.2])
    with col_m1:
        st.subheader("📊 Matrice Probabilità")
        df_m = pd.DataFrame(matrix * 100, index=[f"C{i}" for i in range(max_g)], columns=[f"O{i}" for i in range(max_g)])
        st.dataframe(df_m.style.format("{:.1f}%").background_gradient(cmap='Greens', axis=None), height=245)
    with col_m2:
        st.subheader("🎯 Classifica Esatti")
        ris = []
        for h in range(max_g):
            for a in range(max_g):
                p = matrix[h, a]
                ris.append({"Risultato": f"{h}-{a}", "Prob": p * 100, "QF": 1/p if p > 0 else 0})
        df_r = pd.DataFrame(ris).sort_values(by="Prob", ascending=False).head(10)
        def hl(r): return ['background-color: #ffff00; color: black; font-weight: bold']*3 if r['Risultato'] in top_scen else ['']*3
        st.dataframe(df_r[["Risultato", "Prob", "QF"]].style.apply(hl, axis=1).format({"Prob": "{:.1f}%", "QF": "{:.2f}"}), hide_index=True, height=245, use_container_width=True)

    st.subheader("💡 Scenari Suggeriti")
    c_sce = st.columns(4)
    for i, res_n in enumerate(top_scen):
        h_s, a_s = map(int, res_n.split('-'))
        p_s = matrix[h_s, a_s] * 100
        c_sce[i].metric(f"ESATTO: {res_n}", f"{p_s:.1f}%", f"QF: {100/p_s:.2f}")

    # Combo Dinamiche
    st.subheader("🚀 Scenari Combo Multigol")
    def get_range(mu):
        if mu < 1.2: return (0, 1)
        if mu < 2.2: return (1, 3)
        return (2, 4)
    r_c, r_o = get_range(exp_c), get_range(exp_o)
    def get_combo_p(c_r, o_r): return sum(matrix[h, a] for h in range(c_r[0], c_r[1]+1) for a in range(o_r[0], o_r[1]+1) if h < max_g and a < max_g) * 100
    p_bil = get_combo_p(r_c, r_o)
    if exp_c >= exp_o:
        label_dom, name_dom, p_dom = "DOMINIO CASA", f"CASA {r_c[0]}-{r_c[1]} + OSPITE 0-1", get_combo_p(r_c, (0, 1))
    else:
        label_dom, name_dom, p_dom = "DOMINIO OSPITE", f"CASA 0-1 + OSPITE {r_o[0]}-{r_o[1]}", get_combo_p((0, 1), r_o)
    p_goal_over = get_combo_p((1, 3), (1, 3))
    cc = st.columns(3)
    cc[0].metric("BILANCIATO", f"CASA {r_c[0]}-{r_c[1]} + OSPITE {r_o[0]}-{r_o[1]}", f"{p_bil:.1f}% (QF: {100/p_bil:.2f})")
    cc[1].metric(label_dom, name_dom, f"{p_dom:.1f}% (QF: {100/p_dom:.2f})")
    cc[2].metric("COMBO GOAL", "CASA 1-3 + OSPITE 1-3", f"{p_goal_over:.1f}% (QF: {100/p_goal_over:.2f})")

    # Mercati Principali
    st.subheader("📈 Mercati Principali")
    p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
    ov25 = (1 - (matrix[0,0]+matrix[1,0]+matrix[0,1]+matrix[2,0]+matrix[0,2]+matrix[1,1]))*100
    pg = sum(matrix[h, a] for h in range(1, max_g) for a in range(1, max_g)) * 100
    mc = st.columns(6)
    mc[0].metric("Segno 1", f"{p1:.1f}%", f"QF:{100/p1:.2f}")
    mc[1].metric("Segno X", f"{px:.1f}%", f"QF:{100/px:.2f}")
    mc[2].metric("Segno 2", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
    mc[3].metric("Over 2.5", f"{ov25:.1f}%", f"QF:{100/ov25:.2f}")
    mc[4].metric("GOAL", f"{pg:.1f}%", f"QF:{100/pg:.2f}")
    mc[5].metric("NO GOAL", f"{100-pg:.1f}%", f"QF:{100/(100-pg):.2f}")

    # Multigol e Doppia Chance
    st.markdown("---")
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        st.write("**🏠 MG CASA**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_c_l[i] for i in range(l, h+1)) * 100
            st.metric(f"Casa {l}-{h}", f"{p:.1f}%", f"QF: {100/p:.2f}")
    with cd2:
        st.write("**🚀 MG OSPITE**")
        for l, h in [(1,2), (1,3), (2,3)]:
            p = sum(prob_o_l[i] for i in range(l, h+1)) * 100
            st.metric(f"Ospite {l}-{h}", f"{p:.1f}%", f"QF: {100/p:.2f}")
    with cd3:
        st.write("**⚖️ DOPPIA CHANCE**")
        st.metric("1X", f"{(p1+px):.1f}%", f"QF:{100/(p1+px):.2f}")
        st.metric("X2", f"{(p2+px):.1f}%", f"QF:{100/(p2+px):.2f}")
        st.metric("12", f"{(p1+p2):.1f}%", f"QF:{100/(p1+p2):.2f}")

with tab2:
    st.subheader("📊 Analisi Power Rating System")
    m_gf_c, m_gs_c = c_f_s/c_g_s if c_g_s>0 else 0, c_s_s/c_g_s if c_g_s>0 else 0
    m_gf_o, m_gs_o = o_f_s/o_g_s if o_g_s>0 else 0, o_s_s/o_g_s if o_g_s>0 else 0
    t1 = ((m_gf_c + m_gs_o) / 2) * 25
    t2 = ((m_gf_o + m_gs_c) / 2) * 25
    tx = 107.05 - t1 - t2
    b1, bx, b2 = t1*(106/107.05), tx*(106/107.05), t2*(106/107.05)
    qf1, qfx, qf2 = 100/b1, 100/bx, 100/b2
    bv1, bvx, bv2 = st.columns(3)
    bv1.metric("SEGNO 1", f"QF: {qf1:.2f}", "VALORE ✅" if q1_book > qf1 else "NO VALUE ❌")
    bvx.metric("SEGNO X", f"QF: {qfx:.2f}", "VALORE ✅" if qx_book > qfx else "NO VALUE ❌")
    bv2.metric("SEGNO 2", f"QF: {qf2:.2f}", "VALORE ✅" if q2_book > qf2 else "NO VALUE ❌")
    st.markdown("---")
    bvs_df = pd.DataFrame({"Segno": ["1", "X", "2"], "Prob. Teorica": [t1, tx, t2], "Prob. BVS": [b1, bx, b2], "Quota Book": [q1_book, qx_book, q2_book]})
    st.dataframe(bvs_df.style.highlight_max(subset=["Prob. BVS"], color="#dcfce7").format({"Prob. Teorica": "{:.2f}%", "Prob. BVS": "{:.2f}%", "Quota Book": "{:.2f}"}), hide_index=True, use_container_width=True)

with tab3:
    st.subheader("📂 Database Incontri Analizzati")
    if not st.session_state.db_partite.empty:
        for idx, row in st.session_state.db_partite.iterrows():
            with st.container():
                c_data, c_match, c_win, c_loss, c_del = st.columns([1.5, 4, 1, 1, 0.5])
                c_data.write(row['Data'])
                if c_match.button(row['Incontro'], key=f"rec_{idx}"):
                    # RICHIAMO DATI NELLA SIDEBAR
                    d = row['Dati_Input']
                    st.info(f"Dati di {row['Incontro']} ricaricati! Controlla la sidebar.")
                
                if c_win.button("WIN ✅", key=f"win_{idx}"): st.session_state.db_partite.at[idx, 'Esito'] = 'VINTO 💰'
                if c_loss.button("LOSS ❌", key=f"loss_{idx}"): st.session_state.db_partite.at[idx, 'Esito'] = 'PERSO 📉'
                if c_del.button("🗑️", key=f"del_{idx}"):
                    st.session_state.db_partite = st.session_state.db_partite.drop(idx).reset_index(drop=True)
                    st.rerun()
                
                st.write(f"Stato attuale: **{row['Esito']}**")
                st.markdown("---")
        
        st.download_button("📥 SCARICA BACKUP DATABASE", st.session_state.db_partite.to_csv(index=False), "archivio_partite.csv", "text/csv")
    else:
        st.write("Nessun incontro salvato nel database.")
