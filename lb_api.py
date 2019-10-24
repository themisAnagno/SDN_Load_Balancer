from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from flask_swagger_ui import get_swaggerui_blueprint

import logging
import threading
import json
import os
import atexit

import lb


# Create the logger
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
file_handler = logging.handlers.RotatingFileHandler(
    "logs/lb_app.log", maxBytes=10000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


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
    List of users currently on the WiFi Access Network
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
    List of users currently on the VLC Access network
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


class ServiceLogs(Resource):
    """
    Logs of the service. If no service is created, then returns the logs of the
    application
    """
    def get(self):
        """
        Returns the logs of the service if running or else the logs of the LB
        application
        """
        x = os.system("service lb status")
        if not x:
            os.system("journalctl -u lb.service -b -n 40> logs/lb.log")
            log_file = "lb.log"
        else:
            log_file = "lb_app.log"
        return send_from_directory("./logs/", log_file, as_attachment=True)


class Logs(Resource):
    """
    Logs of the load balancer application
    """
    def get(self):
        """
        Returns the logs of the load balancer application
        """
        log_file = "lb_app.log"
        return send_from_directory("./logs/", log_file, as_attachment=True)


def create_app():
    """
    Creates the Flask application and the Load Balancer thread
    """
    logger.info("IoRL Load Balancer Application starts")
    # Start the lb application
    api_thread.start()
    atexit.register(lambda: os.system("rm -f lb_app.log"))

    app = Flask(__name__)
    api = Api(app)

    # Define the endpoint routes
    api.add_resource(Users, '/api/users')
    api.add_resource(Params, '/api/parameters')
    api.add_resource(Vlcusers, '/api/vlcusers')
    api.add_resource(Wifiusers, '/api/wifiusers')
    api.add_resource(Logs, '/api/logs')
    api.add_resource(ServiceLogs, '/api/service_logs')
    # Register blueprint at URL
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    return app


if (__name__ == "__main__"):
    # Start the application
    app = create_app()
    app.run(host='0.0.0.0', port=8001)
