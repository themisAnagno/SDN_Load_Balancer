from flask import Flask, request
from flask_restful import Resource, Api
from flask_swagger_ui import get_swaggerui_blueprint

import logging
import threading
import json

import lb


# Create the logger
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
stream_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


# Create the swagger
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Test application"})


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
        Add users to the list of the registered users oF the IoRL Platform
        """
        new_users = request.get_json()
        lb.users += new_users["users"]
        return {"Message": "User list changed succesfully",
                "New Users": lb.users}, 201

    def put(self):
        """
        Create the list of the registered users oF the IoRL Platform
        """
        new_users = request.get_json()
        lb.users = new_users["users"]
        return {"Message": "User list changed succesfully",
                "New Users": lb.users}, 201

    def delete(self):
        """
        Deletes the given users form the registered users list. If no users
        provided, it will delete the whole list
        """
        remove_users = request.get_json()
        if not remove_users:
            lb.users = []
        else:
            old_users = list(lb.users)
            lb.users = [user for user in old_users if user not in remove_users["users"]]
        return {"Message": "User list changed succesfully",
                "New Users": lb.users}, 201


class Params(Resource):
    """
    The resource that contains the operational parameters of the Load Balancer
    """
    def get(self):
        """
        Returns the operational parameters of the Load Balancer
        """
        return lb.init_param, 200

    def put(self):
        """
        Creates/Updates the operational parameters of the Load Balancer if the
        Load Balancer is not started
        """
        global api_thread, thread_counter

        new_param = request.get_json()
        lb.init_param = request.get_json()
        if not api_thread.is_alive():
            with open("init_config.json", "w") as param_file:
                json.dump(new_param, param_file)

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
        if api_thread.is_alive():
            wifi_users_list = lb.get_wifi_users()
            return {"WiFi Users": wifi_users_list}, 200
        else:
            return {"Message": "The LB application is not running"}, 400


class Vlcusers(Resource):
    """
    Returns the list of users that are currently on the VLC
    """
    def get(self):
        """
        Returns the list of users on the VLC
        """
        if api_thread.is_alive():
            wifi_users_list = lb.get_wifi_users()
            vlc_users_list = lb.get_vlc_users(wifi_users_list)
            return {"VLC Users": vlc_users_list}, 200
        else:
            return {"Message": "The LB application is not running"}, 400


def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Define the endpoint routes
    api.add_resource(Users, '/api/users')
    api.add_resource(Params, '/api/parameters')
    api.add_resource(Vlcusers, '/api/vlcusers')
    api.add_resource(Wifiusers, '/api/wifiusers')
    # Register blueprint at URL
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    # Start the application
    app.run(host='0.0.0.0', port=8001)


if (__name__ == "__main__"):
    logger.info("IoRL Load Balancer Application starts")
    # Start the lb application
    api_thread.start()
    create_app()
