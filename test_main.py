import unittest

from main import Broadcaster


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
