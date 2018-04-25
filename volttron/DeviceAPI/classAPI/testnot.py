import psycopg2

conn = psycopg2.connect(host="localhost", port="5432",
                        user="admin", password="admin",
                        dbname="bemossdb")


cur = conn.cursor()
cur.execute("SELECT * from information_schema.tables where table_name=%s", ("ac_saijo_token",))
if bool(cur.rowcount):
    pass
else:
    cur.execute('''CREATE TABLE ac_saijo_token(id SERIAL PRIMARY KEY NOT NULL,
            accesstoken VARCHAR(50) NOT NULL, time TIMESTAMP);''')
    print "create new database ac_saijo_token"
    conn.commit()
    cur.execute('INSERT INTO ac_saijo_token (id, accesstoken, time) VALUES (%s, %s ,%s)',
                ('1', 'aaa', datetime.datetime.now()))
    conn.commit()

cur = conn.cursor()
cur.execute('UPDATE ac_saijo_token SET accesstoken=%s WHERE id=%s', (self.token, "1"))
conn.commit()
cur = conn.cursor()
cur.execute('UPDATE ac_saijo_token SET time=%s WHERE id=%s', (datetime.datetime.now(), "1"))
conn.commit()