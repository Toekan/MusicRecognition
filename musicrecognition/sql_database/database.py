import sqlite3


def add_values(cursor, key, values):
    """Adding key-value pairs to the database, one key has a variable
    length list of values."""

    for value in values:
        cursor.execute('INSERT INTO hashtable VALUES(?,?)', (key, value))


def get_values(cursor, key):
    """Takes all the values with matching key in the database.

    Returns empty list when key doesn't have a match, intended
    to be used as boolean false."""

    t = (key,)
    values = cursor.execute('SELECT value FROM hashtable WHERE key = ?', t)\
        .fetchall()
    if values is not None:
        elements = (elem[0] for elem in values)
        return elements
    else:
        return []


class ContextDataBase:
    """Context manager for the database. Returns a cursor to be used
    within the with statement.

    mode = r: reading the database
    mode = w: writing into the database
                If the database didn't exist before, create a table
                with a key and value column.

                If the database existed before, drop INDEX value_dict, as
                adding to the database is faster without INDEX.

                When the mode was write, the INDEX value_dict is created at
                __exit__, as it didn't exist yet or was dropped."""

    def __init__(self, path, mode='r'):
        self.path = path
        self.mode = mode
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()

    def __enter__(self):
        """Enter method returns a cursor after modifying the database,
        depending on the mode chosen."""

        if self.mode == 'r':
            return self.conn
        if self.mode == 'w':
            try:
                # Creating the hashtable and (songID, songname) table
                self.c.execute(('CREATE TABLE songlist '
                               '(songID INTEGER, songname TEXT)'))
                self.c.execute(('CREATE TABLE hashtable '
                                '(key INTEGER,  value INTEGER)'))
                return self.conn
            except sqlite3.OperationalError:
                # Throws an error if the tables already existed,
                # so writing onto an existing library, aka adding extra songs
                self.c.execute('DROP INDEX value_dict')
                return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """An INDEX is created at end of context if the mode w was chosen.
        Not needed in case of r as the INDEX already exists."""

        if self.mode == 'w':
            self.c.execute('CREATE INDEX value_dict ON hashtable (key)')
        self.conn.commit()
        self.conn.close()




