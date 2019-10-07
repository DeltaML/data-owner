import logging
from data_owner.exceptions.exceptions import LoginFailureException, UserNotFoundException
from data_owner.models.user import User
from data_owner.services.user_login_service import UserLoginService


class UserService:

    @staticmethod
    def create(user_data):
        user = User(name=user_data["name"], email=user_data["email"], token=user_data["token"])
        user.save()

    @staticmethod
    def get_all():
        return User.find_all()

    @staticmethod
    def get(user_id):
        user = User.find_one_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    @staticmethod
    def update(user_id, user_data):
        return UserService.get(user_id).partial_update(user_id, user_data)

    def delete(self, user_id):
        user = self.get(user_id)
        user.delete()

    @staticmethod
    def login(data):
        token = data["token"]
        user_info = UserLoginService.get_user_info(token)

        if not UserLoginService.validate(user_info):
            raise LoginFailureException()

        user_external_id = user_info['sub']
        user = User.find_one_by_external_id(user_external_id)
        if user:
            return user

        if not user_info["email_verified"]:
            raise LoginFailureException()

        user = User(external_id=user_external_id,
                    name=user_info["name"],
                    email=user_info["email"],
                    token=token)
        user.save()
        return User.find_one_by_external_id(user_external_id)
