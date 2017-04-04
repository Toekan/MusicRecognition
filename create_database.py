import sqlite3
import time

print(time.clock())
conn = sqlite3.connect('shazamdb.db')
c = conn.cursor()
print(time.clock())

c.execute('CREATE TABLE hashtable (key INTEGER,  value INTEGER)')
#c.execute('DROP INDEX value_dict')
print(time.clock())
#c.execute('CREATE INDEX value_dict ON hashtable (key)')
print(time.clock())

conn.commit()
conn.close()