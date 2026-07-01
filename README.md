# 🏀 BasketOps AI — Advanced Basketball Analytics Platforms

BasketOps AI è una piattaforma integrata di pallacanestro analitica e predittiva. Il sistema raccoglie i dati sui tiri in tempo reale tramite le API NBA, modella le coordinate spaziali del campo da gioco attraverso un database relazionale, genera Shot Charts e Heatmaps di densità interattive, e utilizza un modello di Machine Learning per stimare la probabilità di successo di qualsiasi tiro in base alla posizione e alle condizioni di gioco.

L'intera applicazione è stata ingegnerizzata seguendo la filosofia **DevOps**, distribuendo i servizi attraverso container Docker isolati e orchestrati per garantire la massima portabilità e riproducibilità su qualsiasi ambiente (locale o cloud).

---

## 📐 Architettura del Sistema (Microservizi)

L'applicazione è suddivisa in tre macro-servizi indipendenti che comunicano all'interno di una rete virtuale isolata Docker:

1. **Frontend (Streamlit)**: Interfaccia utente reattiva che permette di visualizzare i dati storici dei giocatori, esplorare le mappe di tiro e simulare conclusioni a canestro.
2. **Backend (FastAPI)**: Il motore logico e analitico dell'applicazione. Espone le API REST per il frontend, elabora le metriche geometriche e ospita il predittore AI.
3. **Database (PostgreSQL)**: Il layer di persistenza dei dati, configurato con un volume Docker dedicato per garantire la conservazione dei dati storici anche in caso di spegnimento dei container.

---

## 🛠️ Tecnologie Utilizzate

- **Core & API**: Python 3.8, FastAPI, Uvicorn
- **Data Science & AI**: Scikit-Learn (Logistic Regression), Pandas, NumPy
- **Data Visualization**: Streamlit, Plotly (Shot Charts & Kernel Density Heatmaps)
- **Database**: PostgreSQL 15 (Alpine-based), Psycopg2
- **DevOps & Deployment**: Docker, Docker Compose, Bash Scripting Automation

---

## 📁 Struttura del Progetto

```text
BasketOps/
├── .basketops/               # Ambiente virtuale Python locale
├── ai/
│   ├── predictor.py          # Script di training dell'algoritmo di Machine Learning
│   └── shot_model.pkl        # Modello predittivo serializzato (generato post-training)
├── analytics/
│   └── engine.py             # Algoritmi di computazione geometrica per le mappe di tiro
├── backend/
│   ├── Dockerfile            # Configurazione Docker per il container FastAPI
│   └── main.py               # Entrypoint delle API REST (FastAPI)
├── frontend/
│   ├── Dockerfile            # Configurazione Docker per il container Streamlit
│   └── app.py                # Interfaccia grafica utente (Streamlit)
├── docker-compose.yml        # Orchestratore dei tre container e delle reti interne
├── init_db.py                # Script di inizializzazione dello schema SQL delle tabelle
├── populate_db.py            # Client API per l'estrazione e il caricamento dati NBA
├── requirements.txt          # Dipendenze centralizzate del progetto
└── start.sh                  # Script DevOps di automazione e orchestrazione totale