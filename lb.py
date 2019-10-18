import requests
import time
import threading
import logging

import lb_api


# Create the logger
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
stream_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

logger.info("IoRL Load Balancer Application starts")

# Create the flask app for implementing APIs
api_thread = threading.Thread(target=lb_api.create_app, args=(), daemon=True)
api_thread.start()


def run_lb():
    """
    Starts the Load Balancer application
    """

    # Initialize the traffic variable
    response = requests.get(url="http://10.100.128.2:8080/stats/port/\
                                182816038959173/2")
    traffic = response.json()["182816038959173"][0]["rx_bytes"]
    while True:
        response = requests.get(url="http://10.100.128.2:8080/stats/port/\
                                182816038959173/2")
        new_traffic = response.json()["182816038959173"][0]["rx_bytes"]
        # Calculate Mbps
        bytes_per_sec = (new_traffic - traffic)/10
        Mbytes_per_sec = bytes_per_sec/1000000
        bitrate = Mbytes_per_sec * 8
        if bitrate > 50:
            logger.debug(f"The bitrate is over the thresehold ({bitrate})")
        traffic = new_traffic
        time.sleep(10)


if (__name__ == "__main__"):
    run_lb()
