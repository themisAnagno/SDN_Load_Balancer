import requests
import time
import logging
import json
import random

from rules import to_wifi, from_wifi


# Create the logger
logger = logging.getLogger(__name__)
file_handler = logging.handlers.RotatingFileHandler(
    "/lb_app.log", maxBytes=10000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Define global vars
users = []
init_param = {}
stop = False


def run_lb(name):
    """
    Starts the Load Balancer application
    """
    global init_param, stop

    # Read the initial config parameters
    with open('init_config.json') as init_config:
        init_param = json.load(init_config)

    # Check if all the values are not null
    for param, value in init_param.items():
        if not value:
            logger.warning(f"Null initial value for -> {param} <- \nWaiting to get initial/parameters via API")
            logger.info(f"Load Balancer on thread {name} stops")
            return

    # Initialize the traffic variable
    response = requests.get(url=f"http://{init_param['ryu_ip']}:8080/stats/\
port/{init_param['br-int_dpid']}/{init_param['vlc_of_port']}")
    traffic = response.json()[init_param['br-int_dpid']][0]["tx_bytes"]

    # Start the lb iteration
    while not stop:
        response = requests.get(url=f"http://{init_param['ryu_ip']}:8080/\
stats/port/{init_param['br-int_dpid']}/{init_param['vlc_of_port']}")
        new_traffic = response.json()[init_param['br-int_dpid']][0]["tx_bytes"]
        # Calculate Mbps
        bytes_per_sec = (new_traffic - traffic)/init_param["interval"]
        Mbytes_per_sec = bytes_per_sec/1000000
        bitrate = Mbytes_per_sec * 8
        logger.info("The bitrate is {0:.2f} Mbps".format(bitrate))
        if bitrate > init_param["upper_bw_limit"]:
            logger.info(f"The bitrate is over upper bw limit")
            wifi_list = get_wifi_users()
            vlc_users = get_vlc_users(wifi_list)
            if len(vlc_users) == 0:
                logger.warning("There are not registered users to go to the WiFi network")
            else:
                chosen_user_index = random.randint(0, len(vlc_users)-1)
                chosen_user = vlc_users[chosen_user_index]
                logger.info(f"User {chosen_user} will be transfered to WiFi")
                # Add rule for incoming traffic
                data = json.dumps(to_wifi(init_param, chosen_user))
                headers = {"Content-Type": "application/json"}
                requests.post(url=f"http://{init_param['ryu_ip']}:8080/stats/flowentry/add", data=data, headers=headers)
                # Add rule for outgoing traffic
                data = json.dumps(from_wifi(init_param, chosen_user))
                headers = {"Content-Type": "application/json"}
                requests.post(url=f"http://{init_param['ryu_ip']}:8080/stats/flowentry/add", data=data, headers=headers)
        elif bitrate < init_param["lower_bw_limit"]:
            logger.info(f"The bitrate is under lower bw limit")
            wifi_list = get_wifi_users()
            if len(wifi_list) == 0:
                logger.warning("There are not users on the WiFi network")
            else:
                chosen_wifi_user_index = random.randint(0, len(wifi_list)-1)
                chosen_wifi_user = wifi_list[chosen_wifi_user_index]
                chosen_user = [user for user in users if user["vlc_ip"] == chosen_wifi_user]
                if len(chosen_user) > 0:
                    logger.info(f"User {chosen_user[0]} will be transfered back to VLC")
                    # Delete rule for ingoing traffic
                    data = json.dumps(to_wifi(init_param, chosen_user[0]))
                    headers = {"Content-Type": "application/json"}
                    requests.post(url=f"http://{init_param['ryu_ip']}:8080/stats/flowentry/delete_strict", data=data, headers=headers)
                    # Delete rule for outgoing traffic
                    data = json.dumps(from_wifi(init_param, chosen_user[0]))
                    headers = {"Content-Type": "application/json"}
                    requests.post(url=f"http://{init_param['ryu_ip']}:8080/stats/flowentry/delete_strict", data=data, headers=headers)

        traffic = new_traffic
        time.sleep(init_param["interval"])

    logger.info(f"Load Balancer on thread {name} stops")


def get_wifi_users():
    """
    Gets the IP of the users currently on the WiFi
    """
    response = requests.get(url=f"http://{init_param['ryu_ip']}:8080/\
stats/flow/{init_param['br-int_dpid']}")
    rules = response.json()[init_param['br-int_dpid']]
    wifi_users = []
    for rule in rules:
        try:
            vlc_ip = rule["match"]["nw_dst"]
        except KeyError:
            continue
        else:
            wifi_users.append(vlc_ip)
    return wifi_users


def get_vlc_users(wifi_list):
    """
    Returns the list of the users that are currently on the VLC/mmWave
    """
    vlc_users = [user for user in users if user["vlc_ip"] not in wifi_list]
    return vlc_users
