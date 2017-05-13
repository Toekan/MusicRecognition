import librosa
import matplotlib.pyplot as plt

def print_specint(S):
    """Takes the spectrograph (absolute values already),
    takes the log of S^2 and plots it on a log scale"""
    logamp = librosa.logamplitude(S**2)
    plt.figure()
    librosa.display.specshow(logamp, sr=44100,hop_length=2048,
                             y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Log-frequency power spectrogram')


def plot_constellation(constellation,S):
    """prints the constellation map"""
    y_map, y_inv_map = librosa.display.__log_scale(S.shape[0])
    x = [f[0] for f in constellation]
    y = [f[1] for f in constellation]
    plt.scatter(x, y_map[y])