import requests
import logging


class FederatedTrainerConnector:

    def __init__(self, config):
        self.federated_trainer_host = config['FEDERATED_TRAINER_HOST']

    def register(self, client_id):
        """
        Register client on federated server
        :param client_data:
        :return:
        """
        server_register_url = self.federated_trainer_host + "/dataowner"
        logging.info("Register client {} to server {}".format(client_id, server_register_url))
        response = requests.post(server_register_url, json={'id': client_id})
        response.raise_for_status()
        return response.status_code == requests.codes.ok

    def send_prediction(self, prediction):
        server_register_url = self.federated_trainer_host + "/prediction"
        logging.info("Send prediction")
        response = requests.post(server_register_url, json=prediction.get_data())
        response.raise_for_status()
        return response.json()