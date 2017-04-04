import sqlite3
import time


class SetDataBase:
    """Creates the class to act on a sqlite database, it can add a value to the set/list that
    belongs to a certain key, or take a whole set out with the key"""

    def __init__(self,databasename):
        self.conn = sqlite3.connect(databasename)
        self.c = self.conn.cursor()
        self.timer1 = []
        self.timer2 = []

    def add_value(self,key,values):
        """Adding values connected with a certain key to the database. Checks if the key already exists, if not
        we insert it with the values, if it does exist, we take the BLOB out of the database, unpack it with pickle,
        extend the list with the new values and put it back."""
        for value in values:
            self.c.execute('INSERT INTO hashtable VALUES(?,?)',(key,value))

    def get_values(self,key):
        """Taking sets/lists of values (SongID+t_abs) out of the database with the key created before.
        An empty list is returned if the key doesn't have a match in the database, can be used as a boolean
        False."""

        t = (key,)
        a = time.clock()
        values = self.c.execute('SELECT value FROM hashtable WHERE key = ?',t).fetchall()
        b = time.clock()
        self.timer1.append((b - a))
        if values is not None:
            elements = (elem[0] for elem in values)
            c = time.clock()
            self.timer2.append((c - b))
            return elements
        else:
            return []



    def close_connection(self):
        self.conn.commit()
        self.conn.close()