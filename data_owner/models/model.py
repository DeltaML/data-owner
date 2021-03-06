from datetime import datetime
import logging
import time
from enum import Enum
from flask import json
import numpy as np
import sqlalchemy.types as types
from sqlalchemy import Column, String, Sequence, JSON, Float, Integer, ForeignKey, ARRAY, DateTime
from sqlalchemy.orm import relationship
from commons.model.model_service import ModelFactory
from data_owner.models.user import User
from data_owner.services.data_base import DbEntity


class TrainingStatus(Enum):
    WAITING = 0
    READY = 1
    INITIATED = 2
    IN_PROGRESS = 3
    FINISHED = 4


class ModelColumn(types.UserDefinedType):

    def get_col_spec(self, **kw):
        return "ModelColumn"

    def bind_processor(self, dialect):
        def process(value):
            x = value.X.tolist() if value and value.X is not None else None
            y = value.y.tolist() if value and value.y is not None else None
            weights = value.weights if value and type(value.weights) == list else value.weights.tolist() if value and value.weights.any() else None
            model_type = value.type if value else None
            return json.dumps({
                'x': x, 'y': y, 'weights': weights, 'type': model_type
            })
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            model_data = json.loads(value)
            x = np.asarray(model_data['x'])
            y = np.asarray(model_data['y'])
            model_type = model_data['type']
            weights = np.asarray(model_data['weights'])
            model = ModelFactory.get_model(model_type)(X=x, y=y, weights=weights)
            return model
        return process


class BaseModel(DbEntity):
    __tablename__ = 'models'
    id = Column(String(100), primary_key=True)
    model_type = Column(String(50))
    requirements = Column(JSON)
    model = Column(ModelColumn())
    request_data = Column(JSON)
    mse = Column(Float)
    initial_mse = Column(Float)
    status = Column(String(50), default=TrainingStatus.WAITING.name)
    improvement = Column(Float)
    name = Column(String(100))
    iterations = Column(Integer)
    earned = Column(Float)
    role = Column(String)
    mse_history = Column(JSON)
    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="models")
    User.models = relationship("Model", back_populates="user")

    def __init__(self, model_id, model_type, reqs, name="default"):
        self.id = model_id
        self.model_type = model_type
        _model = ModelFactory.get_model(self.model_type)(X=None, y=None, requirements=reqs)
        self.model = _model
        self.model.set_weights(_model.weights.tolist())
        self.model.type = self.model_type
        self.requirements = reqs
        self.status = TrainingStatus.WAITING.name
        self.iterations = 0
        self.improvement = 0.0
        self.name = name
        self.earned = 0.0
        self.role = "None"
        self.mse = 0.0
        self.initial_mse = 0.0
        self.mse_history = []

    def link_to_dataset(self, data):
        _model = ModelFactory.get_model(self.model_type)(X=data[0], y=data[1])
        self.model = _model
        self.status = TrainingStatus.INITIATED.name
        self.update()

    def set_weights(self, weights):
        if type(weights) == list:
            weights = np.asarray(weights)
        self.model.set_weights(weights)

    def get_weights(self):
        weights = self.model.weights
        return np.asarray(weights) if type(weights) == list else weights

    def get_weights_as_list(self):
        return self.model.weights.tolist()

    def predict(self, x, y):
        prediction = self.model.predict(x, y)
        self.mse = prediction.mse
        return prediction

    def get_dataset(self):
        return self.model.X, self.model.y

    @classmethod
    def get(cls, model_id=None):
        filters = {'id': model_id} if model_id else None
        return DbEntity.find(BaseModel, filters)

    def update(self):
        filters = {'id': self.id}
        update_data = {BaseModel.model: self.model, BaseModel.status: self.status, BaseModel.iterations: self.iterations,
                       BaseModel.improvement: self.improvement, BaseModel.name: self.name,
                       BaseModel.mse_history: self.mse_history, BaseModel.initial_mse: self.initial_mse,
                       BaseModel.updated_date: self.updated_date, BaseModel.mse: self.mse, BaseModel.earned: self.earned}
        super(BaseModel, self).update(BaseModel, filters, update_data)

    def add_mse(self, mse):
        self.mse = mse
        self.mse_history.append(dict(time=str(time.time()), mse=mse))

    @classmethod
    def find_all(cls):
        return DbEntity.find(BaseModel)

    @classmethod
    def find_all_by(self, filters):
        return DbEntity.find(BaseModel, filters)

    @classmethod
    def find_by_status(self, status):
        filters = {'status': status}
        return DbEntity.find(BaseModel, filters)


class Model(BaseModel):

    def __init__(self, model_id, model_type, data, name="default"):
        super(Model, self).__init__(model_id, model_type, data, name)

    def set_weights(self, weights):
        weights = np.asarray(weights) if type(weights) == list else weights
        self.model.set_weights(weights)

    def get_weights(self):
        return self.model.weights if type(self.model.weights) == list else self.model.weights.tolist()
