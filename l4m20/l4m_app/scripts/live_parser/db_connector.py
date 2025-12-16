import psycopg2
from decouple import config

class DB_Connector:
    def __init__(self):

        self.conn = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port="5432"
        )

        self.cur = self.conn.cursor()

    def delete(self, table, conditions):
        delete_q = f"delete from {table} where {conditions}"
        self.cur.execute(delete_q)

    def select(self, table, cols, conditions, data):
        select_q = f"select {cols} from {table} where {conditions}"
        self.cur.execute(select_q, data)

        rows = self.cur.fetchall()
        return rows

    def insert(self, table, data):
        insert_q = f"insert into {table} (\"Day\",\"Vote\",\"TotVote\",\"GoalSc\",\"GoalTa\",\"GoalDe\",\"PenSc\",\"PenMi\",\"PenSa\",\"Own\",\"Yel\",\
            \"Red\",\"YelRed\",\"AssS\",\"AssL\",\"AssH\",\"AssP\",\"SubJ\",\"Sub\",\"Competition_id\",\"Player_id\",\"RealTeam_id\",\"Live\") values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        
        self.cur.execute(insert_q, data)

    def insert_player(self, surname, role, realteam_id):
        insert_q = f"insert into l4m_app_player (\"Surname\", \"Role\", \"RealTeam_id\", \"Status\") values (%s,%s,%s,%s)"

        self.cur.execute(insert_q, (surname, role, realteam_id, 'A'))

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()