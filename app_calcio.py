import streamlit as st
import math
import pandas as pd
import numpy as np

# Funzione per calcolare Poisson
def poisson_probability(lmbda, x):
    return (math.exp(-lmbda) * (lmbda ** x)) / math.factorial(x)

st.set_page_config(page_title="FT Score Detector", layout="wide")

st.title("⚽ Full Time Correct Score Predictor")
st.write("Analisi statistica basata sulla distribuzione di Poisson per i 90 minuti (FT)")

# --- INPUT DATI ---
st.sidebar.header("Dati Squadre (Full Time)")
casa_gol = st.sidebar.number_input("Gol Fatti in Casa (Totali)", value=20)
casa_match = st.sidebar.number_input("Partite giocate in Casa", value=10)
ospite_gol = st.sidebar.number_input("Gol Fatti in Trasferta (Totali)", value=15)
ospite_match = st.sidebar.number_input("Partite giocate in Trasferta", value=10)

media_casa = casa_gol / casa_match if casa_match > 0 else 0
media_ospite = ospite_gol / ospite_match if ospite_match > 0 else 0

st.sidebar.write(f"**Media Casa:** {media_casa:.2f}")
st.sidebar.write(f"**Media Ospite:** {media_ospite:.2f}")

# --- CALCOLO MATRICE ---
max_goals = 6 
matrix = np.zeros((max_goals, max_goals))

prob_casa = [poisson_probability(media_casa, i) for i in range(max_goals)]
prob_ospite = [poisson_probability(media_ospite, i) for i in range(max_goals)]

for h in range(max_goals):
    for a in range(max_goals):
        matrix[h, a] = prob_casa[h] * prob_ospite[a]

# --- LAYOUT PRINCIPALE ---
col_mat, col_val = st.columns([2, 1])

with col_mat:
    st.subheader("📊 Matrice Probabilità Risultati")
    df_matrix = pd.DataFrame(
        matrix * 100, 
        index=[f"Casa {i}" for i in range(max_goals)],
        columns=[f"Ospite {i}" for i in range(max_goals)]
    )
    st.dataframe(df_matrix.style.format("{:.2f}%").background_gradient(cmap='Greens'))

with col_val:
    st.subheader("🎯 Top Risultati (Quota Fair)")
    risultati = []
    for h in range(max_goals):
        for a in range(max_goals):
            prob = matrix[h, a]
            if prob > 0.01: # Mostra solo quelli con probabilità > 1%
                risultati.append({
                    "Risultato": f"{h}-{a}",
                    "Probabilità": prob * 100,
                    "Quota Fair": 1 / prob
                })
    
    df_res = pd.DataFrame(risultati).sort_values(by="Probabilità", ascending=False)
    st.table(df_res.head(10).style.format({"Probabilità": "{:.2f}%", "Quota Fair": "{:.2f}"}))

# --- MERCATI ACCESSORI ---
st.subheader("📈 Altri Mercati")
c1, c2, c3 = st.columns(3)

over_05 = (1 - (matrix[0, 0])) * 100
over_15 = (1 - (matrix[0, 0] + matrix[1, 0] + matrix[0, 1])) * 100
over_25 = (1 - (matrix[0, 0] + matrix[1, 0] + matrix[0, 1] + matrix[2, 0] + matrix[0, 2] + matrix[1, 1])) * 100
goal = 0
for h in range(1, max_goals):
    for a in range(1, max_goals):
        goal += matrix[h, a]

c1.metric("Over 0.5 FT", f"{over_05:.2f}%")
c2.metric("Over 2.5 FT", f"{over_25:.2f}%")
c3.metric("Segnano Entrambi (Goal)", f"{goal*100:.2f}%")