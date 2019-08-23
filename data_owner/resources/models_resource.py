from flask_restplus import Resource, Namespace, fields
from data_owner.services.data_owner_service import DataOwnerService
from data_owner.services.entities.model_response import ModelResponse, NewModelResponse
from data_owner.models.model import Model

api = Namespace('models', description='Model related operations')

model_detail_reduced = api.model(name='Models', model={
    'id': fields.String(required=True, description='The model identifier'),
    'status': fields.String(required=True, description='The model status'),
    'name': fields.String(required=True, description='The model name'),
    'improvement': fields.Fixed(required=True, decimals=5, description='The model improvement'),
    'iterations': fields.Integer(required=True, description='Number of iterations'),
    'mse': fields.Float(required=True, description='The model mse'),
    'user_id': fields.String(required=True, description='The model user_id'),
    'creation_date': fields.String(description='The model creation date')
})

mse_history = api.model(name='MSE History', model={
    'time': fields.String(required=True,
                          description='The data owner removed from the training of this model to obtain the partial MSE'),
    'mse': fields.Float(required=True, description='The MSE of model updated without the data owner'),
})


metrics_detail = api.model(name='Metrics', model={
    'initial_mse': fields.Float(required=True, description='The Initial MSE of the model'),
    'mse': fields.Float(required=True, description='The MSE of the model'),
    'iterations': fields.Integer(required=True, description='Number of iterations'),
    'improvement': fields.Fixed(required=True, decimals=5, description='The model improvement'),
    'mse_history': fields.List(fields.Nested(mse_history), required=True, description='The model mse history list')
})


model_detail = api.model(name='Model', model={
    'id': fields.String(required=True, description='The model identifier'),
    'status': fields.String(required=True, description='The model status'),
    'type': fields.String(required=True, description='The model type'),
    'weights': fields.List(fields.Raw, required=True, description='The model weights'),
    'creation_date': fields.String(description='The model creation date'),
    'updated_date': fields.String(description='The model updated date'),
    'user_id': fields.String(required=True, description='The model user_id'),
    'name': fields.String(required=True, description='The model name')
})

model_data = api.model(name='Updated Model', model={
    'metrics': fields.Nested(metrics_detail, required=True, description='The model requirements'),
    'model': fields.Nested(model_detail, required=True, description='The model')
})

model = api.model(name='Model', model={
    'id': fields.String(required=True, description='The model identifier'),
    'status': fields.String(required=True, description='The model status'),
    'type': fields.String(required=True, description='The model type'),
    'weights': fields.List(fields.Raw, required=True, description='The model weights')
})

data_owner = DataOwnerService()


@api.route('', endpoint='models_resources_ep')
class ModelsResources(Resource):

    @api.marshal_list_with(model_detail_reduced)
    def get(self):
        return [NewModelResponse(model) for model in Model.find_all()]


@api.route('/<model_id>', endpoint='model_resources_ep')
class ModelResources(Resource):

    @api.doc('Get trained model')
    @api.marshal_with(model_data)
    def get(self, model_id):
        return ModelResponse(Model.get(model_id))
