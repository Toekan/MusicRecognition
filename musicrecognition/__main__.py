"""
Usage:
 musicrecognition create <pathdirsong> <namedb> [--size=<number>]
 musicrecognition search <namedb>

Options:
 --size=<number>  Maximum number of songs added to db [default: 1000]
"""

import os, operator, time
import multiprocessing as mp
import matplotlib.pyplot as plt

from docopt import docopt

import create_musiclib as cm
import search_musiclib as sm
import sql_database.database as db
import record_audio.recording as rec
import plot_audio.plot_audio as plot

arguments = docopt(__doc__)

PATH_DATABASE = os.path.join(os.getcwd(), 'data', arguments['<namedb>'])
PATH_MUSICFOLDER = arguments['<pathdirsong>']
DATATYPES = ['.mp3', '.flac', '.wav', '.m4a']
MAX_SONGLENGTH = 10

WINDOWSIZE = 4096
HOPLENGTH = 2048
LOCALREGION = 60


if arguments['create']:

    with db.ContextDataBase(PATH_DATABASE, 'w') as connection_sql:
        counter = 0
        songid = 0 + counter
        for root, dir, files in os.walk(PATH_MUSICFOLDER):
            for file in files:
                songpath = os.path.join(root, file)

                songname = cm.file_utils.get_name_song(file)
                extension = cm.file_utils.get_filetype_song(file)

                if extension in DATATYPES:
                    songlength = cm.file_utils.get_length_song(songpath)
                    if songlength < MAX_SONGLENGTH:
                        # Process the song
                        song = cm.analyse_song.AnalyseSong(songpath, songid)
                        song.process_song()

                        # Add song to database
                        db.add_full_dictionary(connection_sql, song.database)
                        db.add_songid_to_songlist(connection_sql,
                                                  songid, songname)

                        counter += 1
                        songid += 1

            if counter >= int(arguments['--size']):
                break



if arguments['search']:
    MIN_RECORDING_TIME = 5
    MAX_RECORDING_TIME = 60
    MATCH_DIFFERENCE = 10


    with db.ContextDataBase(PATH_DATABASE, 'r') as connection_sql:
        constellation = sm.analyse_song.AnalyseSong(WINDOWSIZE,
                                                    HOPLENGTH, LOCALREGION)

        # Start recording process, sound is stored in an mp.queue
        print("*recording*")
        q = mp.Queue()
        p = mp.Process(target=rec.function_recording, args=(q,))
        p.start()

        cursor_sql = connection_sql.cursor()
        absolutetime = time.clock()

        # Start analysing sound by taking piece per piece out of the mp.queue
        while True:
            y = q.get(block=True, timeout=1)
            constellation.analyze_recording_piece(y, cursor_sql)

            if (time.clock() - absolutetime) > MIN_RECORDING_TIME:

                bestbinlist = sorted(constellation.best_song_match(),
                                     key=operator.itemgetter(1), reverse=True)
                differencebests = bestbinlist[0][1] - bestbinlist[1][1]

                if differencebests >= MATCH_DIFFERENCE:
                    p.terminate()
                    print("*finished recording*")
                    print("time taken: ", time.clock() - absolutetime)
                    print(db.get_song_from_id(connection_sql, bestbinlist[0][0]))
                    break

            if (time.clock() - absolutetime) > MAX_RECORDING_TIME:
                p.terminate()
                print("*finished recording*")
                print("Song not reliably found, potential options:")
                print(db.get_song_from_id(connection_sql, bestbinlist[0][0]))
                break

        # figuring out which points actually contributed to match
        constellation.matching_peaks()

        # plotting
        plot.print_specint(constellation.Stotal)
        plot.plot_constellation(constellation.constellation, constellation.Stotal)
        plt.show()

        plot.print_specint(constellation.Stotal)
        plot.plot_constellation(constellation.anchorpoints,constellation.Stotal)
        plt.show()