import pyaudio
from struct import *


def function_recording(conn):
    """Function that keeps the recording instance going and puts
    the blocks (of hoplength) in the multiprocessing queue.
    Input: multiprocessing Queue"""
    recordinst = Recording()
    while True:
        y = recordinst.record()
        conn.put(y)

class Recording:
    """Class used to record music from the microphone"""

    def __init__(self, hoplength = 2048):
        self.CHUNK = hoplength
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        RATE = 44100

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=FORMAT,
                            channels=CHANNELS,
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