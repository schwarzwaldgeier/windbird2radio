from wave import open as wave_open
from os.path import isfile

SOUND_DIR = "wav"


def get_wave_file_list(wind_speed_avg, wind_speed_max, wind_heading):
    return [
        SOUND_DIR + "/indi.mus.wav",
        SOUND_DIR + "/w-aktuell.mus.wav",
        SOUND_DIR + "/durchschnitt_kurz.mus.wav",
        SOUND_DIR + "/r-" + deg_to_compass(wind_heading) + ".mus.wav",
        *get_wind_speed_files(wind_speed_avg),
        SOUND_DIR + "/kmh.mus.wav",
        SOUND_DIR + "/boe-kurz.mus.wav",
        *get_wind_speed_files(wind_speed_max),
        SOUND_DIR + "/kmh.mus.wav",
        SOUND_DIR + "/bye.mus.wav",
    ]


def get_wind_speed_files(value):
    value = round(value)
    files = []

    if value >= 100:
        file_name = f"{SOUND_DIR}/{(value // 100) * 100}.mus.wav"
        value %= 100
        if isfile(file_name):
            files.append(file_name)

        if value == 0:
            return files

    for i in range(value, 100):
        file_name = f"wav/{i}.mus.wav"
        if isfile(file_name):
            files.append(file_name)
            break

    return files


def deg_to_compass(deg):
    val = int((deg / 22.5) + .5)
    arr = ["n", "nno", "no",
           "ono", "o", "oso",
           "so", "sso", "s", "ssw", "sw",
           "wsw", "w", "wnw",
           "nw", "nnw"]
    return arr[(val % 16)]


def join_wave_files(input_files_list, output_file_path):
    files = []
    for infile in input_files_list:
        with wave_open(infile, 'rb') as reader:
            # pylint: disable=no-member
            files.append([reader.getparams(), reader.readframes(reader.getnframes())])

    with wave_open(output_file_path, 'wb') as writer:
        # pylint: disable=no-member
        writer.setparams(files[0][0])
        for file_data in files:
            writer.writeframes(file_data[1])
