from datetime import datetime
from os import getenv
from pathlib import Path
from shutil import which
from subprocess import run
from threading import Event
from requests import get
from build_wave_file import get_wave_file_list, join_wave_files


class PlayError(Exception):
    pass


class Broadcaster:
    def __init__(self, station_id, query_delay=3):
        self.station_id = station_id
        self.minimum_delay = query_delay

    def _now_utc(self):
        return datetime.utcnow().timestamp()

    def broadcast(self, wind_data, play_command="play -q"):
        file_list = get_wave_file_list(wind_data["wind_speed_avg"], wind_data["wind_speed_max"],
                                       wind_data["wind_heading"])
        out_file = "combined.wav"
        join_wave_files(file_list, out_file)
        command_parts = play_command.split(" ")
        command_path = which(command_parts[0])
        if command_path is None:
            raise FileNotFoundError(f"Could not find command {command_parts[0]}")

        command = f"{command_path} {' '.join(command_parts[1:])} {out_file}"

        print(f"{command} ... ", end="", flush=True)
        out = run(command, shell=True, capture_output=True, check=False)
        if out.returncode != 0:
            raise PlayError(f"Play command returned {out.returncode}: {out.stderr}")
        print("done.", flush=True)
        Path.unlink(Path(out_file))
        return out, file_list

    def listen(self, sigint_handler_event: Event, max_iterations=None, estimated_wait_time=10.0 * 60.0 + 4.0):
        last_record_date = self._now_utc() - 1
        first_run = True
        i = 0

        report = None

        while not sigint_handler_event.is_set():
            i += 1
            if max_iterations and i > max_iterations:
                break
            diff = self._now_utc() - last_record_date

            if not first_run:
                wait_time = max(estimated_wait_time - round(diff), self.minimum_delay)
                print(f"Waiting {wait_time} seconds before next query", flush=True)
                sigint_handler_event.wait(float(wait_time))

            url = f'http://api.pioupiou.fr/v1/live/{self.station_id}'
            response = get(url=url,
                           headers={
                               "user_agent": getenv("USER_AGENT",
                                                    f"windbird2radio broadcast service for station {self.station_id}")},
                           timeout=10)

            try:
                assert response is not None, "No response from API"
                assert response.status_code == 200, f"HTTP error {response.status_code}: {response.text}"
                api_data = response.json()
                self.check_sanity(api_data)

            except AssertionError as e:
                print(f"Error: {e}. Retrying in 10 minutes.", flush=True)
                sigint_handler_event.wait(estimated_wait_time)
                continue

            if not first_run and self._get_timestamp(api_data) <= last_record_date:
                continue

            new_wind_data = api_data["data"]['measurements']

            report = f"{new_wind_data['date']} UTC: " \
                     f"Avg {new_wind_data['wind_speed_avg']}, " \
                     f"max {new_wind_data['wind_speed_max']}, " \
                     f"heading {new_wind_data['wind_heading']}"
            print(
                report,
                flush=True
            )

            self.broadcast(api_data["data"]['measurements'])
            last_record_date = self._get_timestamp(api_data)
            first_run = False

        return report

    def _get_timestamp(self, api_data):
        utc_dt = datetime.strptime(
            api_data["data"]['measurements']["date"],
            "%Y-%m-%dT%H:%M:%S.%fZ")
        return (utc_dt - datetime(1970, 1, 1)).total_seconds()

    def check_sanity(self, api_data):
        assert api_data is not None, "No response from API"
        assert api_data["data"]['status']['state'] is not None, "Unknown station status"
        assert api_data["data"]['status']['state'] == "on", "Station is offline"

        assert api_data["data"]['measurements']["wind_speed_avg"] is not None, "No wind speed avg data"
        assert api_data["data"]['measurements']["wind_speed_max"] is not None, "No wind speed max data"
        assert api_data["data"]['measurements']["wind_heading"] is not None, "No wind heading data"

        assert int(api_data["data"]['measurements']["wind_speed_avg"]) < 399, "Wind speed avg invalid"
        assert int(api_data["data"]['measurements']["wind_speed_max"]) < 399, "Wind speed max invalud"
        assert int(api_data["data"]['measurements']["wind_heading"]) <= 360, "Invalid wind heading"
