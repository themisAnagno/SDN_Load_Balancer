from flask import Flask, request
from flask_restful import Resource, Api


rules = [{
    'name': 'My Store',
    'items': [{'name': 'my item', 'price': 15.99}]
}]


class Rules(Resource):
	"""
	The resource that contains the rules that have been applied by the load balancer
	"""
	def get(self):
		return rules, 200


def create_app():
    app = Flask(__name__)
    api = Api(app)
    
    api.add_resource(Rules, '/api/rules')
    app.run(host='0.0.0.0', port=8001)
