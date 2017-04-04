import matplotlib.pyplot as plt
import numpy as np
import operator
from scipy import signal

import librosa
import database as db

class CreateLibrary:
    '''All the methods needed to create datapoints of full songs, so used to create the library from
        my the tracks loaded in'''


    borders = [2,10,20,40,80,160,500]
    coeff = [2.2,1.5,1.5,1.5,1.5,1]

    def __init__(self,filepath,songID):
        self.path = filepath
        self.songID = songID

        self.S = []
        self.constellation = []
        self.database = {}

        self.sql = db.SetDataBase('Data/shazamdb.db')

    def create_spectograph(self):
        """Loads the music file and returns abs(stft)"""

        #Important to use sr = None, the default forces it to 22050!
        y,sr = librosa.load(self.path,sr = None, mono= True)
        self.S = np.abs(librosa.stft(y,n_fft=4096,hop_length=2048,window=signal.hamming(4096)))


    def take_peaks(self):
        """Input is the absolute value of the spectrograph (as created in give_specint),
        creates a list of tuples (time, frequency) of all the peaks. This is the constellation map"""

        max_time = self.S.shape[1]
        values = np.zeros((6,max_time))
        freq = np.zeros((6,max_time))
        time = np.arange(max_time)

        for i in range(0,6):
            values[i] = np.amax(self.S[CreateLibrary.borders[i]:CreateLibrary.borders[i+1]],axis=0)
            freq[i] = np.argmax(self.S[CreateLibrary.borders[i]:CreateLibrary.borders[i+1]],axis=0)

        for Ssub,pos in MatrixSlide(values,60,1):
            for i in range(0,6):
                Ssubsub = Ssub[i]
                av = np.average(Ssubsub)
                std = np.std(Ssubsub)
                if values[i][pos] > av + CreateLibrary.coeff[i]*std:
                    self.constellation.append((int(time[pos]),int(freq[i][pos])+CreateLibrary.borders[i]))

        self.constellation = sorted(self.constellation, key = operator.itemgetter(0))


    def create_targetzones(self):
        """adds points to the database instead of searching it. This function is to add songs to the database!"""

        for i in range(0, len(self.constellation) - 9):
            anchor_t = int(self.constellation[i][0])
            anchor_f = int(self.constellation[i][1])
            for key in (int(str(anchor_f) + str(elem[1])+str(int(elem[0] - anchor_t)))
                                for elem in self.constellation[i+3:i+8]):
                if key in self.database:
                    self.database[key].append(int(str(anchor_t)+str(self.songID).zfill(5)))
                else:
                    self.database[key] = [int(str(anchor_t)+str(self.songID).zfill(5))]

    def add_to_sql(self):
        """Taking the whole database of this song and put it in the SQL database, using the object of the
        SetDataBase class."""
        for key in self.database:
            self.sql.add_value(key,self.database[key])

        self.sql.close_connection()


def print_specint(S):
    '''Takes the spectrograph (absolute values already), takes the log of S^2 and plots it on a log scale'''
    logamp = librosa.logamplitude(S**2)
    plt.figure()
    librosa.display.specshow(logamp, sr=44100,hop_length=2048, y_axis='log',x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Log-frequency power spectrogram')


def plot_constellation(constellation,S):
    '''prints the constellation map'''
    y_map, y_inv_map = librosa.display.__log_scale(S.shape[0])
    x = [f[0] for f in constellation]
    y = [f[1] for f in constellation]
    plt.scatter(x,y_map[y])


class MatrixSlide:
    '''slides over a matrix in a predefined stepsize, takes S as input, returns Ssub for every step of the iterator and
    the position pos, where the middle of Ssub is on S. So (Ssub,pos)'''

    def __init__(self,S,width,stepsize):
        self.S = S
        self.width = width
        self.stepsize = stepsize

    def __iter__(self):
        self.pos = 0
        return self


    def __next__(self):
        if self.pos == self.S.shape[1]:
            raise StopIteration

        Ssub = self.S[:,max(self.pos-self.width/2,0):min(self.pos+self.width/2,self.S.shape[1])]
        pos = self.pos
        self.pos += self.stepsize
        return Ssub,pos