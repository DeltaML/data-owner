import logging

from commons.utils.singleton import Singleton

from data_owner.exceptions.exceptions import LoginFailureException, UserNotFoundException, AddressNotFoundException
from data_owner.models.user import User
from data_owner.services.user_login_service import UserLoginService


class UserService(metaclass=Singleton):

    def __init__(self):
        self.config = None
        self.data_owner_service = None

    def init(self, config, data_owner_service):
        self.config = config
        self.data_owner_service = data_owner_service

    @staticmethod
    def create(user_data):
        user = User(name=user_data["name"], email=user_data["email"], token=user_data["token"])
        user.save()
        return user

    @staticmethod
    def get_all():
        return User.find_all()

    @staticmethod
    def get(user_id):
        user = User.find_one_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    def update(self, user_id, user_data):
        user = self.get(user_id)
        return user.partial_update(user_id, user_data)

    def delete(self, user_id):
        user = self.get(user_id)
        user.delete()

    def login(self, data):
        token = data["token"]
        user_info = UserLoginService.get_user_info(token)

        if not UserLoginService.validate(user_info):
            raise LoginFailureException()

        user_external_id = user_info['sub']
        user = User.find_one_by_external_id(user_external_id)
        if not user:
            user = self.create_user(token, user_external_id, user_info)

        if not user_info["email_verified"]:
            raise LoginFailureException()

        try:
            self._register(user)
        except AddressNotFoundException:
            logging.warning("User {} haven't ethereum address to register into delta ml context".format(user.delta_id))
        return user

    @staticmethod
    def create_user(token, user_external_id, user_info):
        user = User(external_id=user_external_id,
                    name=user_info["name"],
                    email=user_info["email"],
                    token=token)
        user.save()
        return user

    def register(self, user_id, user_data):
        """
        Register a user into delta ml context
        :param user_id:
        :return:
        """
        user = self.get(user_id)
        user = user.update_address(user_id, user_data["address"])
        self._register(user)

    def _register(self, user):
        """
        Register client into federated server
        :return:
        """
        if not user.address:
            raise AddressNotFoundException("User {} haven't ethereum address to register into delta ml context".format(user.delta_id))
        result = self.data_owner_service.register(user)
        logging.info("DataOwner registration status:" + str(result))
