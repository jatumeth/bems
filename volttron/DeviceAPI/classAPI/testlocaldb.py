import pprint
import psycopg2
import sys

def updatedb(name):
    print 'update'
    name = name
    cur.execute("UPDATE scenceappagent SET info=%s WHERE scence=%s", ('{"topic1":"hivecdf12345","message":{"name":"myscence","tasks":[{"command":{"status":"on"},"device_id":"18DOR1445K1200138"},{"command":{"status":"on"},"device_id":"2HUEK1445K1200138"}]}}', name))
    conn.commit()
    conn.close()

def insertdb(name):
    print 'insert'
    jsoninfo ='{"topic77":"hivecdf12345"}'
    namescence = name

    cur.execute(
        """INSERT INTO scenceappagent (scence, info) VALUES (%s,%s);""",
        (str(namescence),jsoninfo))
    conn.commit()
    conn.close()


db_database = 'hivedb'
db_host = 'localhost'
db_port = '5432'
db_user = 'hiveadmin'
db_password = 'hiveadmin'

name = 'myscence3'
conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,user=db_user, password=db_password)
cursor = conn.cursor()
cur = conn.cursor()
xx = 'goodmorning'



# cur.execute("SELECT * FROM scenceappagent WHERE scence = ANY(%s)", (xx))
cur.execute("SELECT * FROM scenceappagent WHERE scence = %s", (xx,))
scence = cur.fetchone()[2]
scence_conve = list(scence)

for i in range(len(scence_conve)):
    print(scence_conve[i])
    device = str(scence_conve[i]['device_id'])
    command = scence_conve[i]['command']
    print device
    print command


# cur.execute("""SELECT * from scenceappagent""")
# rows = cur.fetchall()
# checkinsert = True
# for row in rows:
#     if (str(row[1]).replace(" ", "")) == (str(name).replace(" ", "")):
#         updatedb(name)
#         checkinsert = False
#     else:
#         a = True
# if checkinsert == True:
#     insertdb(name)
# print checkinsert
