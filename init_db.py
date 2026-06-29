import psycopg2

def initialize_database():
    try:
        # Connessione al database PostgreSQL su Docker
        conn = psycopg2.connect(
            host="localhost",
            database="basketops_db",
            user="basketadmin",
            password="basketpassword",
            port="5432"
        )
        cursor = conn.cursor()
        
        print("⚡ Connessione al database riuscita!")
        
        # 1. Pulizia: eliminiamo le tabelle se esistono in uno stato corrotto
        print("🧹 Pulizia vecchie tabelle (se esistenti)...")
        cursor.execute("DROP TABLE IF EXISTS shots CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS players CASCADE;")
        
        # 2. Creazione Tabella Players
        print("📐 Creazione tabella 'players'...")
        cursor.execute("""
            CREATE TABLE players (
                player_id INT PRIMARY KEY,
                player_name VARCHAR(150) NOT NULL,
                team_id INT,
                team_name VARCHAR(100)
            );
        """)
        
        # 3. Creazione Tabella Shots
        print("📐 Creazione tabella 'shots'...")
        cursor.execute("""
            CREATE TABLE shots (
                id SERIAL PRIMARY KEY,
                player_id INT REFERENCES players(player_id) ON DELETE CASCADE,
                game_id VARCHAR(50),
                x NUMERIC(5,2) NOT NULL,
                y NUMERIC(5,2) NOT NULL,
                distance NUMERIC(4,1) NOT NULL,
                made BOOLEAN NOT NULL,
                period INT NOT NULL,
                minutes_remaining INT,
                seconds_remaining INT,
                shot_type VARCHAR(100)
            );
        """)
        
        # CRITICO: Conferma l'operazione sul database
        conn.commit()
        print("💾 Modifiche salvate con successo (COMMIT)!")
        
        # 4. VERIFICA REALE: Chiediamo al DB se le tabelle esistono davvero
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        print(f"📊 Tabelle effettivamente presenti nel database: {tables}")
        
    except Exception as e:
        print(f"❌ ERRORE CRITICO DURANTE L'INIZIALIZZAZIONE: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
            print("🔌 Connessione chiusa.")

if __name__ == "__main__":
    initialize_database()