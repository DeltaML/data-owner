import logging

from flask_restplus import Resource, Namespace, fields
from flask import request
from data_owner.services.data_owner_service import DataOwnerService

api = Namespace('trainings', description='Training related operations')

features = api.model(name='Features', model={
    'list': fields.List(fields.String, required=True, description='The model type'),
    'range': fields.List(fields.Integer, required=True, description='The model type'),
    'pre_processing': fields.List(fields.Raw, required=False, description='The model type'),
    'desc': fields.Raw(required=False, description='The model type')
})

target = api.model(name='Target', model={
    'range': fields.List(fields.Integer, required=True, description='The model type'),
    'desc': fields.List(fields.String, required=True, description='The model type')
})

data_requirements = api.model(name='Data Requirements', model={
    'features': fields.Nested(features, required=True, description='The model type'),
    'target': fields.Nested(target, required=True, description='The model type'),
})

requirements = api.model(name='Requirements', model={
    'model_type': fields.String(required=True, description='The model type'),
    'testing_file_name': fields.String(required=True, description='The name of the file to test'),
    'data_requirements': fields.Nested(data_requirements, required=True, description='Data requirements')
})
model = api.model(name='Model', model={
    'id': fields.String(required=True, description='The model identifier'),
    'status': fields.String(required=True, description='The model status'),
    'type': fields.String(required=True, description='The model type'),
    'weights': fields.List(fields.Raw, required=True, description='The model weights')
})

update = api.model(name='Update', model={
    'data_owner_id': fields.String(required=True, description='The model identifier'),
    'update': fields.List(fields.Raw, required=True, description='The model weights')
})

link = api.model(name='Link', model={
    'model_id': fields.String(required=True, description='The model identifier'),
    'data_owner_id': fields.String(required=True, description='The model identifier'),
    'linked': fields.Boolean(required=True, description='The model weights')
})

metric = api.model(name='Metric', model={
    'diff': fields.List(fields.Raw, required=True, description='The difference between y and y_pred')
})

features = api.model(name='Features', model={
    'list': fields.List(fields.String, required=True, description='The model type'),
    'range': fields.List(fields.Integer, required=True, description='The model type'),
    'pre_processing': fields.List(fields.Raw, required=False, description='The model type'),
    'desc': fields.Raw(required=False, description='The model type')
})

target = api.model(name='Target', model={
    'range': fields.List(fields.Integer, required=True, description='The model type'),
    'desc': fields.List(fields.String, required=True, description='The model type')
})

data_requirements = api.model(name='Data Requirements', model={
    'features': fields.Nested(features, required=True, description='The model type'),
    'target': fields.Nested(target, required=True, description='The model type'),
})

data_metadata = api.model(name='Requirements', model={
    'data_requirements': fields.Nested(data_requirements, required=True, description='Data requirements'),
    'status': fields.String(required=True, description='The model training status'),
    'model_id': fields.String(required=True, description='The model id'),
    'model_type': fields.String(required=True, description='The model type'),
    'model_buyer_id': fields.String(required=True, description='The model buyer id'),
    'weights': fields.List(fields.Raw, required=True, description='The model weights')
})

data_owner = DataOwnerService()


@api.route('', endpoint='training_resources_ep')
class TrainingResources(Resource):

    @api.doc('Save new training request')
    @api.expect(data_metadata)
    def post(self):
        data = request.get_json()
        training_id = data['model_id']
        reqs = data['requirements']
        data_owner.init_model(training_id, data['model_type'], reqs)


@api.route('/<model_id>', endpoint='training_resource_ep')
class TrainingResource(Resource):

    @api.doc('Get if data owner is training the model')
    @api.marshal_with(link, code=201)
    def get(self, model_id):
        return {'model_id': model_id, 'data_owner_id': data_owner.get_id(), 'linked': data_owner.model_is_linked(model_id)}

    @api.doc('Get gradient updated')
    @api.marshal_with(update, code=200)
    def post(self, model_id):
        """
        Process weights from server
        :return:
        """
        logging.info('Process weights')
        data = request.get_json()
        gradients = data_owner.process(model_id, data['weights'], data['public_key'])
        return {'data_owner_id': data_owner.get_id(), 'update': gradients}

    @api.doc('Update local model with gradient')
    def put(self, model_id):
        """
        Execute step with gradient
        :return:
        """
        data = request.get_json()
        logging.info('Gradient step')
        data_owner.step(model_id, data['gradient'], data['public_key'])
        return 200

    @api.doc('Finishes the local training or validation')
    def patch(self, model_id):
        data = request.get_json()
        logging.info("Finishing training in data owner")
        contribs = data['contribs']['contributions']
        improvement = data['contribs']['improvement']
        data_owner.finish_training(model_id, contribs, improvement)
        return 200


@api.route('/<model_id>/metrics', endpoint='metrics_resource_ep')
class MetricsResource(Resource):

    @api.doc('Generate a new vector which is the difference between y_test and y_pred')
    @api.marshal_with(metric, code=201)
    def post(self, model_id):
        data = request.get_json()
        diff = data_owner.model_quality_metrics(model_id, data["model"], data["public_key"], data["model_type"])
        return {'diff': diff}

    def put(self, model_id):
        data = request.get_json()
        data_owner.update_mse(model_id, data['mse'], data['role'])
        return 200


@api.route('/<model_id>/accept', endpoint='accept_training_resource_ep')
class MetricsResource(Resource):

    @api.doc('Initialize new model with existing dataset')
    @api.marshal_with(link, code=200)
    def put(self, model_id):
        data = request.get_json()
        model_id, do_id, has_dataset = data_owner.link_model_to_dataset(model_id)
        return {'linked': has_dataset}
