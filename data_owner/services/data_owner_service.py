import logging
import uuid

import numpy as np

from commons.decorators.decorators import optimized_collection_parameter
from commons.utils.singleton import Singleton
from commons.data.data_loader import DataLoader
from commons.model.model_service import ModelFactory
from data_owner.domain.data_owner import DataOwner
from data_owner.models.model import Model
from data_owner.services.federated_trainer_connector import FederatedTrainerConnector


class DataOwnerService(metaclass=Singleton):

    def __init__(self):
        self.client_id = None
        self.trainings = {}
        self.config = None
        self.data_loader = None
        self.federated_trainer_connector = None

    def init(self, config):
        """
        :param config:
        :param data_loader:
        :param encryption_service:
        """
        self.client_id = str(uuid.uuid1())
        self.config = config
        self.federated_trainer_connector = FederatedTrainerConnector(self.config)
        if config['REGISTRATION_ENABLE']:
            self.register()

    @optimized_collection_parameter(optimization=np.asarray, active=True)
    def process(self, model_id, weights):
        """
        Process to run model
        :param model_type:
        :param weights:
        :return:
        """
        logging.info("Initializing local model")
        model_orm = Model.get(model_id)
        model_orm.set_weights(weights)
        model, gradient = DataOwner().calculate_gradient(model_orm.model)
        model_orm.model = model
        model_orm.update()
        return gradient

    def register(self):
        """
        Register client into federated server
        :return:
        """
        result = self.federated_trainer_connector.register(self.get_id())
        logging.info("DataOwner registration status:" + str(result))

    def get_id(self):
        return self.client_id

    @optimized_collection_parameter(optimization=np.asarray, active=True)
    def step(self, model_id, step_data):
        """
        :param model:
        :param step_data:
        :return:
        """
        model_orm = Model.get(model_id)
        model = DataOwner().step(model_orm.model, step_data, float(self.config['ETA']))
        model_orm.update()
        logging.info("Model current weights {}".format(model.weights.tolist()))
        return model

    def model_quality_metrics(self, model_id, model_type, weights):
        """
        Method used only by validator role. It doesn't use the model built from the data. It gets the model from
        the federated trainer and use the local data to calculate quality metrics
        :return: the model quality (currently measured with the MSE)
        """
        data_owner = DataOwner()
        logging.info("Getting metrics, data owner: {}".format(self.client_id))
        X_test, y_test = DataLoader().get_sub_set()
        model_orm = Model.get(model_id) or ModelFactory.get_model(model_type)()
        model = model_orm.model
        model.set_weights(np.asarray(weights))
        mse = data_owner.model_quality_metrics(model, X_test, y_test)
        model_orm.add_mse(mse)
        model_orm.update()
        logging.info("Calculated mse: {}".format(mse))
        return mse

    def link_model_to_dataset(self, model_id, model_type, reqs):
        filename = DataLoader().get_dataset_for_training(reqs)
        if filename is not None:
            DataLoader().load_data(filename)
            dataset = DataLoader().get_sub_set()
            model = Model(model_id, model_type, dataset)
            model.save()
        return model_id, self.get_id(), filename is not None


class DataOwnerFactory:
    @classmethod
    def create_data_owner(cls, name):
        """
        :param name:
        :param data_loader:
        :return:
        """
        return DataOwnerService(name)
