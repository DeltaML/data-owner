import logging

from flask_restplus import Resource, Namespace, fields
from flask import request

from data_owner.resources.models_resource import model
from data_owner.services.user_service import UserService

api = Namespace('users', description='Users related operations')


user_google_token_req = api.model(name='UserGoogleLogin', model={
    'token': fields.String(required=True, description='Google login token')
})


user_register_req = api.model(name='UserRegister', model={
    'address': fields.String(required=True, description='User register request')
})


user_register_data = api.model(name='UserRequest', model={
    'name': fields.String(required=True, description='The user name'),
    'email': fields.String(required=True, description='The user email'),
    'token': fields.String(required=True, description='The user token'),
    'address': fields.String(required=True, description='The user ethereum address')
})

user_data = api.model(name='UserResponse', model={
    'id': fields.String(required=True, description='The user identifier'),
    'external_id': fields.String(required=True, description='External user id. From external service'),
    'delta_id': fields.String(required=True, description='Delta id. From delta ml context'),
    'name': fields.String(required=True, description='The user name'),
    'email': fields.String(required=True, description='The user email'),
    'token': fields.String(required=True, description='The user token'),
    'address': fields.String(required=True, description='The user ethereum address'),
    'models': fields.Nested(model, required=False, description='The user models')
})


user_basic_data = api.model(name='UserReducedResponse', model={
    'id': fields.String(required=True, description='The user identifier'),
    'external_id': fields.String(required=True, description='External user id. From external service'),
    'delta_id': fields.String(required=True, description='Delta id. From delta ml context'),
    'name': fields.String(required=True, description='The user name'),
    'email': fields.String(required=True, description='The user email'),
    'token': fields.String(required=True, description='The user token')#,
    #'address': fields.String(required=True, description='The user ethereum address')
})


@api.route('', endpoint='users_resources_ep')
class UserResources(Resource):

    @api.expect(user_register_data)
    @api.marshal_with(user_basic_data, code=201)
    @api.doc('Create new user')
    def post(self):
        data = request.get_json()
        logging.info("Creating new user {}".format(data))

        return UserService().create(data), 201

    @api.marshal_list_with(user_data)
    def get(self):
        return UserService().get_all(), 200


@api.route('/<user_id>', endpoint='user_ep')
@api.response(404, 'User not found')
@api.param('user_id', 'The user identifier')
class UserResource(Resource):

    @api.doc('Update user')
    @api.expect(user_data)
    @api.marshal_with(user_data)
    def put(self, user_id):
        logging.info("Update user {}".format(user_id))
        data = request.get_json()
        return UserService().update(user_id, data), 200

    @api.doc('get_user')
    @api.marshal_with(user_data)
    def get(self, user_id):
        logging.info("Get user {}".format(user_id))
        return UserService().get(user_id), 200

    @api.doc('delete_user')
    def delete(self, user_id):
        logging.info("Delete user {}".format(user_id))
        return UserService().delete(user_id), 200


@api.route('/login', endpoint='users_login_resources_ep')
class UserLoginResources(Resource):

    @api.expect(user_google_token_req)
    @api.marshal_with(user_data, code=201)
    @api.doc('Login user')
    def post(self):
        logging.info("Login user")
        data = request.get_json()
        response = UserService().login(data)
        logging.info(response)
        return response, 200


@api.route('/<user_id>/register', endpoint='users_register_resources_ep')
class UserAddressResources(Resource):

    @api.expect(user_register_req)
    @api.marshal_with(user_basic_data, code=201)
    @api.doc('Register user in federated aggregator')
    def post(self, user_id):
        data = request.get_json()
        logging.info("Register user with data {}".format(data))
        response = UserService().register(user_id, data)
        logging.info(response)
        return response, 200
