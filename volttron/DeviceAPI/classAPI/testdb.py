import pprint
import psycopg2
import sys

db_database = 'postgres'
db_host = 'peahivedev2.postgres.database.azure.com'
db_port = '5432'
db_user = 'peahive@peahivedev2'
db_password = '28Sep1960'


name = '15FIT01'

# conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,user=db_user, password=db_password)
# cursor = conn.cursor()
#
# # execute our Query
# cursor.execute("SELECT * FROM device_info")
#
# # retrieve the records from the database
# records = cursor.fetchall()
# print "--------------------------------------"
# print records
# print "--------------------------------------"

conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,user=db_user, password=db_password)
cursor = conn.cursor()
cur = conn.cursor()

cur.execute("""SELECT * from device_info""")
rows = cur.fetchall()
print "\nRows: \n"
for row in rows:
    if row[0] == '15FIT01':
        print "   ", row[0]
    else:
        a = True

cur.execute(
                        """INSERT INTO device_info (device_id, device_type,device_model,device_name,
                        date_added,room_id,device_model_id,gateway_id,is_enable) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                        (str("03WSP060BFEA2"), str("smartplug"),'indoor','homeplug','2017-09-02 05:07:41.402+00','1','03WSP','1',True))
con.commit()
conn.close()