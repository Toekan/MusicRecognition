import re
import subprocess
import os

re_filetype = re.compile('[.]\w+$')

def get_filetype(songpath):
    """Returns the extension (including .) of the filename"""
    return re_filetype.search(songpath).group()


def get_length_song(songpath):
    """Returns the length of the song in minutes (rounded down)"""
    process = subprocess.Popen(['ffmpeg', '-i', songpath],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    matches = re.search(
        (r"Duration:\s{1}(?P<hours>\d+?):"
         r"(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),"),
        str(stdout), re.DOTALL).groupdict()
    return int(matches['minutes'])


def create_songlist(path_musicfolder, datatypes = ['.mp3','.flac','.wav','.m4a'],
                    max_length_song = 10):
    """Creates a generator to iterate through the directory and subdirectories
    to find all audio files (of the chosen datatypes) with a maximum length
    of max_length_song (in minutes)"""
    for root, dirs, files in os.walk(path_musicfolder):
        for songname in files:
            try:
                songpath = os.path.join(root, songname)
                if (get_filetype(songpath) in datatypes) & \
                        (get_length_song(songpath) < max_length_song):
                    yield songpath, songname
            except AttributeError:
                pass