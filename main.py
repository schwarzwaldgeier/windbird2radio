from multiprocessing import Event
from os import getenv
from signal import signal, SIGINT
from dotenv import load_dotenv
from broadcaster import Broadcaster


def get_sigint_handler():
    waiter = Event()

    def sigint_handler(signum, frame):
        print(f"Received signal {signum} in frame {frame}")
        waiter.set()

    signal(SIGINT, sigint_handler)
    return waiter


def get_config():
    conf = {}
    load_dotenv(".env.local")
    load_dotenv(".env")
    conf["station_id"] = getenv("STATION_ID")
    conf["user_agent"] = getenv("USER_AGENT")
    return conf


def main():
    sigint_handler = get_sigint_handler()
    config = get_config()
    assert config.get('station_id'), "Please set STATION_ID in .env file"

    broadcaster = Broadcaster(config.get('station_id'))
    broadcaster.listen(sigint_handler_event=sigint_handler)


if __name__ == "__main__":
    main()
