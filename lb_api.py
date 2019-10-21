from flask import Flask, request
from flask_restful import Resource, Api

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
        logger.debug(new_users)
        lb.users = new_users["users"]
        return {"Message": "User list changed succesfully"}, 201


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
        logger.debug(new_param)
        if not api_thread.is_alive():
            thread_counter += 1
            api_thread = threading.Thread(target=lb.run_lb,
                                          args=(thread_counter,),
                                          daemon=True)
            api_thread.start()
            # lb.stop = True
            # thread_counter += 1
            # api_thread = threading.Thread(target=lb.run_lb,
            #                               args=(thread_counter),
            #                               daemon=True)
            # api_thread.start()
        return {"Message": "Operational changed succesfully"}, 201


def create_app():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Users, '/api/users')
    api.add_resource(Params, '/api/parameters')
    app.run(host='0.0.0.0', port=8001)


if (__name__ == "__main__"):
    logger.info("IoRL Load Balancer Application starts")
    # Start the lb application
    api_thread.start()
    create_app()
