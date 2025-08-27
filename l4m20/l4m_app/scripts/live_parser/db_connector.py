import psycopg2
import decouple
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

    def select(self, table, cols, conditions):
        select_q = f"select {cols} from {table} where {conditions}"
        self.cur.execute(select_q)
        
        rows = self.cur.fetchall()
        return rows

    def insert(self, table, cols, data):
        insert_q = f"insert into {table} ({cols}) values (\
            %s %s %s %s %s %s %s %s %s %s \
            %s %s %s %s %s %s %s %s %s %s )"
        
        self.cur.execute(insert_q, data)

    def close(self):
        self.cur.close()
        self.conn.close()