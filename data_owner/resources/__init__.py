import logging
from flask import jsonify, make_response, abort
from flask_restplus import Api

from data_owner.exceptions.exceptions import NoResultFoundException, LoginFailureException
from data_owner.resources.trainings_resource import api as trainings_api
from data_owner.resources.datasets_resource import api as datasets_api
from data_owner.resources.metrics_resource import api as metrics_api

api = Api(
    title='Data Owner Api',
    version='1.0',
    description='Data Owner Api API',
    doc='/doc/'
)

# Add apis to namespace
api.add_namespace(trainings_api)
api.add_namespace(datasets_api)
api.add_namespace(metrics_api)


@api.errorhandler(LoginFailureException)
def login_failure_handler(error):
    """
    Default error handler
    :param error:
    :return:
    """
    logging.error(error)
    return {'message': str(error)}, 400


@api.errorhandler(NoResultFoundException)
def not_found_error_handler(error):
    """
    Default error handler
    :param error:
    :return:
    """
    logging.error(error)
    return {'message': str(error)}, 404


@api.errorhandler(NoResultFoundException)
def dataset_not_found_error_handler(error):
    """
    Default error handler
    :param error:
    :return:
    """
    logging.error(error)
    return {'message': str(error)}, 404


@api.errorhandler(Exception)
def default_error_handler(error):
    """
    Default error handler
    :param error:
    :return:
    """
    logging.error(error)
    return {'message': str(error)}, 500


def _handle_error(error):
    logging.error(error)
    return ErrorHandler.create_error_response(error.status_code, error.message)


class ErrorHandler:
    @staticmethod
    def create_error_response(status_code, message):
        return make_response(
            jsonify(
                {
                    "status_code": status_code,
                    "message": message
                }
            ),
            status_code
        )
