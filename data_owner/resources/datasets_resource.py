import logging

from flask import request
from flask_restplus import Resource, Namespace, fields

from data_owner.models.dataset import Dataset
from data_owner.services.datasets_service import DatasetsService

api = Namespace('datasets', description='Datasets related operations')

dataset_data = api.model(name='Dataset', model={
    'training_id': fields.String(required=True, description='The model training identifier'),
    'data_owner_id': fields.String(required=True, description='The data owner identifier'),
    'result': fields.Boolean(required=True, description='The data owner has the dataset for the model training'),
})

dataset_overview = api.model(name='DatasetOverview', model={
    'filename': fields.String(required=True, description='The name of the file of the dataset'),
    'features': fields.String(required=True, description='The features that the dataset has.')
})

datasets = api.model(name="Datasets", model={
    'datasets': fields.List(fields.Nested(dataset_overview), required=True,
                            description='The datasets that the data owner has uploaded')
})


@api.route('', endpoint='datasets_resources_ep')
class DatasetResources(Resource):

    @api.doc('Save new  Dataset')
    def post(self):
        file = request.files.get('file')
        DatasetsService.validate(file)
        logging.info("File received {}".format(file.filename))
        DatasetsService.save(file)
        return 200

    @api.marshal_list_with(datasets)
    def get(self):
        return Dataset.find_all()
