import pyaudio
from struct import *


class Recording:
    '''Class used to record music from the microphone'''

    def __init__(self):
        self.CHUNK = 2048
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        RATE = 44100

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=FORMAT,
                            channels = CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK)

    def record(self):
        data = self.stream.read(self.CHUNK)
        data = unpack(str(self.CHUNK)+"f",data)
        return data

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()





