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
api_thread = threading.Thread(target=lb.run_lb, args=(1,), daemon=True)


class Users(Resource):
    """
    The resource that contains the rules that have been applied by the load
    balancer
    """
    def get(self):
        global users

        return users, 200

    def post(self):

        new_users = request.get_json()
        logger.debug(new_users)
        lb.users = new_users["users"]
        return "New users added succesfully", 201


def create_app():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Users, '/api/users')
    app.run(host='0.0.0.0', port=8001)


if (__name__ == "__main__"):
    logger.info("IoRL Load Balancer Application starts")
    # Start the lb application
    api_thread.start()
    create_app()
