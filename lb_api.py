from flask import Flask, request
from flask_restplus import Resource, Api

import logging
import threading

import lb


# Create the logger
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
stream_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

# Define global variables
thread_counter = 1
api_thread = threading.Thread(target=lb.run_lb, args=(thread_counter,),
                              daemon=True)


class Users(Resource):
    """
    The resource that contains the rules that have been applied by the load
    balancer
    """
    def get(self):
        """
        Returns the list of the registered users oF the IoRL Platform
        """
        return lb.users, 200

    def post(self):
        """
        Create the list of the registered users oF the IoRL Platform
        """
        new_users = request.get_json()
        lb.users = new_users["users"]
        return {"Message": "User list changed succesfully",
                "New Users": new_users}, 201


class Params(Resource):
    """
    The resource that contains the operational parameters of the Load Balancer
    """
    def get(self):
        """
        Returns the operational parameters of the Load Balancer
        """
        return lb.init_param, 200

    def post(self):
        """
        Creates/Updates the operational parameters of the Load Balancer if the
        Load Balancer is not started
        """
        global api_thread, thread_counter

        new_param = request.get_json()
        lb.init_param = request.get_json()
        if not api_thread.is_alive():
            thread_counter += 1
            api_thread = threading.Thread(target=lb.run_lb,
                                          args=(thread_counter,),
                                          daemon=True)
            api_thread.start()
        return {"Message": "Operational changed succesfully",
                "New Parameters": new_param}, 201


class Wifiusers(Resource):
    """
    Returns the list of users that are currently  on the WiFi
    """
    def get(self):
        """
        Returns the list of users on the WiFi
        """
        wifi_users_list = lb.get_wifi_users()
        return {"WiFi Users": wifi_users_list}, 200


class Vlcusers(Resource):
    """
    Returns the list of users that are currently on the VLC
    """
    def get(self):
        """
        Returns the list of users on the VLC
        """
        wifi_users_list = lb.get_wifi_users()
        vlc_users_list = lb.get_vlc_users(wifi_users_list)
        return {"VLC Users": vlc_users_list}, 200


def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Define the endpoint routes
    api.add_resource(Users, '/api/users')
    api.add_resource(Params, '/api/parameters')
    api.add_resource(Vlcusers, '/api/vlcusers')
    api.add_resource(Wifiusers, '/api/wifiusers')
    # Start the application
    app.run(host='0.0.0.0', port=8001)


if (__name__ == "__main__"):
    logger.info("IoRL Load Balancer Application starts")
    # Start the lb application
    api_thread.start()
    create_app()
