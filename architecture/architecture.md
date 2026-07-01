# 🏛️ Architectural Documentation — BasketOps AI

Questo documento descrive in dettaglio l'architettura software, la topologia di rete, i flussi di dati e i pattern di integrazione scelti per la piattaforma **BasketOps AI**. Il sistema è stato ingegnerizzato seguendo i principi della programmazione a microservizi, dell'isolamento dei contesti e dell'automazione infrastrutturale (DevOps).

---

## 🗺️ Vista Topologica dell'Infrastruttura

L'intera applicazione vive all'interno di un'unica rete virtuale isolata creata da Docker Compose (`basketops_network`). Nessun container (eccetto il database, per scopi di debug locale) espone le proprie porte direttamente sul modulo di rete globale senza un mapping esplicito.

```text
       [ Browser dell'Utente (Host Mac) ]
           │                      │
    Porta 8501             Porta 8000
           │                      │
           ▼                      ▼
┌──────────────────────┐  ┌──────────────────────┐
│  basketops_frontend  │  │  basketops_backend   │
│     (Streamlit)      │  │      (FastAPI)       │
└──────────────────────┐  └──────────────────────┘
           │                         │
           │ (Rete Docker Interna)   │ (Rete Docker Interna)
           │ http://backend:8000     │ Host: postgres_db:5432
           │                         │
           └───────────┐ ┌───────────┘
                       ▼ ▼
            ┌──────────────────────┐
            │     postgres_db      │
            │  (PostgreSQL 15)     │
            └──────────────────────┘
                       │
               (Volume Docker)
                       ▼
            [ basketops_postgres_data ]