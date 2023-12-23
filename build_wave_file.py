from wave import open as wave_open
from os.path import isfile

sound_dir = "wav"


def get_wave_file_list(wind_speed_avg, wind_speed_max, wind_heading):
    return [
        sound_dir + "/indi.mus.wav",
        sound_dir + "/w-aktuell.mus.wav",
        sound_dir + "/durchschnitt_kurz.mus.wav",
        sound_dir + "/r-" + deg_to_compass(wind_heading) + ".mus.wav",
        *get_wind_speed_files(wind_speed_avg),
        sound_dir + "/kmh.mus.wav",
        sound_dir + "/boe-kurz.mus.wav",
        *get_wind_speed_files(wind_speed_max),
        sound_dir + "/kmh.mus.wav",
        sound_dir + "/bye.mus.wav",
    ]


def get_wind_speed_files(value):
    value = round(value)
    files = []

    if value >= 100:
        file_name = "{}/{}.mus.wav".format(sound_dir, (value // 100) * 100)
        value %= 100
        if isfile(file_name):
            files.append(file_name)

        if value == 0:
            return files

    for i in range(value, 100):
        file_name = "wav/{}.mus.wav".format(i)
        if isfile(file_name):
            files.append(file_name)
            break

    return files


def deg_to_compass(deg):
    val = int((deg / 22.5) + .5)
    arr = ["n", "nno", "no", "ono", "o", "oso", "so", "sso", "s", "ssw", "sw", "wsw", "w", "wnw", "nw", "nnw"]
    return arr[(val % 16)]


def join_wave_files(input_files_list, output_file_path):
    files = []
    for infile in input_files_list:
        with wave_open(infile, 'rb') as reader:
            files.append([reader.getparams(), reader.readframes(reader.getnframes())])

    with wave_open(output_file_path, 'wb') as writer:
        writer.setparams(files[0][0])
        for i in range(len(files)):
            writer.writeframes(files[i][1])
