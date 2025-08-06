import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="l4m20_db",
        user="andrea",
        password="pg_andrea!")

    cur = conn.cursor()
    cur.execute("CALL bet_update();")
    conn.commit()


except (Exception, psycopg2.DatabaseError) as error:
    raise(error)
finally:
    cur.close()
    if conn is not None:
        conn.close()
