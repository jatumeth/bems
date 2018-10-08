
import sqlite3
from os.path import expanduser
gg = home_path = expanduser("~")
path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
conn = sqlite3.connect(gg+path)
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE scenes
       (SCENE_ID SERIAL   PRIMARY KEY   NOT NULL,
       SCENE_NAME   VARCHAR(30)   NOT NULL,
       SCENE_TASKS     TEXT);''')
print "Table scenes created successfully"


c.execute('''CREATE TABLE token
       (gateway_id VARCHAR(30)   PRIMARY KEY   NOT NULL,
       login_token   VARCHAR(30)   NOT NULL,
       expo_token     VARCHAR(30)   NOT NULL);''')
print "Table token  created successfully"

c.execute('''CREATE TABLE automation
       (automation_id SERIAL   PRIMARY KEY   NOT NULL,
       automation_image   VARCHAR(30)   NOT NULL,
       automation_name   VARCHAR(30)   NOT NULL,
       trigger_device   TEXT,
       trigger_event   VARCHAR(30)   NOT NULL,
       trigger_value   VARCHAR(30)   NOT NULL,
       condition_event VARCHAR(30)   NOT NULL,
       action_tasks   TEXT);''')
print "Table automation created successfully"


c.execute('''CREATE TABLE active_scene
       (SCENE_ID SERIAL   PRIMARY KEY   NOT NULL,
       SCENE_NAME   VARCHAR(30)   NOT NULL);''')
print "Table active_scene created successfully"

# Insert a row of data
# c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
