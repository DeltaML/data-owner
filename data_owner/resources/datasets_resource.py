import logging
from threading import Thread

from flask import request
from flask_restplus import Resource, Namespace, fields

from commons.data.data_loader import DataLoader
from data_owner.services.data_owner_service import DataOwnerService
from data_owner.models.dataset import Dataset


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
    'datasets': fields.List(fields.Nested(dataset_overview), required=True, description='The datasets that the data owner has uploaded')
})


@api.route('', endpoint='datasets_resources_ep')
class DatasetResources(Resource):

    @staticmethod
    def __save_dataset(file):
        filename = request.files.get('filename') or file.filename
        logging.info(file)
        file.save('./dataset/{}'.format(filename))
        DataLoader().get_dataset_metadata(filename).save()
        file.close()

    @api.doc('Create new user')
    def post(self):
        file = request.files.get('file')
        Thread(target=self.__save_dataset, args={'file': file}).start()
        return 200

    @api.marshal_list_with(datasets)
    def get(self):
        return Dataset.find_all()
