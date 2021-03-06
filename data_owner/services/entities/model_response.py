class ModelResponse:
    @staticmethod
    def map_weights(weights):
        return weights.tolist()

    def __init__(self, model):
        self.model = {"id": model.id,
                      "weights": self.map_weights(model.model.weights),
                      "type": model.model_type,
                      "status": model.status,
                      "creation_date": model.creation_date,
                      "updated_date": model.updated_date,
                      "user_id": model.user_id,
                      "requirements": model.requirements,
                      "name": model.name}

        self.metrics = {"mse": model.mse,
                        "improvement": model.improvement,
                        "initial_mse": model.initial_mse,
                        'iterations': model.iterations,
                        'mse_history': model.mse_history,
                        "earned": model.earned
                        }


class NewModelResponse:

    def __init__(self, ordered_model):
        self.requirements = ordered_model.request_data
        self.model = {"id": ordered_model.id,
                      "status": ordered_model.status,
                      "type": ordered_model.model_type,
                      "weights": ordered_model.model.weights.tolist()
                      }


class NewModelRequestData:

    def __init__(self, ordered_model, requirements, user_id, model_type):
        self.requirements = requirements
        self.status = ordered_model.status
        self.model_id = ordered_model.id
        self.model_type = model_type
        self.model_buyer_id = user_id
        self.weights = ordered_model.model.weights.tolist()

    def get(self):
        return dict(requirements=self.requirements,
                    status=self.status,
                    model_id=self.model_id,
                    model_type=self.model_type,
                    model_buyer_id=self.model_buyer_id,
                    weights=self.weights)
