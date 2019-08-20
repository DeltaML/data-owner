import logging
import json
from flask_restplus import Resource, Namespace, fields
from flask import request
from commons.model.model_service import ModelFactory
from data_owner.services.data_owner_service import DataOwnerService
from data_owner.models.model import Model
from data_owner.models.dataset import Dataset
from commons.data.data_loader import DataLoader

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

data_owner = DataOwnerService()


@api.route('', endpoint='training_resources_ep')
class TrainingResources(Resource):

    @api.doc('Create new user')
    @api.marshal_with(link, code=201)
    def post(self):
        data = request.get_json()
        training_id = data['model_id']
        reqs = data['requirements']
        # TODO: For now i'm creating the training and linking the dataset to the training all at once
        # TODO: and doing it in the back, but a future change will be to do those in separate API calls.
        filename = DataLoader().get_dataset_for_training(reqs)
        if filename is not None:
            DataLoader().load_data(filename)
            dataset = DataLoader().get_sub_set()
            model = Model(training_id, data['model_type'], dataset)
            model.save()
        return {'model_id': training_id, 'data_owner_id': DataOwnerService().get_id(), 'has_dataset': filename is not None}


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
        model_orm = Model.get(model_id)
        print(data['weights'])
        model, response = data_owner.process(model_orm.model, data['weights'])
        model_orm.model = model
        model_orm.update()
        return {'data_owner_id': data_owner.get_id(), 'update': response}

    @api.doc('Update local model with gradient')
    def put(self, model_id):
        """
        Execute step with gradient
        :return:
        """
        data = request.get_json()
        logging.info('Gradient step')
        model_orm = Model.get(model_id)
        data_owner.step(model_orm.model, data['gradient'])
        model_orm.update()
        return 200


#@api.route('/<model_id>', endpoint='training_ep')
#@api.response(404, 'Training not found')
#@api.param('model_id', 'The model identifier')
#class TrainingResource(Resource):

#    @api.doc('put_model')
#    #@api.marshal_with(updated_model)
#    def put(self, model_id):
#        data = request.get_json()
#        training_id = data['model_id']
#        reqs = data['requirements']

#    @api.doc('patch_model')
#    #@api.marshal_with(updated_model)
#    def patch(self, model_id):
#        data = request.get_json()
#        logging.info('Received update from fed. aggr. {}'.format(data))
#        DataOwnerService().update_model(model_id, data)
#        return 200
