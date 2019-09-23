from sqlalchemy import Column, String, Integer, JSON, Float
from data_owner.services.data_base import DbEntity


class Dataset(DbEntity):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(500), unique=True)
    filename = Column(String(100), unique=True)
    features = Column(JSON)
    features_max = Column(Float)
    features_min = Column(Float)
    target_max = Column(Float)
    target_min = Column(Float)

    # TODO:
    #linked_models = Column(JSON)

    def __init__(self,
                 external_id,
                 filename,
                 features_cols,
                 features_max,
                 features_min,
                 target_max,
                 target_min):
        self.external_id = external_id
        self.filename = filename
        self.features = features_cols
        self.features_max = features_max
        self.features_min = features_min
        self.target_max = target_max
        self.target_min = target_min

    @classmethod
    def exists_external_id(cls, external_id):
        filters = {'external_id': external_id}
        return DbEntity.exists(Dataset, filters)

    @classmethod
    def find_all(cls):
        return DbEntity.find(Dataset)

    @classmethod
    def find_one_by_id(cls, user_id):
        filters = {'id': user_id}
        return DbEntity.find(Dataset, filters)

    @classmethod
    def find_one_by_external_id(cls, external_id):
        filters = {'external_id': external_id}
        return DbEntity.find(Dataset, filters)

    @classmethod
    def find_one_by_filename(cls, filename):
        filters = {'filename': filename}
        return DbEntity.find(Dataset, filters)

    @classmethod
    def find_one_by_features(cls, features, all=False):
        filters = {'features': features}
        return DbEntity.find(Dataset, filters, all)

    @classmethod
    def find_all_by_features(cls, features, all=True):
        filters = {'features': features}
        return DbEntity.find(Dataset, filters, all)

    def __str__(self):
        return str({
            'external_id': str(self.external_id),
            'filename': str(self.filename),
            'features': str(self.features),
            'features_max': str(self.features_max),
            'features_min': str(self.features_min),
            'target_max': str(self.target_max),
            'target_min': str(self.target_min)

        })

    def __repr__(self):
        return self.__str__()
