# musicrecognition

A real-time music recognition program written in Python based on the following publication:

http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.217.8882

## Usage:

Uses the following packages:

- Librosa: https://github.com/librosa/librosa
- pyaudio: https://people.csail.mit.edu/hubert/pyaudio/
- pyfftw: https://github.com/hgomersall/pyFFTW
- docopt: https://github.com/docopt/docopt

Command line interface:

'''
Usage:
 musicrecognition create <pathdirsong> <namedb> [--size=<number>]
 musicrecognition search <namedb>

Options:
 --size=<number>  Maximum number of songs added to db [default: 1000]
'''
