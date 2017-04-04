import time
import pickle
import operator
import matplotlib.pyplot as plt
import warnings
import multiprocessing as mp

import search_library_class as sl
import recording as rec
warnings.filterwarnings("ignore")

def f(conn):
    recordinst = rec.Recording()
    while True:
        y = recordinst.record()
        conn.put(y)




if __name__ == '__main__':
    #Importing the list of songs with their IDnumbers
    songlibrary = pickle.load(open("songlibrary.p", "rb"))

    #Waiting for user input to start recording
    a = input("Press enter to start, any other key to abort:")
    if len(list(a)) == 0:
        startrecording = True
    else:
        startrecording = False

    while startrecording:
        constellation = sl.Constellation(4096,2048,60)
        timer = 0
        outlier = False
        absolutetime = time.clock()

        #First a fixed length of recording to start
        seconds = 10
        print("*recording*")
        q = mp.Queue()
        p = mp.Process(target=f, args=(q,))
        p.start()
        jaja = time.clock()
        while timer < 44100*seconds:
            y = q.get()
            constellation.analyze_recording_piece(y)
            timer += 2048

        haha = time.clock()

        #Now a part that keeps on going until the threshold is met, looking for an outlier in
        #terms of having a time bin with a lot of hits

        while outlier is False:
            y = q.get(block=True,timeout=1)
            constellation.analyze_recording_piece(y)
            constellation.search_and_sort()

            bestbinlist = sorted(constellation.best_song_match(),
                                 key = operator.itemgetter(1), reverse = True)
            bestbinmean = sum((elem[1] for elem in bestbinlist))/len(bestbinlist)
            differencebests = bestbinlist[0][1] - bestbinlist[1][1]

            if differencebests >= 10:
                outlier = True
                p.terminate()

                print("*finished recording*")
                print("time taken: ",time.clock() - absolutetime)
                #print("Songs with best bin", bestbinlist)
                print("Correct song:", songlibrary[bestbinlist[0][0]],bestbinlist[0][1])
                print("2nd song:", songlibrary[bestbinlist[1][0]],bestbinlist[1][1])
                print("3rd song:", songlibrary[bestbinlist[2][0]])
                print("4th song:", songlibrary[bestbinlist[3][0]])
                print("5th song:", songlibrary[bestbinlist[4][0]])

            if time.clock() - absolutetime > 60:
                outlier = True
                p.terminate()

                print("*finished recording*")
                print("Song not reliably found, potential options:")
                print(songlibrary[bestbinlist[0][0]],bestbinlist[0][1])
                print(songlibrary[bestbinlist[1][0]],bestbinlist[1][1])
                print(songlibrary[bestbinlist[2][0]])
                print(songlibrary[bestbinlist[3][0]])
                print(songlibrary[bestbinlist[4][0]])
                #print("Songs with best bin", bestbinlist)


        print('Amount of points:',len(constellation.constellation))
        #print('Tavg SELECT sql:',sum(constellation.sql.timer1)/len(constellation.sql.timer1))
        #print('Tavg sort:',sum(constellation.sql.timer2)/len(constellation.sql.timer2))
        #print('value errors:',constellation.valueerrors)
        #print(sorted(constellation.t_delta_hist[bestbinlist[0][0]].items(),key = operator.itemgetter(1),reverse = True))
        #print(sorted(constellation.t_delta_hist[bestbinlist[1][0]].items(),key = operator.itemgetter(1),reverse = True))
        #print(sorted(constellation.t_delta_hist[bestbinlist[2][0]].items(),key = operator.itemgetter(1),reverse = True))
        #print(sorted(constellation.t_delta_hist[bestbinlist[3][0]].items(),key = operator.itemgetter(1),reverse = True))
        #print(sorted(constellation.t_delta_hist[bestbinlist[4][0]].items(),key = operator.itemgetter(1),reverse = True))
        constellation.sql.close_connection()


        #print(sum(constellation.sql.timer1)/len(constellation.sql.timer1))

        #with open('test.txt', mode = 'a') as a_file:
        #    for i in range(0,5):
        #        blabla = bestbinlist[i][1]
        #        a_file.write(songlibrary[bestbinlist[i][0]]+': '+str(blabla))
        #        a_file.write('\n')
        #    a_file.write('\n')

        #figuring out which points actually contributed to match
        constellation.matching_peaks()

        #plotting
        sl.print_specint(constellation.Stotal)
        sl.plot_constellation(constellation.constellation, constellation.Stotal)
        plt.show()

        sl.print_specint(constellation.Stotal)
        sl.plot_constellation(constellation.anchorpoints,constellation.Stotal)
        plt.show()

        a = input("Press enter to start, any other key to abort:")
        if len(list(a)) == 0:
            startrecording = True
        else:
            startrecording = False