from data_owner.models.model import Model
from data_owner.services.entities.model_response import ModelResponse


class ModelService:

    @classmethod
    def get_all(cls):
        return Model.find_all()

    @classmethod
    def get(cls, model_id):
        return ModelResponse(Model.get(model_id))
