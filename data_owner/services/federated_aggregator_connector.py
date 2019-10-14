import requests
import logging
from commons.utils.async_thread_pool_executor import AsyncThreadPoolExecutor


class FederatedAggregatorConnector:

    def __init__(self, config):
        self.federated_aggregator_host = config['FEDERATED_AGGREGATOR_HOST']
        self.async_thread_pool = AsyncThreadPoolExecutor()

    def register(self, client):
        """
        Register client on federated server
        :param client:
        :return:
        """
        server_register_url = self.federated_aggregator_host + "/dataowner"
        logging.info("Register client {} to server {}".format(client.delta_id, server_register_url))
        response = requests.post(server_register_url, json={'id': client.delta_id, 'address': client.address})
        response.raise_for_status()
        return response.status_code == requests.codes.ok

    def accept_model_training(self, client_id, model_id):
        server_register_url = self.federated_aggregator_host + "/model/" + model_id + "/accept"
        logging.info("Register client {} to server {}".format(client_id, server_register_url))
        args = [{'url': server_register_url, 'payload': {'data_owner_id': client_id, 'model_id': model_id}}]
        self.async_thread_pool.run(executable=self.send_accept_request, args=args)

    def send_accept_request(self, args):
        response = requests.post(args['url'], json=args['payload'])
        response.raise_for_status()
        return response.status_code == requests.codes.ok

    def send_prediction(self, prediction):
        server_register_url = self.federated_aggregator_host + "/prediction"
        logging.info("Send prediction")
        response = requests.post(server_register_url, json=prediction.get_data())
        response.raise_for_status()
        return response.json()
