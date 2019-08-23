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
    'has_dataset': fields.Boolean(required=True, description='The model weights')
})

metric = api.model(name='Metric', model={
    'mse': fields.Float(required=True, description='The model mse')
})

data_owner = DataOwnerService()


@api.route('', endpoint='training_resources_ep')
class TrainingResources(Resource):

    @api.doc('Initialize new model with existing dataset')
    @api.marshal_with(link, code=201)
    def post(self):
        data = request.get_json()
        training_id = data['model_id']
        reqs = data['requirements']
        # TODO: For now i'm creating the training and linking the dataset to the training all at once
        # TODO: and doing it in the back, but a future change will be to do those in separate API calls.
        model_id, do_id, has_dataset = data_owner.link_model_to_dataset(training_id, data['model_type'], reqs)
        return {'model_id': model_id, 'data_owner_id': do_id, 'has_dataset': has_dataset}


@api.route('/<model_id>', endpoint='training_resource_ep')
class TrainingResource(Resource):

    @api.doc('Get gradient updated')
    @api.marshal_with(update, code=200)
    def post(self, model_id):
        """
        Process weights from server
        :return:
        """
        logging.info('Process weights')
        data = request.get_json()
        gradients = data_owner.process(model_id, data['weights'])
        return {'data_owner_id': data_owner.get_id(), 'update': gradients}

    @api.doc('Update local model with gradient')
    def put(self, model_id):
        """
        Execute step with gradient
        :return:
        """
        data = request.get_json()
        logging.info('Gradient step')
        data_owner.step(model_id, data['gradient'])
        return 200


@api.route('/<model_id>/metrics', endpoint='metrics_resource_ep')
class MetricsResource(Resource):

    @api.doc('Generate a new metric that measures the quality of a model')
    @api.marshal_with(metric, code=201)
    def post(self, model_id):
        data = request.get_json()
        model_type = data["model_type"]
        weights = data["model"]
        mse = data_owner.model_quality_metrics(model_id, model_type, weights)
        return {'mse': mse}
