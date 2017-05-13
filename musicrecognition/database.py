import sqlite3

class SetDataBase:
    """
    Creates the class to act on the sqlite database.
    functions:
        add_value:  Adds key-value pairs to the database, one key has a
                    variable length list of values.

        get_values: Takes all the values with matching key in the database.
                    Return empty list when key doesn't have a match, intended
                    to be used as boolean false.
    """

    def __init__(self,databasename):
        self.conn = sqlite3.connect(databasename)
        self.c = self.conn.cursor()

    def add_values(self,key,values):
        """Adding key-value pairs to the database, one key has a variable
        length list of values."""

        for value in values:
            self.c.execute('INSERT INTO hashtable VALUES(?,?)',(key,value))

    def get_values(self,key):
        """Takes all the values with matching key in the database.

        Returns empty list when key doesn't have a match, intended
        to be used as boolean false."""

        t = (key,)
        values = self.c.execute('SELECT value FROM hashtable WHERE key = ?', t)\
            .fetchall()
        if values is not None:
            elements = (elem[0] for elem in values)
            return elements
        else:
            return []

    def close_connection(self):
        self.conn.commit()
        self.conn.close()
