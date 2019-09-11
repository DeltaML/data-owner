import logging
import uuid

import numpy as np

from commons.data.data_loader import DataLoader
from commons.decorators.decorators import optimized_collection_parameter
from commons.model.model_service import ModelFactory
from commons.utils.singleton import Singleton
from data_owner.domain.data_owner import DataOwner
from data_owner.models.model import Model
from data_owner.services.datasets_service import DatasetsService
from data_owner.services.federated_aggregator_connector import FederatedAggregatorConnector


class DataOwnerService(metaclass=Singleton):

    def __init__(self):
        self.client_id = None
        self.trainings = {}
        self.config = None
        self.data_loader = None
        self.federated_aggregator_connector = None
        self.encryption_service = None

    def init(self, config, encryption_service=None):
        """
        :param config:
        :param data_loader:
        :param encryption_service:
        """
        self.client_id = str(uuid.uuid1())
        self.config = config
        self.encryption_service = encryption_service
        self.federated_aggregator_connector = FederatedAggregatorConnector(self.config)
        if config['REGISTRATION_ENABLE']:
            self.register()

    #@optimized_collection_parameter(optimization=np.asarray, active=False)
    def process(self, model_id, weights):
        """
        Process to run model
        :param model_type:
        :param weights:
        :return:
        """

        logging.info("Initializing local model")
        model_orm = Model.get(model_id)
        # TODO agrojas
        model_orm.set_weights(weights)
        #model_orm.set_weights(np.asarray(weights))
        model, gradient = DataOwner().calculate_gradient(model_orm.model)
        model_orm.model = model
        # TODO agrojas
        #model_orm.set_weights(model_orm.get_weights().tolist())
        model_orm.update()
        return gradient

    def register(self):
        """
        Register client into federated server
        :return:
        """
        result = self.federated_aggregator_connector.register(self.get_id())
        logging.info("DataOwner registration status:" + str(result))

    def get_id(self):
        return self.client_id

    #@optimized_collection_parameter(optimization=np.asarray, active=True)
    def step(self, model_id, step_data):
        """
        :param model_id:
        :param step_data:
        :return:
        """
        model_orm = Model.get(model_id)
        # TODO agrojas
        model = DataOwner().step(model_orm.model, step_data, float(self.config['ETA']))
        #model_orm.model.weights = model_orm.model.weights.tolist()
        model_orm.update()
        return model

    def model_quality_metrics(self, model_id, model_type, weights, public_key):
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
        model_weights = self._get_model_weights(weights, public_key)
        model.set_weights(model_weights)
        mse = data_owner.model_quality_metrics(model, X_test, y_test)
        model_orm.add_mse(mse)
        # TODO agrojas
        #model_orm.model.weights = model_orm.model.weights.tolist()
        model_orm.update()
        logging.info("Calculated mse: {}".format(mse))
        return mse

    def _get_model_weights(self, rq_weights, public_key):
        self.encryption_service.set_public_key(public_key)
        weights = rq_weights if not self.encryption_service.is_active else self.encryption_service.get_deserialized_collection(
            rq_weights)
        return np.asarray(weights)

    def link_model_to_dataset(self, model_id, model_type, reqs):
        has_dataset = False
        dataset = DatasetsService().get_dataset_for_training(reqs)
        if not dataset:
            return model_id, self.get_id(), has_dataset
        model = Model(model_id, model_type, dataset)
        model.save()
        return model_id, self.get_id(), not has_dataset
