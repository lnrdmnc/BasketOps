import time
import psycopg2
from nba_api.stats.static import players as nba_players_api
from nba_api.stats.endpoints import shotchartdetail
import os
def populate():

    db_host = os.getenv("DB_HOST", "localhost")
    # Connessione al DB
    conn = psycopg2.connect(
        host=db_host,
        database=os.getenv("DB_NAME", "basketops_db"),
        user=os.getenv("DB_USER", "basketadmin"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )
    cursor = conn.cursor()

    target_players = [
        "Stephen Curry", "Nikola Jokic", "Giannis Antetokounmpo", 
        "Luka Doncic", "LeBron James", "Kevin Durant"
    ]

    print(f"🏀 Inizio popolamento database per {len(target_players)} giocatori...")

    for name in target_players:
        search_results = nba_players_api.find_players_by_full_name(name)
        if not search_results:
            continue
        
        p_id = search_results[0]['id']
        print(f"🚀 Scaricamento e inserimento dati per: {name} (ID: {p_id})")

        try:
            # 1. Scarica i tiri dalla NBA API
            shot_data = shotchartdetail.ShotChartDetail(
                team_id=0, player_id=p_id, context_measure_simple='FGA',
                season_nullable='2023-24', season_type_all_star='Regular Season'
            )
            df = shot_data.get_data_frames()[0]

            if df.empty:
                continue

            # Prendiamo i dati della squadra dal primo tiro disponibile per quel giocatore
            t_id = int(df.iloc[0]['TEAM_ID'])
            t_name = str(df.iloc[0]['TEAM_NAME'])

            # 2. Inserisci il giocatore nella tabella 'players'
            cursor.execute(
                "INSERT INTO players (player_id, player_name, team_id, team_name) VALUES (%s, %s, %s, %s) ON CONFLICT (player_id) DO NOTHING",
                (p_id, name, t_id, t_name)
            )

            # 3. Inserisci tutti i suoi tiri nella tabella 'shots'
            for _, row in df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO shots (player_id, game_id, x, y, distance, made, period, minutes_remaining, seconds_remaining, shot_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        p_id, str(row['GAME_ID']), float(row['LOC_X']), float(row['LOC_Y']),
                        float(row['SHOT_DISTANCE']), bool(row['SHOT_MADE_FLAG']),
                        int(row['PERIOD']), int(row['MINUTES_REMAINING']), int(row['SECONDS_REMAINING']),
                        str(row['ACTION_TYPE'])
                    )
                )
            
            conn.commit() # Salva i dati di questo giocatore
            print(f"✅ Inseriti {len(df)} tiri nel database per {name}.")
            time.sleep(2) # Pausa anti-blocco

        except Exception as e:
            print(f"❌ Errore con {name}: {e}")
            conn.rollback()
            time.sleep(5)

    cursor.close()
    conn.close()
    print("🎉 Database BasketOps AI popolato con successo!")

if __name__ == "__main__":
    populate()