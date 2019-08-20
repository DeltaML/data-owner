from enum import Enum
from sqlalchemy import Column, String, Sequence, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from data_owner.models.user import User
from data_owner.services.data_base import DbEntity


class Status(Enum):
    WAITING = 0
    INITIATED = 1
    IN_PROGRESS = 2
    FINISHED = 3


class Training(DbEntity):
    __tablename__ = 'models'
    id = Column(String(100), Sequence('model_id_seq'), primary_key=True)
    model_type = Column(String(50))
    requirements = Column(JSON)
    request_data = Column(JSON)
    status = Column(String(50), default=Status.INITIATED.name)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="models")
    User.models = relationship("Model", back_populates="user")
    data_base = relationship("Database")

    def __init__(self, model_id, model_type, requirements, name="default"):
        self.id = model_id
        self.model_type = model_type
        self.status = Status.INITIATED.name
        self.name = name
        self.requirements = requirements

    @classmethod
    def get(cls, model_id=None):
        filters = {'id': model_id} if model_id else None
        return DbEntity.find(Training, filters)

    def update_model(self, status, model_id=None):
        filters = {'id': model_id} if model_id else None
        self.update(Training, filters, {Training.status: status})

    @classmethod
    def find_all(cls):
        return DbEntity.find(Training)
