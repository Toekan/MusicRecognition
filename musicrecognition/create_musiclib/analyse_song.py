import numpy as np
import operator
from scipy import signal
import librosa

from . import matrixslider
import sql_database.database as db


class AnalyseSong:
    """All the methods needed to create datapoints of full songs,
    so used to create the library from my the tracks loaded in"""

    borders_ = [2, 10, 20, 40, 80, 160, 500]
    coeff_ = [2.2, 1.5, 1.5, 1.5, 1.5, 1]

    def __init__(self, filepath, songID):
        self.path = filepath
        self.songID = songID

        self.S = []
        self.constellation = []
        self.database = {}

    def process_song(self):
        self.create_spectograph()
        self.take_peaks()
        self.create_targetzones()

    def create_spectograph(self):
        """Loads the music file and returns abs(stft)"""

        # Important to use sr = None, the default forces it to 22050!
        y, sr = librosa.load(self.path, sr=None, mono=True)
        self.S = np.abs(librosa.stft(y, n_fft=4096, hop_length=2048,
                                     window=signal.hamming(4096)))

    def take_peaks(self):
        """Input is the absolute value of the spectrograph (as created in
        give_specint), creates a list of tuples (time, frequency)
        of all the peaks. This is the constellation map"""

        max_time = self.S.shape[1]
        values = np.zeros((6, max_time))
        freq = np.zeros((6, max_time))
        time = np.arange(max_time)

        for i in range(0, 6):
            values[i] = np.amax(self.S[AnalyseSong.borders_[i]:
                                    AnalyseSong.borders_[i+1]], axis=0)
            freq[i] = np.argmax(self.S[AnalyseSong.borders_[i]:
                                    AnalyseSong.borders_[i+1]], axis=0)

        for Ssub, pos in matrixslider.MatrixSlide(values, 60, 1):
            for i in range(0, 6):
                Ssubrow = Ssub[i]
                av = np.average(Ssubrow)
                std = np.std(Ssubrow)
                if values[i][pos] > av + AnalyseSong.coeff_[i]*std:
                    self.constellation.append((int(time[pos]),
                                int(freq[i][pos]) + AnalyseSong.borders_[i]))

        self.constellation = sorted(self.constellation,
                                    key=operator.itemgetter(0))

    def create_targetzones(self):
        """Creates all the anchor-point pairs and adds them to the database
        dictionary of the class instance.

        The anchorpoint and targetzone (of the peak points) are 3 points apart,
        this can be made higher or lower, influence to be investigated."""

        for i in range(0, len(self.constellation) - 9):
            anchor_t = int(self.constellation[i][0])
            anchor_f = int(self.constellation[i][1])
            for key in (int(str(anchor_f) + str(elem[1])
                        + str(int(elem[0] - anchor_t)))
                        for elem in self.constellation[i+3:i+8]):
                if key in self.database:
                    self.database[key].append(int(str(anchor_t) +
                                                  str(self.songID).zfill(5)))
                else:
                    self.database[key] = [int(str(anchor_t) +
                                              str(self.songID).zfill(5))]

    def add_to_sql(self, cursor):
        """Taking the whole database of this song and put it in the SQL
        database, using function of the sql_database package."""

        for key in self.database:
            db.add_values(cursor, key, self.database[key])