import logging
import uuid

import numpy as np

from commons.decorators.decorators import optimized_collection_parameter
from commons.utils.singleton import Singleton
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
    def process(self, model, weights):
        """
        Process to run model
        :param model_type:
        :param weights:
        :return:
        """
        logging.info("Initializing local model")
        model.set_weights(weights)
        gradient = model.compute_gradient()
        return model, gradient.tolist()

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
    def step(self, model, step_data):
        """
        :param encrypted_model:
        :return:
        """
        model.gradient_step(step_data, float(self.config['ETA']))
        logging.info("Model current weights {}".format(model.weights.tolist()))
        return model

    def model_quality_metrics(self, model, X_test, y_test):
        """
        Method used only by validator role. It doesn't use the model built from the data. It gets the model from
        the federated trainer and use the local data to calculate quality metrics
        :return: the model quality (currently measured with the MSE)
        """
        mse = model.predict(X_test, y_test).mse
        logging.info("Calculated mse: {}".format(mse))
        return mse


class DataOwnerFactory:
    @classmethod
    def create_data_owner(cls, name):
        """
        :param name:
        :param data_loader:
        :return:
        """
        return DataOwnerService(name)
