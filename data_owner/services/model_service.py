from data_owner.models.model import Model

class ModelService:

    @classmethod
    def get_all(cls, args):
        filters = {k: v for k, v in args.items() if v is not None}
        return Model.find_all_by(filters)

    @classmethod
    def get(cls, model_id):
        return Model.get(model_id)
