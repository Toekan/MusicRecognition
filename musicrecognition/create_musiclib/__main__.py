from . import create_library_class as cl
from . import file_utils
from musicrecognition.sql_database import database as db


PATH_DATABASE = (r'C:\Users\Frederik\Documents\PythonScripts'
                '\MusicRecognition\Data\shazamdb.db')
PATH_MUSICFOLDER = r"C:\Users\Frederik\Dropbox\MUSIC"
DATATYPES = ['.mp3','.flac','.wav','.m4a']

n = 5

with db.ContextDataBase(PATH_DATABASE, 'w') as connection:

    for songid, (songpath, songname) in zip(range(n),
                                file_utils.create_songlist(PATH_MUSICFOLDER)):

        print(songname)
        
        # Create a dictionary of the fingerpoints of this song
        song = cl.CreateLibrary(songpath, songid)
        song.process_song()

        # Add the fingerpoints to the SQL database table hashtable and
        # the songid with songname to the SQL database table songlist.
        cursor = connection.cursor()
        song.add_to_sql(cursor)
        cursor.execute('INSERT INTO songlist VALUES(?,?)', (songid, songname))
        connection.commit()


print('finished')
