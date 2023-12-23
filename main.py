import time
from datetime import datetime
from pathlib import Path
from shutil import which
from signal import signal, SIGINT
from subprocess import run
from threading import Event

from requests import get

from build_wave_file import get_wave_file_list, join_wave_files


class Broadcaster:
    def __init__(self, station_id, query_delay=5):
        self.station_id = station_id
        self.minimum_delay = query_delay

    def _now_utc(self):
        return datetime.utcnow().timestamp()

    def broadcast(self, wind_data, play_command="play"):
        file_list = get_wave_file_list(wind_data["wind_speed_avg"], wind_data["wind_speed_max"],
                                       wind_data["wind_heading"])
        out_file = "combined.wav"
        join_wave_files(file_list, out_file)
        stdout = None
        play = which(play_command)
        if play is None:
            raise Exception("Could not find 'play' command. Please install 'sox' and make sure 'play' is in your path.")

        out = run(play + " " + out_file, shell=True, capture_output=True)
        Path.unlink(Path(out_file))
        return out, file_list

    def listen(self, sigint_handler_event: Event, max_iterations=None):
        last_record_date = self._now_utc() - 1
        first_run = True
        i = 0

        while not sigint_handler_event.is_set():
            i += 1
            now = self._now_utc()
            diff = now - last_record_date
            minimum_wait_time = round(9.98 * 60.0)

            if not first_run:
                wait_time = max(minimum_wait_time - round(diff), self.minimum_delay)
                print(f"Waiting {wait_time} seconds for next record")
                sigint_handler_event.wait(wait_time)

            first_run = False
            api_data = get('http://api.pioupiou.fr/v1/live/%s' % self.station_id).json()

            last_record_date = datetime.strptime(api_data["data"]['measurements']["date"],
                                                 "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            new_wind_data = api_data["data"]['measurements']

            print(f"{new_wind_data['date']} UTC: Avg {new_wind_data['wind_speed_avg']}, max {new_wind_data['wind_speed_max']}, "
                  f"heading {new_wind_data['wind_heading']}")

            self.broadcast(api_data["data"]['measurements'])

            last_date = last_record_date
            if max_iterations and i >= max_iterations:
                break



if __name__ == "__main__":
    waiter = Event()


    def sigint_handler(signum, frame):
        waiter.set()


    signal(SIGINT, sigint_handler)

    broadcaster = Broadcaster('1333')

    broadcaster.listen(sigint_handler_event=waiter)
