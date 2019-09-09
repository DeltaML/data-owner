import logging
from threading import Thread

from commons.data.data_loader import DataLoader
from data_owner.exceptions.exceptions import InvalidFileException
from data_owner.models.dataset import Dataset


class DatasetsService:

    VALID_FILE_TYPES = ["text/csv"]
    DATASET_DIR = "./dataset"

    @classmethod
    def save(cls, file):
        """
        :param file:
        :return:
        """
        logging.info(file)
        file.save('{}/{}'.format(cls.DATASET_DIR, file.filename))
        metadata = DataLoader().get_dataset_metadata(file.filename)
        Dataset(metadata.id,
                file.filename,
                metadata.features,
                metadata.features_max,
                metadata.features_min,
                metadata.target_max,
                metadata.target_min).save()
        file.close()

    @classmethod
    def async_save(cls, file):
        """
        TODO: This method dont run -> fix
        :param file:
        :return:
        """
        Thread(target=cls.save, args=(file,)).start()

    @classmethod
    def validate(cls, file):
        if not file:
            raise InvalidFileException("Empty file")
        if file.content_type not in cls.VALID_FILE_TYPES:
            raise InvalidFileException("Invalid file type")
