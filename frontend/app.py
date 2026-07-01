import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(page_title="BasketOps AI", layout="wide")

st.title("🏀 BasketOps AI - Shot Chart Analyzer")
st.subheader("Visualizzazione spaziale e intelligenza balistica")
API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-Key": API_KEY}

if os.getenv("DOCKER_ENV") == "true":
    BACKEND_URL = "http://backend:8000/api/v1"
else:
    BACKEND_URL = "http://127.0.0.1:8000/api/v1"

@st.cache_data
def load_players():
    try:
        response = requests.get(f"{BACKEND_URL}/players", headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        st.error("❌ Impossibile connettersi al Backend FastAPI. Assicurati che sia acceso!")
        return []
players_data = load_players()

if not players_data:
    st.info("In attesa che il backend si avvii...")
else:
    # Creiamo un dizionario comodo per il menu a tendina: "Nome Giocatore" -> ID
    player_dict = {p['player_name']: p['player_id'] for p in players_data}
    
    # Barra laterale per i filtri
    st.sidebar.header("Filtri Giocatore")
    selected_player_name = st.sidebar.selectbox("Seleziona un Giocatore:", list(player_dict.keys()))
    selected_player_id = player_dict[selected_player_name]

    # 2. Recupera i tiri del giocatore selezionato dal Backend
    with st.spinner("Caricamento tiri dal database..."):
        response = requests.get(f"{BACKEND_URL}/shots/{selected_player_id}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            shots_list = data['shots']
            df = pd.DataFrame(shots_list)
        else:
            df = pd.DataFrame()

    if not df.empty:
        # Metriche veloci in alto
        made_shots = df[df['made'] == True].shape[0]
        total_shots = df.shape[0]
        fg_pct = (made_shots / total_shots) * 100 if total_shots > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Tiri Totali", total_shots)
        col2.metric("Tiri Segnati", made_shots)
        col3.metric("Percentuale dal Campo (FG%)", f"{fg_pct:.1f}%")

        # 3. DISEGNO DELLO SHOT CHART CON PLOTLY
        # Creiamo due Tab in Streamlit per pulire l'interfaccia
        tab1, tab2 = st.tabs(["🎯 Shot Chart Classico", "🔥 Heatmap di Densità"])

        with tab1:
            # --- CODICE DELLO SHOT CHART CLASSICO ---
            fig = go.Figure()
            made_df = df[df['made'] == True]
            missed_df = df[df['made'] == False]

            fig.add_trace(go.Scatter(
                x=missed_df['x'], y=missed_df['y'], mode='markers', name='Sbagliato',
                marker=dict(color='red', size=5, opacity=0.5)
            ))
            fig.add_trace(go.Scatter(
                x=made_df['x'], y=made_df['y'], mode='markers', name='Segnato',
                marker=dict(color='green', size=5, opacity=0.6)
            ))
            
            # Linee del campo
            fig.add_shape(type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, line_color="black")
            fig.add_shape(type="line", x0=-30, y0=-7.5, x1=30, y1=-7.5, line_color="black")
            fig.add_shape(type="rect", x0=-80, y0=-52, x1=80, y1=143, line_color="black")

            fig.update_layout(
                width=700, height=500,
                xaxis=dict(range=[-250, 250], visible=False),
                yaxis=dict(range=[-52, 420], visible=False),
                plot_bgcolor='white'
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            # --- CODICE DELLA HEATMAP CORRETTO ---
            with st.spinner("Generazione mappa di densità..."):
                heat_response = requests.get(f"{BACKEND_URL}/analytics/heatmap/{selected_player_id}" , headers=HEADERS)
                if heat_response.status_code == 200:
                    heat_data = heat_response.json()
                    hdf = pd.DataFrame(heat_data)
                else:
                    hdf = pd.DataFrame()

            if not hdf.empty:
                # Usiamo go.Scatter (2D) mappando il colore sul volume dei tiri
                fig_heat = go.Figure(data=go.Scatter(
                    x=hdf['x_bin'], y=hdf['y_bin'],
                    mode='markers',
                    marker=dict(
                        size=14,
                        symbol='square', 
                        color=hdf['tiri_tentati'], 
                        colorscale='YlOrRd', 
                        showscale=True,
                        colorbar=dict(title="Volume Tiri")
                    ),
                    text=[f"Tiri tentati in questa zona: {int(t)}" for t in hdf['tiri_tentati']],
                    hoverinfo='text'
                ))

                # Disegniamo le linee guida del campo
                fig_heat.add_shape(type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, line_color="gray")
                fig_heat.add_shape(type="line", x0=-30, y0=-7.5, x1=30, y1=-7.5, line_color="gray")
                fig_heat.add_shape(type="rect", x0=-80, y0=-52, x1=80, y1=143, line_color="gray")

                fig_heat.update_layout(
                    width=700, height=500,
                    xaxis=dict(range=[-250, 250], visible=False, fixedrange=True),
                    yaxis=dict(range=[-52, 420], visible=False, fixedrange=True),
                    plot_bgcolor='white',
                    title=f"Mappa delle zone calde di {selected_player_name}"
                )
                st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("Nessun tiro trovato per questo giocatore.")

    # --- SEZIONE: AI SHOT SIMULATOR (CORRETTAMENTE INDENTATA DENTRO L'ELSE PRINCIPALE) ---
    st.markdown("---")
    st.header("🧠 AI Shot Simulator (Modello Predittivo)")
    st.write("Sposta i cursori per simulare la posizione di un giocatore e calcolare istantaneamente la probabilità di fare canestro stimata dall'Intelligenza Artificiale.")

    col_sim1, col_sim2, col_sim3 = st.columns(3)
    
    with col_sim1:
        sim_dist = st.slider("Distanza dal canestro (in piedi):", min_value=0.0, max_value=40.0, value=15.0, step=0.5)
        sim_period = st.selectbox("Quarto di gioco (Period):", [1, 2, 3, 4])
        
    with col_sim2:
        max_x_allowed = min(25.0, sim_dist)
        sim_x_feet = st.slider("Spostamento laterale X (in piedi):", 
                               min_value=-float(max_x_allowed), 
                               max_value=float(max_x_allowed), 
                               value=0.0, 
                               step=0.5)
        sim_min = st.slider("Minuti rimanenti nel quarto:", min_value=0, max_value=12, value=5)
        
    with col_sim3:
        sim_y_feet = np.sqrt(max(0.0, sim_dist**2 - sim_x_feet**2))
        
        sim_x = int(sim_x_feet * 10)
        sim_y = int(sim_y_feet * 10)
        
        st.info(f"📍 Coordinate generate per l'AI:\n\n**X:** {sim_x} | **Y:** {sim_y}")
        sim_sec = st.slider("Secondi rimanenti sul cronometro:", min_value=0, max_value=59, value=30)

    # Bottone di calcolo collegato all'API POST del Backend
    if st.button("🔮 Calcola Probabilità con l'AI", type="primary"):
        payload = {
            "x": float(sim_x),
            "y": float(sim_y),
            "distance": float(sim_dist),
            "period": int(sim_period),
            "minutes_remaining": int(sim_min),
            "seconds_remaining": int(sim_sec)
        }
        
        try:
            ai_response = requests.post(f"{BACKEND_URL}/predict-shot", json=payload)
            if ai_response.status_code == 200:
                result = ai_response.json()
                prob = result["shot_probability_pct"]
                
                if prob >= 50:
                    st.success(f"### 🎯 Alta Probabilità: **{prob}%** di successo!")
                elif prob >= 35:
                    st.warning(f"### ⚖️ Tiro Discreto: **{prob}%** di successo.")
                else:
                    st.error(f"### 🧱 Tiro Difficile: **{prob}%** di successo (Rischio mattone).")
            else:
                st.error("Errore nella risposta del motore AI.")
        except Exception as e:
            st.error(f"Impossibile comunicare con l'API predittiva: {e}")