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
    def __init__(self, station_id, query_delay=3):
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

        if play_command == "play":
            play += " -q"

        command = play + " " + out_file
        print(f"{command} ... ", end="", flush=True)
        out = run(command, shell=True, capture_output=True)
        if out.returncode != 0:
            raise Exception(f"Could not play file {out_file}: {out.stderr.decode('utf-8')}")
        print("done.", flush=True)
        Path.unlink(Path(out_file))
        return out, file_list

    def listen(self, sigint_handler_event: Event, max_iterations=None):
        last_record_date = self._now_utc() - 1
        first_run = True
        i = 0

        while not sigint_handler_event.is_set():
            i += 1
            diff = self._now_utc() - last_record_date
            estimated_wait_time = round(10.0 * 60.0 + 4.0)

            if not first_run:
                wait_time = max(estimated_wait_time - round(diff), self.minimum_delay)
                print(f"Waiting {wait_time} seconds before next query", flush=True)
                sigint_handler_event.wait(float(wait_time))

            api_data = get('http://api.pioupiou.fr/v1/live/%s' % self.station_id).json()

            new_record_date = datetime.strptime(
                api_data["data"]['measurements']["date"],
                "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()

            if not first_run and new_record_date <= last_record_date:
                continue

            new_wind_data = api_data["data"]['measurements']

            print(
                f"{new_wind_data['date']} UTC: "
                f"Avg {new_wind_data['wind_speed_avg']}, "
                f"max {new_wind_data['wind_speed_max']}, "
                f"heading {new_wind_data['wind_heading']}",
                flush=True
            )

            self.broadcast(api_data["data"]['measurements'])
            last_record_date = new_record_date

            first_run = False

            if max_iterations and i >= max_iterations:
                break


if __name__ == "__main__":
    waiter = Event()


    def sigint_handler(signum, frame):
        waiter.set()


    signal(SIGINT, sigint_handler)

    broadcaster = Broadcaster('1333')

    broadcaster.listen(sigint_handler_event=waiter)
