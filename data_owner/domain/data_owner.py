from commons.utils.singleton import Singleton
import numpy as np

class DataOwner(metaclass=Singleton):
    # TODO (Fabrizio): Ver que esta clase no quede como un pasamanos

    def calculate_gradient(self, model):
        """
        Process to run model
        :param model: the ML model wich will calculate a gradient vector for a future step in gradient descent
        :param weights: the weights of the model
        :return:
        """
        gradient = model.compute_gradient()
        return model, gradient.tolist()

    def step(self, model, step_data, eta=1.5):
        """
        :param model: the ML model that will perform a step of gradient descent
        :param step_data: the gradient vector to be used in the gradient descent step
        :param eta: the length of the step
        :return:
        """
        # TODO agrojas
        step_data = np.asarray(step_data) if type(step_data) == list else step_data
        model.gradient_step(step_data, eta)
        return model

    def model_quality_metrics(self, model, X_test, y_test):
        """
        :param model: the ML model that will be tested
        :param X_test: the test dataset features
        :param y_test: the expected target of the test dataset
        Method used only by validator role. It doesn't use the model built from the data. It gets the model from
        the federated trainer and use the local data to calculate quality metrics
        :return: the model quality (currently measured with the MSE)
        """
        mse = model.predict(X_test, y_test).mse
        return mse


class DataOwnerFactory:
    @classmethod
    def create_data_owner(cls):
        """
        :param name:
        :param data_loader:
        :return:
        """
        return DataOwner()
