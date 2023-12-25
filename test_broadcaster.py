import json
import unittest
from multiprocessing import Event
from time import sleep
from unittest.mock import patch, MagicMock

from broadcaster import Broadcaster


class TestBroadcaster(unittest.TestCase):
    mock_data = {
        "doc": "http://developers.pioupiou.fr/api/live/",
        "license": "http://developers.pioupiou.fr/data-licensing",
        "attribution": "(c) contributors of the Pioupiou wind network <http://pioupiou.fr>",
        "data": {
            "id": 1333,
            "meta": {
                "name": "Wetterstation Schwarzwaldgeier"
            },
            "location": {
                "latitude": 48.764463,
                "longitude": 8.280487,
                "date": "2023-12-22T10:31:55.000Z",
                "success": "true",
                "hdop": 1
            },
            "measurements": {
                "date": "2023-12-23T12:41:07.000Z",
                "pressure": "null",
                "wind_heading": 225,
                "wind_speed_avg": 72.5,
                "wind_speed_max": 99,
                "wind_speed_min": 47
            },
            "status": {
                "date": "2023-12-23T12:41:07.000Z",
                "snr": -1,
                "state": "on"
            }
        }
    }

    def test_broadcast(self):
        broadcaster = Broadcaster('test_station')
        out, file_list = broadcaster.broadcast(self.mock_data["data"]["measurements"], "file")
        assert out
        assert "WAVE audio" in str(out.stdout)
        assert file_list

        assert file_list == ['wav/indi.mus.wav',
                             'wav/w-aktuell.mus.wav',
                             'wav/durchschnitt_kurz.mus.wav',
                             'wav/r-sw.mus.wav',
                             'wav/72.mus.wav',
                             'wav/kmh.mus.wav',
                             'wav/boe-kurz.mus.wav',
                             'wav/99.mus.wav',
                             'wav/kmh.mus.wav',
                             'wav/bye.mus.wav']

    def test_no_play_command_raises_exception(self):
        broadcaster = Broadcaster('test_station')
        with self.assertRaises(Exception):
            broadcaster.broadcast(
                self.mock_data["data"]["measurements"],
                "windows_media_player_mock_fake_edition")

    def test_play_exit_code_not_zero_raises_exception(self):
        broadcaster = Broadcaster('test_station')
        with self.assertRaises(Exception):
            broadcaster.broadcast(
                self.mock_data["data"]["measurements"],
                "play -q --non-existing-option")

    def test_check_sanity(self):
        broadcaster = Broadcaster('test_station')
        broadcaster.check_sanity(self.mock_data)

        insane_mock_data = self.mock_data.copy()
        insane_mock_data["data"]["measurements"]["wind_speed_avg"] = 9000
        with self.assertRaises(Exception):
            broadcaster.check_sanity(insane_mock_data)

        insane_mock_data = self.mock_data.copy()
        insane_mock_data["data"]["measurements"]["wind_speed_max"] = 9000
        with self.assertRaises(Exception):
            broadcaster.check_sanity(insane_mock_data)

        insane_mock_data = self.mock_data.copy()
        insane_mock_data["data"]["measurements"]["wind_heading"] = 9000
        with self.assertRaises(Exception):
            broadcaster.check_sanity(insane_mock_data)

        insane_mock_data = self.mock_data.copy()
        insane_mock_data["data"]["status"]["state"] = "off"
        with self.assertRaises(Exception):
            broadcaster.check_sanity(insane_mock_data)

        insane_mock_data = self.mock_data.copy()
        insane_mock_data["data"] = b"0000"
        with self.assertRaises(Exception):
            broadcaster.check_sanity(insane_mock_data)

        insane_mock_data = self.mock_data.copy()
        insane_mock_data["data"] = None
        with self.assertRaises(Exception):
            broadcaster.check_sanity(insane_mock_data)

    def test_now_utc(self):
        broadcaster = Broadcaster('test_station')
        now = broadcaster._now_utc()
        sleep(0.0000001)
        now2 = broadcaster._now_utc()
        assert now < now2

    @patch('broadcaster.Broadcaster.broadcast')
    @patch('broadcaster.get')
    @patch('broadcaster.Broadcaster.check_sanity')
    @patch('broadcaster.Broadcaster._get_timestamp')
    def test_listen(self, mock_get_timestamp, mock_check_sanity, mock_get, mock_broadcast):
        broadcaster = Broadcaster('1333')

        mock_broadcast.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(self.mock_data).encode('utf-8')

        mock_get.return_value = mock_response

        mock_check_sanity.return_value = None

        mock_get_timestamp.return_value = 1234567890
        broadcaster.minimum_delay = 0.0

        broadcasted = broadcaster.listen(sigint_handler_event=Event(), max_iterations=2, estimated_wait_time=0.0)
        assert "Avg" in broadcasted
        assert "max" in broadcasted
        assert "heading" in broadcasted

        mock_check_sanity.side_effect = AssertionError
        broadcasted = broadcaster.listen(sigint_handler_event=Event(), max_iterations=2, estimated_wait_time=0.0)
        assert broadcasted is None

    def test_get_timestamp(self):
        broadcaster = Broadcaster('test_station')
        timestamp = broadcaster._get_timestamp(self.mock_data)
        assert timestamp == 1703331667.0
