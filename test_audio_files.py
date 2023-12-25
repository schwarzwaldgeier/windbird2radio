import wave
from os import listdir
from os.path import isfile, join


def test_audio_files_are_radio_compatible():
    files = [f for f in listdir("wav") if isfile(join("wav", f)) and f.endswith(".wav")]
    for file in files:
        try:
            with wave.open(join("wav", file), 'rb') as reader:
                nchannels, sampwidth, framerate, nframes = reader.getparams()[:4]
                assert nchannels == 1, f"File {file} has {nchannels} channels, expected 1"
                assert sampwidth == 2, f"File {file} has {sampwidth} sample width, expected 2"
                assert framerate == 44100, f"File {file} has {framerate} frame rate, expected 44100"
                assert nframes > 0, f"File {file} has {nframes} frames, expected more than 0"
        except wave.Error as e:
            print(f"Error checking {file}: {e}")
            raise e
