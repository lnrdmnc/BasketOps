#!/bin/bash

# Blocco l'esecuzione se un comando fallisce
set -e

echo "🚀 [DevOps] Avvio dell'ecosistema BasketOps in corso..."

# 1. Spegni eventuali container residui e riaccendi tutto in background
echo "📦 Configurazione e avvio dei container Docker..."
docker compose down
docker compose up --build -d

echo "⏳ Attesa che il database (PostgreSQL) sia pronto a ricevere connessioni..."
# Aspetta che il database risponda prima di lanciare gli script di inizializzazione
until docker exec basketops_backend_container pg_isready -h postgres_db -U basketadmin -d basketops_db > /dev/null 2>&1; do
  echo "   ...il database si sta inizializzando, attendo 2 secondi..."
  sleep 2
done

echo "✅ Database pronto!"

# 2. Copia i file aggiornati dalla root del Mac dentro il container del Backend
echo "📂 Copia degli script di configurazione nel container..."
docker cp init_db.py basketops_backend_container:/app/
docker cp populate_db.py basketops_backend_container:/app/

# 3. Inizializza le tabelle del Database
echo "📐 Inizializzazione delle tabelle SQL..."
docker exec basketops_backend_container python3 init_db.py

# 4. Popola il database con i dati NBA
echo "🏀 Scaricamento e popolamento dei dati NBA (API)..."
docker exec basketops_backend_container python3 populate_db.py

# 5. Addestra il modello predittivo di Machine Learning
echo "🧠 Addestramento del modello AI (scikit-learn)..."
docker exec basketops_backend_container python3 ai/predictor.py

echo "--------------------------------------------------------"
echo "🎉 [COMPLETATO] BasketOps AI è online e configurato!"
echo "📺 Frontend Streamlit: http://localhost:8501"
echo "🔌 Backend FastAPI API Docs: http://localhost:8000/docs"
echo "--------------------------------------------------------"

# Mostra i log in tempo reale per monitorare l'infrastruttura
docker compose logs -f