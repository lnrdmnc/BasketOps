from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="BasketOps AI API",
    description="Backend Engine per l'analisi dei tiri e statistiche avanzate NBA",
    version="1.0.0"
)

# Configurazione CORS: permette al Frontend (Streamlit) di parlare con il Backend senza blocchi di sicurezza
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In produzione metteremo l'URL specifico del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funzione interna per connettersi al database PostgreSQL su Docker
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="basketops_db",
        user="basketadmin",
        password="basketpassword",
        port="5432",
        cursor_factory=RealDictCursor # Trasforma i risultati delle query direttamente in dizionari Python (perfetti per JSON)
    )

# 1. Rotta di test (Root)
@app.get("/")
def read_root():
    return {"status": "online", "message": "Benvenuto su BasketOps AI API Engine"}

# 2. API per ottenere la lista di tutti i giocatori presenti nel DB
@app.get("/api/v1/players")
def get_players():
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