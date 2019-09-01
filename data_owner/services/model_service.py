from data_owner.models.model import Model


class ModelService:

    @classmethod
    def get_all(cls):
        return Model.find_all()

    @classmethod
    def get(cls, model_id):
        return Model.get(model_id)
