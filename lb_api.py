from flask import Flask, request
from flask_restful import Resource, Api
import logging


# Create the logger
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
stream_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

users = []


class Users(Resource):
    """
    The resource that contains the rules that have been applied by the load
    balancer
    """
    def get(self):
        return users, 200

    def post(self):
        new_users = request.get_json()
        logger.debug(new_users)
        users.append(new_users)
        return "New users added succesfully", 201


def create_app():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Users, '/api/users')
    app.run(host='0.0.0.0', port=8001)
