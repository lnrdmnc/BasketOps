from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from analytics.engine import calculate_advanced_stats, generate_heatmap_data

from pydantic import BaseModel
from ai.predictor import predict_shot_probability

# backend/main.py
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader






# Definiamo la struttura dati che l'API deve aspettarsi dal frontend
class ShotPredictionRequest(BaseModel):
    x: float
    y: float
    distance: float
    period: int
    minutes_remaining: int
    seconds_remaining: int

app = FastAPI(
    title="BasketOps AI API",
    description="Backend Engine per l'analisi dei tiri e statistiche avanzate NBA",
    version="1.0.0"
)

# Configurazione CORS: permette al Frontend (Streamlit) di parlare con il Backend senza blocchi di sicurezza
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], 
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Funzione interna per connettersi al database PostgreSQL su Docker
import os

def get_db_connection():
    # Se rileva che è dentro Docker usa 'postgres_db', altrimenti usa 'localhost'
    db_host = os.getenv("DB_HOST", "localhost")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "basketops_db"),
        user=os.getenv("DB_USER", "basketadmin"),
        password=os.getenv("DB_PASSWORD"),  # niente default: se manca, deve fallire
        port=os.getenv("DB_PORT", "5432"),
    )

# 1. Rotta di test (Root)
@app.get("/")
def read_root():
    return {"status": "online", "message": "Benvenuto su BasketOps AI API Engine"}


API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Accesso negato")

@app.get("/api/v1/players", dependencies=[Depends(verify_api_key)])
def get_players():
    
    
    
    import logging
logger = logging.getLogger("basketops")

except Exception as e:
    logger.error(f"Errore DB: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Errore interno del server")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT player_id, player_name, team_name FROM players ORDER BY player_name;")
        players = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return players
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore del database: {str(e)}")

# 3. API per ottenere tutti i tiri di un giocatore specifico tramite il suo ID
@app.get("/api/v1/shots/{player_id}")
def get_player_shots(player_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifichiamo prima se il giocatore esiste
        cursor.execute("SELECT player_name FROM players WHERE player_id = %s;", (player_id,))
        player = cursor.fetchone()
        if not player:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Giocatore non trovato nel database")
        
        # Estraiamo tutti i tiri di quel giocatore
        cursor.execute("""
            SELECT id, x, y, distance, made, period, minutes_remaining, seconds_remaining, shot_type 
            FROM shots 
            WHERE player_id = %s;
        """, (player_id,))
        shots = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "player_id": player_id,
            "player_name": player["player_name"],
            "total_shots": len(shots),
            "shots": shots
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore del database: {str(e)}")

# 4. API per ottenere le statistiche avanzate di un giocatore
@app.get("/api/v1/analytics/stats/{player_id}")
def get_advanced_player_stats(player_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, x, y, distance, made FROM shots WHERE player_id = %s;", (player_id,))
        shots = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Usiamo l'engine per calcolare i dati avanzati
        stats = calculate_advanced_stats(shots)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. API per ottenere i dati della Heatmap raggruppati
@app.get("/api/v1/analytics/heatmap/{player_id}")
def get_player_heatmap(player_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT x, y, made FROM shots WHERE player_id = %s;", (player_id,))
        shots = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        heatmap_data = generate_heatmap_data(shots)
        return heatmap_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    # 6. API Predittiva con Machine Learning
@app.post("/api/v1/predict-shot")
def predict_shot(request: ShotPredictionRequest):
    try:
        probability = predict_shot_probability(
            x=request.x,
            y=request.y,
            distance=request.distance,
            period=request.period,
            minutes_remaining=request.minutes_remaining,
            seconds_remaining=request.seconds_remaining
        )
        return {
            "status": "success",
            "shot_probability_pct": probability,
            "message": f"Questo tiro ha il {probability}% di probabilità di andare a segno."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

