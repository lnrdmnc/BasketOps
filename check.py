import psycopg2

def verify_data():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="basketops_db",
            user="basketadmin",
            password="basketpassword",
            port="5432"
        )
        cursor = conn.cursor()
        
        print("🔍 --- VERIFICA DEI DATI IN CORSO --- 🔍\n")
        
        # 1. Contiamo i giocatori
        cursor.execute("SELECT COUNT(*) FROM players;")
        total_players = cursor.fetchone()[0]
        print(f"👥 Giocatori totali censiti nel DB: {total_players}")
        
        # Vediamo quali giocatori ci sono
        cursor.execute("SELECT player_name, team_name FROM players;")
        players_list = cursor.fetchall()
        for p in players_list:
            print(f"   • {p[0]} ({p[1]})")
            
        print("\n-----------------------------------------")
        
        # 2. Contiamo i tiri totali
        cursor.execute("SELECT COUNT(*) FROM shots;")
        total_shots = cursor.fetchone()[0]
        print(f"🏀 Tiri totali salvati: {total_shots}")
        
        # 3. Vediamo la distribuzione dei tiri per giocatore
        cursor.execute("""
            SELECT p.player_name, COUNT(s.id) 
            FROM players p 
            JOIN shots s ON p.player_id = s.player_id 
            GROUP BY p.player_name;
        """)
        distribution = cursor.fetchall()
        print("\n📊 Distribuzione dei tiri caricati:")
        for dist in distribution:
            print(f"   • {dist[0]}: {dist[1]} tiri")
            
        print("\n🚀 VERIFICA COMPLETATA!")
        
    except Exception as e:
        print(f"❌ Errore durante la verifica: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    verify_data()