import logging
import numpy as np

from data_owner.services.data_owner_service import DataOwnerService
from commons.model.model_service import ModelFactory
from data_owner.models.model import Model
from flask_restplus import Resource, Namespace, fields
from commons.data.data_loader import DataLoader
from flask import request

api = Namespace('metrics', description='Datasets related operations')

metric = api.model(name='Metric', model={
    'mse': fields.Float(required=True, description='The model mse')
})

data_owner = DataOwnerService()


@api.route('', endpoint='metrics_resources_ep')
class MetricsResources(Resource):

    @api.doc('Create new user')
    @api.marshal_with(metric, code=201)
    def post(self):
        data = request.get_json()
        model_id = data["model_id"]
        model_type = data["model_type"]
        weights = data["model"]
        logging.info("Getting metrics, data owner: {}".format(data_owner.client_id))
        X_test, y_test = DataLoader().get_sub_set()
        model_orm = Model.get(model_id) or ModelFactory.get_model(model_type)()
        model = model_orm.model
        model.set_weights(np.asarray(weights))
        mse = data_owner.model_quality_metrics(model, X_test, y_test)
        model_orm.add_mse(mse)
        model_orm.update()
        return {'mse': mse}
