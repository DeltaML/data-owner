from flask_restplus import Resource, Namespace, fields
from data_owner.services.data_owner_service import DataOwnerService
from data_owner.models.model import Model

api = Namespace('models', description='Training related operations')

model = api.model(name='Model', model={
    'id': fields.String(required=True, description='The model identifier'),
    'status': fields.String(required=True, description='The model status'),
    'type': fields.String(required=True, description='The model type'),
    'weights': fields.List(fields.Raw, required=True, description='The model weights')
})

data_owner = DataOwnerService()


@api.route('', endpoint='models_resources_ep')
class ModelsResources(Resource):

    @api.marshal_list_with(model)
    def get(self):
        return Model.find_all(), 200

    @api.doc('Get trained model')
    @api.marshal_with(model)
    def get(self, model_id):
        return Model.get(model_id)
