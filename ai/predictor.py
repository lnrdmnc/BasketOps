import psycopg2
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "shot_model.pkl")

def train_shot_predictor():
    """
    Estrae tutti i tiri dal database, addestra il modello di Machine Learning
    e lo salva su disco in formato pickle.
    """
    print("🧠 AI Engine: Connessione al DB per estrazione dataset di addestramento...")
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        conn = psycopg2.connect(
            host=db_host,
            database=os.getenv("DB_NAME", "basketops_db"),
            user=os.getenv("DB_USER", "basketadmin"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )
        # Estraiamo le feature geometriche e temporali, e il target 'made'
        query = "SELECT x, y, distance, period, minutes_remaining, seconds_remaining, made FROM shots;"
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        print(f"❌ Errore di connessione al DB durante il training AI: {e}")
        return False

    if df.empty:
        print("⚠️ Dataset vuoto! Impossibile addestrare l'AI.")
        return False

    print(f"📊 Dataset caricato: {len(df)} tiri disponibili per l'addestramento.")

    # 1. Definizione di Features (X) e Target (y)
    X = df[['x', 'y', 'distance', 'period', 'minutes_remaining', 'seconds_remaining']]
    y = df['made'].astype(int) # Convertiamo True/False in 1/0

    # 2. Split del dataset: 80% Addestramento, 20% Test per la verifica delle performance
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Inizializzazione e Addestramento del modello di Regressione Logistica
    print("🏋️ Addestramento dell'algoritmo in corso...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # 4. Calcolo dell'Accuratezza
    accuracy = model.score(X_test, y_test)
    print(f"🎯 Addestramento completato! Accuratezza del modello: {accuracy*100:.2f}%")

    # 5. Salvataggio del modello su file pkl
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"💾 Modello AI salvato con successo in: {MODEL_PATH}")
    return True

def predict_shot_probability(x, y, distance, period, minutes_remaining, seconds_remaining):
    """
    Carica il modello salvato e calcola la probabilità percentuale di successo di un tiro.
    """
    if not os.path.exists(MODEL_PATH):
        # Se il modello non esiste, lo addestriamo al volo
        success = train_shot_predictor()
        if not success:
            return 45.0 # Valore di fallback generico se l'AI fallisce
            
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
        
    # Prepariamo i dati nel formato richiesto dal modello (array 2D)
    features = np.array([[x, y, distance, period, minutes_remaining, seconds_remaining]])
    
    # predict_proba restituisce [probabilità_0, probabilità_1]. A noi interessa la probabilità di 1 (canestro segnato)
    probabilities = model.predict_proba(features)
    make_probability = probabilities[0][1] * 100
    
    return round(make_probability, 1)

if __name__ == "__main__":
    # Avviando lo script direttamente, addestriamo il modello
    train_shot_predictor()