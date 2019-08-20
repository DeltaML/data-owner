import numpy as np
import logging

from commons.model.exceptions.exceptions import ModelErrorException


class DeltaModel(object):
    def __init__(self, X=None, y=None, model_type=None, requirements=None, weights=None):
        self.X, self.y = X, y
        self.weights = weights if weights is not None else self._get_weights(X, requirements)
        self.type = model_type

    def set_data(self, X, y):
        self.X, self.y = X, y
        self.weights = np.zeros(X.shape[1])

    def set_weights(self, weights):
        self.weights = weights

    def fit(self, n_iter, eta=0.01):
        pass

    def predict(self, X):
        pass

    def _get_weights(self, X, requirements):
        """
        Get model weights from X data or length of list of features in requirements data or raise ModelErrorException
        :param X:
        :param requirements:
        :return:
        """
        if X.any():
            return np.zeros(X.shape[1])
        elif requirements:
            return self._get_from_requirements(requirements)
        else:
            logging.error("Data for model {} {}".format(X, requirements))
            raise ModelErrorException()

    @staticmethod
    def _get_from_requirements(requirements):
        """
        Add one dimaension to emulate intercept
        :param requirements:
        :return:
        """
        try:
            return np.zeros(len(requirements["features"]["list"]) + 1)
        except KeyError:
            pass
