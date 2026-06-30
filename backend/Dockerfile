# Usa un'immagine Python ufficiale leggera
FROM python:3.8-slim

# Imposta la cartella di lavoro dentro il container
WORKDIR /app

# Copia i requisiti e installali
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice del backend e l'engine di analytics/AI necessari
COPY ./backend ./backend
COPY ./analytics ./analytics
COPY ./ai ./ai

# Esponi la porta di FastAPI
EXPOSE 8000

# Comando per avviare il backend (usiamo 0.0.0.0 per accettare connessioni esterne al container)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]