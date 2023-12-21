import os.path
import signal
from datetime import datetime, timedelta
from subprocess import run
from pathlib import Path
from threading import Event

from requests import get

from build_wave_file import get_wave_file_list, join_wave_files

waiter = Event()


def sigint_handler(signum, frame):
    print("SIGINT received. Exiting...")
    waiter.set()


signal.signal(signal.SIGINT, sigint_handler)


def get_api_response(url):
    return get(url).json()


def broadcast(wind_data):
    file_list = get_wave_file_list(wind_data["wind_speed_avg"], wind_data["wind_speed_max"], wind_data["wind_heading"])

    out_file = "combined.wav"
    join_wave_files(file_list, out_file)

    play_binary = "/usr/bin/play"

    if not os.path.isfile(play_binary):
        play_binary = "/opt/homebrew/bin/play"
        if not os.path.isfile(play_binary):
            print("No player found. Exiting...")
            return

    run(play_binary + " " + out_file, shell=True)
    Path.unlink(Path(out_file))

# TODO auto offset
time_offset = 0.0

last_date = datetime.now().timestamp() - 1 - time_offset
first_run = True
delay = 5


while not waiter.is_set():
    now = datetime.now().timestamp()
    diff = now - last_date
    minimum_wait_time = 9.9*60.0

    if not first_run and diff < minimum_wait_time:
        wait_time = minimum_wait_time - diff
        print(f"Waiting {wait_time} seconds...")
        waiter.wait(wait_time)
        continue

    api_data = get_api_response('http://api.pioupiou.fr/v1/live/1333')

    date = datetime.strptime(api_data["data"]['measurements']["date"],
                             "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() + time_offset

    if not first_run and date <= last_date:
        last_date_age = datetime.now().timestamp() - last_date
        print(".", end="")
        first_run = False
        waiter.wait(delay)
        continue

    first_run = False
    new_wind_data = api_data["data"]['measurements']

    print(new_wind_data)
    broadcast(api_data["data"]['measurements'])

    last_date = date
    waiter.wait(delay)
