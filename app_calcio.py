# ==========================================
# ⚽/🏒 ZONA CALCIO E HOCKEY 
# ==========================================
if not is_tennis:
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

    if is_calcio:
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
            st.write(f"**🏠 MG T1**")
            for l, h in [(1,2), (1,3), (2,3)]:
                pr = sum(pc[i] for i in range(l, h+1) if i < len(pc))*100
                st.metric(f"T1 {l}-{h}", f"{pr:.1f}%", f"QF:{100/pr*100:.2f}" if pr>0 else "0")
        with cd2:
            st.write(f"**🚀 MG T2**")
            for l, h in [(1,2), (1,3), (2,3)]:
                pr = sum(po[i] for i in range(l, h+1) if i < len(po))*100
                st.metric(f"T2 {l}-{h}", f"{pr:.1f}%", f"QF:{100/pr*100:.2f}" if pr>0 else "0")
        with cd3:
            st.write("**⚖️ DOPPIA CHANCE**")
            st.metric("1X", f"{(p1+px):.1f}%", f"QF:{100/(p1+px):.2f}"); st.metric("X2", f"{(p2+px):.1f}%", f"QF:{100/(p2+px):.2f}"); st.metric("12", f"{(p1+p2):.1f}%", f"QF:{100/(p1+p2):.2f}")

    elif is_hockey:
        p1, px, p2 = np.sum(np.tril(matrix, -1))*100, np.trace(matrix)*100, np.sum(np.triu(matrix, 1))*100
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
        tt_1 = p1 + (px / 2); tt_2 = p2 + (px / 2)
        hc_t1_minus15 = t1_2g + t1_3pg; hc_t2_plus15 = p2 + px + t1_1g
        
        ctt = st.columns(4)
        ctt[0].metric(f"T/T 1 ({t_h[:8]})", f"{tt_1:.1f}%", f"QF:{100/tt_1:.2f}" if tt_1>0 else "0")
        ctt[1].metric(f"T/T 2 ({t_o[:8]})", f"{tt_2:.1f}%", f"QF:{100/tt_2:.2f}" if tt_2>0 else "0")
        ctt[2].metric(f"HANDICAP 1 (-1.5)", f"{hc_t1_minus15:.1f}%", f"QF:{100/hc_t1_minus15:.2f}" if hc_t1_minus15>0 else "0")
        ctt[3].metric(f"HANDICAP 2 (+1.5)", f"{hc_t2_plus15:.1f}%", f"QF:{100/hc_t2_plus15:.2f}" if hc_t2_plus15>0 else "0")

        st.markdown("---")
        st.subheader("🚀 Mercati Principali & Combo Hockey")
        def over_prob(line): return sum(matrix[r, c] for r in range(max_g) for c in range(max_g) if r+c > line) * 100
        o45, o55 = over_prob(4.5), over_prob(5.5)
        
        c1_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h > a and h+a > 4.5) * 100
        c1_u55 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h > a and h+a < 5.5) * 100
        c2_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if a > h and h+a > 4.5) * 100
        cx_o45 = sum(matrix[h, a] for h in range(max_g) for a in range(max_g) if h == a and h+a > 4.5) * 100

        mch = st.columns(6)
        mch[0].metric("1 (Reg Time)", f"{p1:.1f}%", f"QF:{100/p1:.2f}"); mch[1].metric("X (Reg Time)", f"{px:.1f}%", f"QF:{100/px:.2f}"); mch[2].metric("2 (Reg Time)", f"{p2:.1f}%", f"QF:{100/p2:.2f}")
        mch[3].metric("OVER 4.5", f"{o45:.1f}%", f"QF:{100/o45:.2f}" if o45>0 else "0"); mch[4].metric("OVER 5.5", f"{o55:.1f}%", f"QF:{100/o55:.2f}" if o55>0 else "0"); mch[5].metric("UNDER 5.5", f"{(100-o55):.1f}%", f"QF:{100/(100-o55):.2f}" if (100-o55)>0 else "0")
        
        c_combo = st.columns(4)
        c_combo[0].metric("1 + Over 4.5", f"{c1_o45:.1f}%", f"QF:{100/c1_o45:.2f}" if c1_o45>0 else "0")
        c_combo[1].metric("1 + Under 5.5", f"{c1_u55:.1f}%", f"QF:{100/c1_u55:.2f}" if c1_u55>0 else "0")
        c_combo[2].metric("2 + Over 4.5", f"{c2_o45:.1f}%", f"QF:{100/c2_o45:.2f}" if c2_o45>0 else "0")
        c_combo[3].metric("X + Over 4.5", f"{cx_o45:.1f}%", f"QF:{100/cx_o45:.2f}" if cx_o45>0 else "0")

# ==========================================
# 🎾 ZONA TENNIS (MOTORE SET POISSON)
# ==========================================
elif is_tennis:
    st.info(f"📊 Set Attesi (xS): **{t_h} {ex_c:.2f}** | **{t_o} {ex_o:.2f}**")
    
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

    col_t1, col_t2 = st.columns([2, 1.2])
    
    with col_t1:
        st.subheader("🎯 Set Betting (Risultato Esatto)")
        df_sets = pd.DataFrame({
            "Risultato": ["2-0", "2-1", "0-2", "1-2"],
            "Vincitore": [t_h, t_h, t_o, t_o],
            "Probabilità": [f"{s_20:.1f}%", f"{s_21:.1f}%", f"{s_02:.1f}%", f"{s_12:.1f}%"],
            "Quota Fiera": [f"{100/s_20:.2f}" if s_20>0 else "0", f"{100/s_21:.2f}" if s_21>0 else "0", f"{100/s_02:.2f}" if s_02>0 else "0", f"{100/s_12:.2f}" if s_12>0 else "0"]
        }).sort_values(by="Probabilità", ascending=False)
        st.dataframe(df_sets.style.apply(lambda r: ['background-color: #ffeb3b; color: black; font-weight: bold']*4 if r.name == df_sets.index[0] else ['']*4, axis=1), hide_index=True, use_container_width=True)

    with col_t2:
        st.subheader("🎾 Testa a Testa (Match)")
        st.metric(f"VITTORIA {t_h[:8].upper()}", f"{p1_vincente:.1f}%", f"QF: {100/p1_vincente:.2f}" if p1_vincente>0 else "0")
        st.metric(f"VITTORIA {t_o[:8].upper()}", f"{p2_vincente:.1f}%", f"QF: {100/p2_vincente:.2f}" if p2_vincente>0 else "0")

    st.markdown("---")
    st.subheader("⚖️ Set Totali & Handicap Set")
    
    tc1 = st.columns(4)
    tc1[0].metric("UNDER 2.5 SET (Finisce in 2 Set)", f"{under_25_set:.1f}%", f"QF:{100/under_25_set:.2f}" if under_25_set>0 else "0")
    tc1[1].metric("OVER 2.5 SET (Si va al 3° Set)", f"{over_25_set:.1f}%", f"QF:{100/over_25_set:.2f}" if over_25_set>0 else "0")
    tc1[2].metric(f"HANDICAP SET 1 (-1.5)", f"{s_20:.1f}%", f"QF:{100/s_20:.2f}" if s_20>0 else "0")
    tc1[3].metric(f"HANDICAP SET 2 (+1.5)", f"{(s_02 + s_12 + s_21):.1f}%", f"QF:{100/(s_02 + s_12 + s_21):.2f}" if (s_02 + s_12 + s_21)>0 else "0")
