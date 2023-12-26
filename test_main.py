import unittest
from os import environ
from unittest.mock import patch, Mock

from main import get_sigint_handler, get_config, main


class TestMain(unittest.TestCase):

    @patch('main.get_sigint_handler')
    @patch('main.get_config')
    @patch('main.Broadcaster')
    def test_main(self, mock_broadcaster, mock_get_config, mock_get_sigint_handler):
        mock_sigint_handler = Mock()
        mock_get_sigint_handler.return_value = mock_sigint_handler
        mock_config = {'station_id': 'test_station_id', 'user_agent': 'test_user_agent'}
        mock_get_config.return_value = mock_config

        main()

        mock_get_sigint_handler.assert_called_once()
        mock_get_config.assert_called_once()
        mock_broadcaster.assert_called_once_with('test_station_id')
        mock_broadcaster_instance = mock_broadcaster.return_value
        mock_broadcaster_instance.listen.assert_called_once_with(sigint_handler_event=mock_sigint_handler)

    def test_sigint_handler(self):
        handler = get_sigint_handler()
        assert not handler.is_set()
        handler.set()
        assert handler.is_set()

    def test_get_config(self):
        test_id = 'test_station_id'
        environ['STATION_ID'] = test_id
        conf = get_config()
        assert conf.get('station_id') == test_id
