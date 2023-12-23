from os import remove
from os.path import isfile

import build_wave_file as bwf


class TestBuildWaveFile:
    def test_get_wave_file_list_some(self):
        for windspeed in range(0, 3):
            for windheading in range(0, 3):
                for windmax in range(0, 4):
                    files = bwf.get_wave_file_list(windspeed, windmax, windheading)
                    for file in files:
                        assert isfile(file)

    def test_get_wave_file_list_over_hundred_windspeed(self):
        windspeed = 170
        windheading = 0
        windmax = 202
        files = bwf.get_wave_file_list(windspeed, windmax, windheading)
        for file in files:
            assert isfile(file)

        assert files[4] == "wav/100.mus.wav"
        assert files[5] == "wav/70.mus.wav"
        assert files[8] == "wav/200.mus.wav"
        assert files[9] == "wav/2.mus.wav"

    def test_get_wind_speed_files(self):
        for speed in range(0, 400):
            file_names = bwf.get_wind_speed_files(speed)
            assert file_names
            assert isfile(file_names[0])

    def test_deg_to_compass(self):
        deg = 90
        compass = bwf.deg_to_compass(deg)
        assert compass == "o"

        deg = 180
        compass = bwf.deg_to_compass(deg)
        assert compass == "s"

        deg = 180.123456
        compass = bwf.deg_to_compass(deg)
        assert compass == "s"

        deg = 270
        compass = bwf.deg_to_compass(deg)
        assert compass == "w"

        for deg in range(0, 360):
            compass = bwf.deg_to_compass(deg)
            assert compass in ["n", "nno", "no", "ono", "o", "oso", "so", "sso", "s", "ssw", "sw", "wsw", "w", "wnw",
                               "nw", "nnw"]

    def test_join_wave_files(self):
        input_files = bwf.get_wave_file_list(23, 54, 90)
        output_file = "temp/test.wav"
        bwf.join_wave_files(input_files, output_file)
        assert isfile(output_file)
        remove(output_file)
