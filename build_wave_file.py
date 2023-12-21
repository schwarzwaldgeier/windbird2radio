import wave
from os.path import isfile


def get_wave_file_list(wind_speed_avg, wind_speed_max, wind_heading):
    avg_wind_files = get_wind_speed_files(wind_speed_avg)
    max_wind_files = get_wind_speed_files(wind_speed_max)

    files = [
        "wav/indi.mus.wav",
        "wav/w-aktuell.mus.wav",
        "wav/durchschnitt_kurz.mus.wav",
        "wav/r-" + deg_to_compass(wind_heading) + ".mus.wav",
        *avg_wind_files,
        "wav/kmh.mus.wav",
        "wav/boe-kurz.mus.wav",
        *max_wind_files,
        "wav/kmh.mus.wav",
        "wav/bye.mus.wav",
    ]
    return files


def get_wind_speed_files(wind_speed):
    wind_speed = round(wind_speed)
    files = []

    if wind_speed >= 100:
        file_name = "wav/{}.mus.wav".format((wind_speed // 100) * 100)
        wind_speed %= 100
        if isfile(file_name):
            files.append(file_name)

        # avoid "hundert null kmh"
        if wind_speed == 0:
            return files

    for i in range(wind_speed, 100):
        file_name = "wav/{}.mus.wav".format(i)
        if isfile(file_name):
            files.append(file_name)
            break

    return files


def deg_to_compass(num):
    val = int((num / 22.5) + .5)
    arr = ["n", "nno", "no", "ono", "o", "oso", "so", "sso", "s", "ssw", "sw", "wsw", "w", "wnw", "nw", "nnw"]
    return arr[(val % 16)]


def join_wave_files(input_files, output_file):
    data = []
    for infile in input_files:
        w = wave.open(infile, 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()

    output = wave.open(output_file, 'wb')
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()
