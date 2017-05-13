import sqlite3


conn = sqlite3.connect('Data/shazamdb.db')
c = conn.cursor()


#c.execute('CREATE TABLE hashtable (key INTEGER,  value INTEGER)')
#c.execute('DROP INDEX value_dict')

c.execute('CREATE INDEX value_dict ON hashtable (key)')


conn.commit()
conn.close()