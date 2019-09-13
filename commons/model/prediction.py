import uuid


class Prediction:
    def __init__(self, values, diff=None, model=None):
        self.id = str(uuid.uuid1())
        self.model = model
        self.values = values
        self.diff = diff

    def get_values(self):
        """
        TODO: Refactor this!
        :return:
        """
        return self.values.tolist()
