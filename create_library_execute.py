import time
import os
import matplotlib.pyplot as plt
import create_library_class as cl
import pickle

mp3files = []
for root, dirs, files in os.walk(r"C:\Users\Frederik\Dropbox\MUSIC"):
    for file in files:
        fullpath = os.path.join(root,file)
        if fullpath[-3:] == "mp3":
            mp3files.append(fullpath)
        else:
            pass


songid = 0
songlibrary = {}
print(time.clock())
for file in mp3files[:100]:
    metadata = os.stat(file)
    if metadata.st_size/10**6 < 25:
        print(file)
        a = time.clock()
        song = cl.CreateLibrary(file,songid)
        b = time.clock()
        song.create_spectograph()
        c = time.clock()
        song.take_peaks()
        song.create_targetzones()
        d = time.clock()
        song.add_to_sql()
        e = time.clock()
        print('Create instance:', b - a)
        print('Spectograph:', c - b)
        print('Targetzones:', d - c)
        print('Add to SQL:', e - d)
        songlibrary[songid] = file
        songid += 1
    else:
        print(metadata.st_size/10**6)

pickle.dump(songlibrary, open("Data/Songlibrary.p", "wb"))

cl.print_specint(song.S)
cl.plot_constellation(song.constellation,song.S)
plt.show()
