from data_owner.models.model import Model
from data_owner.services.datasets_service import DatasetsService
from data_owner.models.model import TrainingStatus


class ModelService:

    @classmethod
    def get_all(cls, args):
        filters = {k: v for k, v in args.items() if v is not None}
        return Model.find_all_by(filters)

    @classmethod
    def get(cls, model_id):
        model = Model.get(model_id)
        dataset = DatasetsService().get_dataset_for_training(model.requirements)
        if dataset and model.status == TrainingStatus.WAITING.name:
            model.status = TrainingStatus.READY.name
        model.update()
        return model
