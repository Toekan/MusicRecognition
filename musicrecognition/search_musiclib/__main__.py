import operator
import warnings
import time
import multiprocessing as mp
import matplotlib.pyplot as plt

from musicrecognition.sql_database import database as db
from . import search_library_class as sl
import musicrecognition.record_audio as rec

warnings.filterwarnings("ignore")


PATH_DATABASE = (r'C:\Users\Frederik\Documents\PythonScripts'
                '\MusicRecognition\Data\shazamdb.db')
MIN_RECORDING_TIME = 10
MAX_RECORDING_TIME = 60


def f(conn):
    recordinst = rec.Recording()
    while True:
        y = recordinst.record()
        conn.put(y)


def is_start_program():
    # Waiting for user input to start recording
    a = input("Press enter to start, any other key to abort:")
    if len(list(a)) == 0:
        return True
    else:
        return False


if __name__ == '__main__':

    startrecording = is_start_program()

    while startrecording:
        with db.ContextDataBase(PATH_DATABASE, 'r') as connection_sql:
            constellation = sl.Constellation(4096, 2048, 60)

            absolutetime = time.clock()

            # First a fixed length of recording to start
            print("*recording*")
            q = mp.Queue()
            p = mp.Process(target=f, args=(q,))
            p.start()
            cursor_sql = connection_sql.cursor()

            for _ in range(stop=44100*MIN_RECORDING_TIME, step=2048):
                constellation.analyze_recording_piece(q.get(), cursor_sql)

            # Now a part that keeps on going until the threshold is met,
            # looking for an outlier in
            # terms of having a time bin with a lot of hits

            outlier = False
            while outlier is False:
                y = q.get(block=True, timeout=1)
                constellation.analyze_recording_piece(y, cursor_sql)

                bestbinlist = sorted(constellation.best_song_match(),
                                     key = operator.itemgetter(1), reverse = True)
                differencebests = bestbinlist[0][1] - bestbinlist[1][1]

                if differencebests >= 10:
                    outlier = True
                    p.terminate()

                    print("*finished recording*")
                    print("time taken: ",time.clock() - absolutetime)


                if time.clock() - absolutetime > MAX_RECORDING_TIME:
                    outlier = True
                    p.terminate()

                    print("*finished recording*")
                    print("Song not reliably found, potential options:")


        print('Amount of points:',len(constellation.constellation))


        # figuring out which points actually contributed to match
        constellation.matching_peaks()

        # plotting
        sl.print_specint(constellation.Stotal)
        sl.plot_constellation(constellation.constellation, constellation.Stotal)
        plt.show()

        sl.print_specint(constellation.Stotal)
        sl.plot_constellation(constellation.anchorpoints,constellation.Stotal)
        plt.show()

        startrecording = is_start_program()