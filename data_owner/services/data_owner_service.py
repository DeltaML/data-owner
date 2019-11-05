import logging

from commons.data.data_loader import DataLoader
from commons.decorators.decorators import data_owner_computation
from commons.model.model_service import ModelFactory
from commons.utils.singleton import Singleton
from commons.operations_utils.functions import deserialize, serialize
from data_owner.domain.data_owner import DataOwner
from data_owner.models.model import Model, TrainingStatus
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
        self.config = config
        self.encryption_service = encryption_service
        self.federated_aggregator_connector = FederatedAggregatorConnector(self.config)

    def update_stored_model(self, model_orm, model, public_key):
        model_orm.set_weights(serialize(model.weights, self.encryption_service, public_key))
        model_orm.model = model
        model_orm.update()

    def get_stored_model(self, model_orm, public_key):
        model_orm.set_weights(deserialize(model_orm.get_weights(), self.encryption_service, public_key))

    @data_owner_computation()
    def process(self, model_id, weights, public_key):
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
        self.update_stored_model(model_orm, model, public_key)
        return gradient

    def register(self, user):
        """
        Register client into federated server
        :return:
        """
        self.client_id = user.delta_id
        result = self.federated_aggregator_connector.register(user)

        logging.info("DataOwner registration status:" + str(result))

    def get_id(self):
        return self.client_id

    @data_owner_computation()
    def step(self, model_id, step_data, public_key):
        """
        :param model_id:
        :param step_data:
        :param public_key:
        :return:
        """
        model_orm = Model.get(model_id)
        self.get_stored_model(model_orm, public_key)
        model = DataOwner().step(model_orm.model, step_data, float(self.config['ETA']))
        return model.weights

    @data_owner_computation()
    def model_quality_metrics(self, model_id, weights, model_type, public_key):
        """
        Method used only by validator role. It doesn't use the model built from the data. It gets the model from
        the federated trainer and use the local data to calculate quality metrics
        :return: the model quality (currently measured with the MSE)
        """
        data_owner = DataOwner()
        logging.info("Getting metrics, data owner: {}".format(self.client_id))
        model_orm = Model.get(model_id)
        X_test, y_test = model_orm.get_dataset()
        model_orm.set_weights(weights)
        diffs = data_owner.model_quality_metrics(model_orm.model, X_test, y_test)
        return diffs

    def update_mse(self, model_id, mse, role):
        """
        Method used only by validator role. It doesn't use the model built from the data. It gets the model from
        the federated trainer and use the local data to calculate quality metrics
        :return: the model quality (currently measured with the MSE)
        """
        logging.info("Getting metrics, data owner: {}".format(self.client_id))
        model_orm = Model.get(model_id)
        model_orm.add_mse(mse)
        if model_orm.initial_mse == 0.0:
            model_orm.initial_mse = mse
        model_orm.improvement = max([(model_orm.initial_mse - mse) / model_orm.initial_mse, 0])
        model_orm.iterations += 1
        model_orm.role = role
        model_orm.update()
        logging.info("Calculated mse: {}".format(mse))

    def link_model_to_dataset(self, model_id):
        has_dataset = False
        model = Model.get(model_id)
        dataset = DatasetsService().get_dataset_for_training(model.requirements)
        if not dataset:
            return model_id, self.get_id(), has_dataset
        model.link_to_dataset(dataset)
        model.update()
        self.federated_aggregator_connector.accept_model_training(self.get_id(), model_id)
        return model_id, self.get_id(), not has_dataset

    def model_is_linked(self, model_id):
        return Model.get(model_id).status != TrainingStatus.WAITING

    def init_model(self, model_id, model_type, reqs):
        model = Model(model_id, model_type, reqs)
        model.save()
        return model_id, self.get_id()

    def finish_training(self, model_id, contrib):
        model = Model.get(model_id)
        model.status = TrainingStatus.FINISHED
        model.earned = self._calculate_earnings(model, contrib)
        model.update()

    def _calculate_earnings(self, model, contrib):
        if model.role == 'trainer':
            trainers_pay = 5 * model.improvement * 0.7
            return round(trainers_pay * contrib, 3)
        else:
            return round(5 * 0.2, 3)
