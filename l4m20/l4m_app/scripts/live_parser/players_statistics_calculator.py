from db_connector import *
import constants as C
import utilities as U

try:
    conn = DB_Connector()
    players_stats = U.get_players_statistics(conn)
    
    for player_id, stats in players_stats.items():
        conn.update_player_statistics(player_id, stats)
    conn.commit()
except Exception as e:
        print(f"Error calculating player statistics: {e}")