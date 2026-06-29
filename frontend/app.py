import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="BasketOps AI", layout="wide")

st.title("🏀 BasketOps AI - Shot Chart Analyzer")
st.subheader("Visualizzazione spaziale e intelligenza balistica")

# URL del nostro backend FastAPI
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# 1. Recupera la lista dei giocatori dal Backend
@st.cache_data # Evita di rifare la chiamata API a ogni click, velocizzando l'app
def load_players():
    try:
        response = requests.get(f"{BACKEND_URL}/players")
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
        response = requests.get(f"{BACKEND_URL}/shots/{selected_player_id}")
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
        # Le coordinate NBA sono in decimi di piede. Il campo è largo 50 piedi (-250 a 250) e lungo 47 (-50 a 420).
        fig = go.Figure()

        # Separazione tiri segnati / sbagliati
        made_df = df[df['made'] == True]
        missed_df = df[df['made'] == False]

        # Aggiungiamo i tiri sbagliati (Rossi)
        fig.add_trace(go.Scatter(
            x=missed_df['x'], y=missed_df['y'],
            mode='markers',
            name='Sbagliato',
            marker=dict(color='red', size=6, opacity=0.6),
            text=missed_df['shot_type']
        ))

        # Aggiungiamo i tiri segnati (Verdi)
        fig.add_trace(go.Scatter(
            x=made_df['x'], y=made_df['y'],
            mode='markers',
            name='Segnato',
            marker=dict(color='green', size=6, opacity=0.7),
            text=made_df['shot_type']
        ))

        # Tracciamo le linee essenziali del campo da basket (Canestro e Tabellone)
        # Canestro (Raggio 7.5 decimi di piede a x=0, y=0)
        fig.add_shape(type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, line_color="black")
        # Tabellone (Linea orizzontale a y=-7.5 da x=-30 a 30)
        fig.add_shape(type="line", x0=-30, y0=-7.5, x1=30, y1=-7.5, line_color="black")
        # Area dei tre secondi (Rettangolo)
        fig.add_shape(type="rect", x0=-80, y0=-52, x1=80, y1=143, line_color="black")

        # Configurazione layout del grafico per farlo sembrare un campo da basket
        fig.update_layout(
            width=700, height=600,
            xaxis=dict(range=[-250, 250], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[-52, 420], showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='white',
            title=f"Shot Chart di {selected_player_name} - Stagione 2023-24",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Nessun tiro trovato per questo giocatore.")