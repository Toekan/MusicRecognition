'''Module for making the constellation map. Contains take_peaks(S)
(which returns a list of (time,freq) tuples of all the peaks.
plot_constellation(constellation,S) creates a plot of the constellation points'''

import numpy as np
import operator
import pyfftw
import math
from collections import Counter
from collections import defaultdict


from sql_database import database as db


class AnalyseSong:
    """Class that contains the constellation map and the hash table as instance
    variables. Input is the part of the spectrograph that was newly recorded."""

    borders = [2, 10, 20, 40, 80, 160, 500]
    coeff = [2.2, 1.5, 1.5, 1.5, 1.5, 1]

    def __init__(self, windowsize, hoplength, localregion):
        """Initializes the instance. Windowsize is the windowsize of the FFT,
        so n_fft. Hoplength is the stepsize in the STFT. Localregion is the region
        around the time-point that is used to create the limits for creating
        the constellation map."""

        self.windowsize = windowsize
        self.hoplength = hoplength
        self.localregion = localregion

        self.y = pyfftw.empty_aligned(windowsize, dtype='complex64')
        self.window = np.array(list(AnalyseSong.hamming(n,self.windowsize)
                                    for n in range(self.windowsize)))
        self.y_withwindow = pyfftw.empty_aligned(windowsize, dtype='complex64')
        self.Ssingleline = pyfftw.empty_aligned(windowsize, dtype='complex64')
        self.fft_object = pyfftw.FFTW(self.y_withwindow, self.Ssingleline)
        self.y[:] = np.zeros(windowsize,dtype='complex64')
        self.y_withwindow[:] = np.zeros(windowsize,dtype='complex64')
        self.averaging_counter = 0

        self.new_points = 0

        self.values = -np.ones((6,localregion))
        self.freq = np.empty((6,localregion))
        self.pos = 0

        self.Stotal = []
        self.constellation = []
        self.valueerrors = []
        self.keys_list = []

        self.t_delta_hist = defaultdict(lambda: Counter())
        self.t_delta_hist_tracker = defaultdict(lambda: defaultdict(lambda: []))
        self.bestbinlist = []
        self.anchorpoints = []
        self.database = {}

    def analyze_recording_piece(self, y, cursor):
        """Put y as input, which should received through recording and have the right
         length (= hoplength). This method takes all the other ones to go from this
         recording to create constellation points and search through the database
         for matches."""
        if self.pos >= 1:
            self.fft(y)
            self.update_localregion()
            self.take_peaks()
            self.search_and_sort(cursor)
        else:
            self.preparefft(y)

    def preparefft(self,y):
        """Fills up the y far enough to do the first FFT, important when hoplength is
         not the same as the windowsize!"""
        if self.pos < int(self.windowsize/self.hoplength)-1:
            self.y[0:self.windowsize-self.hoplength] = self.y[self.hoplength:]
            self.y[self.windowsize-self.hoplength:] = y
            self.pos += 1

    def fft(self,y):
        """takes the recorded input (of length hop length!), shoves at the end of
        self.y, which has length windowsize, calculates the DFT (by pyfftw FFT),
        Stores it into the instance variable Ssingleline.
        Make sure it's a vertical vector."""

        self.y[0:self.windowsize-self.hoplength] = self.y[self.hoplength:]
        self.y[self.windowsize-self.hoplength:] = y

        #the pyfftw seems to lack a window function, so transforming it myself first
        #with a hamming function
        self.y_withwindow[:] = self.window * self.y
        self.Ssingleline = self.fft_object()
        self.Ssingleline = self.Ssingleline[:2049]

        if len(self.Stotal) > 0:
            self.Ssingleline = np.absolute(self.Ssingleline[:])
            self.Stotal = np.c_[self.Stotal,self.Ssingleline[:]]
        else:
            self.Stotal = np.absolute(self.Ssingleline[:])

    def update_localregion(self):
        """Ssub is the part of the spectrograph that is the environment of the line
        being analyzed, as to provide a reference for mean values and std.
        This Ssub is created here by deleting the first line and adding a line
        at the end."""

        self.values[:,0:self.localregion-1] = self.values[:,1:self.localregion]
        self.freq[:,0:self.localregion-1] = self.freq[:,1:self.localregion]

        for i in range(0,6):
            self.values[i,self.localregion-1] = np.amax(self.Ssingleline
                                                        [AnalyseSong.borders[i]:
                                                        AnalyseSong.borders[i+1]])
            self.freq[i,self.localregion-1] = np.argmax(self.Ssingleline
                                                        [AnalyseSong.borders[i]:
                                                        AnalyseSong.borders[i+1]])

        self.pos += 1

    def take_peaks(self):
        """Input is the absolute value of the spectrograph (as created in
        give_specint), creates a list of tuples (time, frequency) of all the peaks.
        This is the constellation map"""

        time = self.pos - self.localregion/2 - 1
        subconstellation = []

        for i in range(0,6):
            av = np.average(self.values[i][max((0,self.localregion-self.pos)):])
            std = np.std(self.values[i][max((0,self.localregion-self.pos)):])

            if self.values[i][self.localregion/2] > av + AnalyseSong.coeff[i]*std:
                subconstellation.append((int(time),int(self.freq[i][self.localregion/2])
                                         + AnalyseSong.borders[i]))

        self.constellation.extend(subconstellation)
        self.new_points = len(subconstellation)

    def search_and_sort(self, cursor):
        """Taking every newly created point in the last frame, making the key for it,
         searching the library, and adding everything in the right [SongID][delta_t]
         bin of the histograms."""

        for i in range(len(self.constellation)-self.new_points,len(self.constellation)):
            pointt = int(self.constellation[i][0])
            pointf = int(self.constellation[i][1])
            for key,anchort,anchorf in ((int(str(elem[1])+str(pointf)+str(pointt-elem[0])),elem[0],elem[1])
                        for elem in self.constellation[i-8:i-3]):
                self.keys_list.append(key)
                values = db.get_values(cursor, key)
                if values:
                    for value in values:
                        try:
                            time_anchor_abs,songID = int(str(value)[:-5]),int(str(value)[-5:])
                            t_delta = time_anchor_abs - pointt
                            self.t_delta_hist[songID][t_delta] += 1
                            self.t_delta_hist_tracker[songID][t_delta]\
                                            .extend([(anchort,anchorf),(pointt,pointf)])
                        except ValueError:
                            self.valueerrors.append(value)

    def best_song_match(self):
        """goes through the t_delta_hist and finds the best bin for each song, the
        correct song should have one bin that is considerably higher than all the
        other bins of all other songs."""

        self.bestbinlist = []
        for songID in self.t_delta_hist:
            bestbintuple = max(self.t_delta_hist[songID].items(), key=operator.itemgetter(1))
            bestbint,bestbinvalue = bestbintuple[0],bestbintuple[1]
            bestbin = 0
            for i in range(bestbint-2,bestbint+3):
                bestbin += self.t_delta_hist[songID][i]

            self.bestbinlist.append((songID,bestbin))

        return self.bestbinlist

    @staticmethod
    def hamming(n,N):
        alpha = 0.54
        beta = 0.46
        return alpha - beta*math.cos(2*math.pi*n/(N-1))

    def matching_peaks(self):
        """After the matching song (correct or wrong) has been found, this method
        checks which target points actually contributed to the match. This way we can
         try to improve the accuracy of the program.

        Input:      Takes the list of the anchorpoint - elementpoint duos
        Output:     All the peak points that were part of a matching duo
                    within the time coherency calculated in best_match_song"""
        bestbinlist_final = sorted(self.bestbinlist, key=operator.itemgetter(1), reverse=True)
        songID = bestbinlist_final[0][0]
        bestbintuple = max(self.t_delta_hist[songID].items(), key=operator.itemgetter(1))
        bestbint, bestbinvalue = bestbintuple[0], bestbintuple[1]

        for i in range(bestbint - 2, bestbint + 3):
            if i in self.t_delta_hist_tracker[songID]:
                self.anchorpoints.extend(self.t_delta_hist_tracker[songID][i])