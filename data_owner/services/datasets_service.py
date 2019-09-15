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
        if not metadata:
            raise InvalidFileException()
        ds = Dataset(metadata.id,
                file.filename,
                metadata.features,
                metadata.features_max,
                metadata.features_min,
                metadata.target_max,
                metadata.target_min)
        ds.save()
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
        if cls.allowed_file_extension(file.filename):
            raise InvalidFileException("Invalid file type")

    def get_dataset_for_training(self, reqs):
        ds = self.search_dataset_by_requirements(reqs)
        if not ds:
            logging.warning("Empty file")
            return None
        logging.info("File {} found".format(ds.filename))
        DataLoader().load_data(ds.filename)
        return DataLoader().get_sub_set()

    @classmethod
    def allowed_file_extension(cls, filename):

        # We only want files with a . in the filename
        if not "." in filename:
            return False

        # Split the extension from the filename
        ext = filename.rsplit(".", 1)[1]

        # Check if the extension is in VALID_FILE_TYPES
        if ext.upper() in cls.VALID_FILE_TYPES:
            return True
        else:
            return False

    @staticmethod
    def search_dataset_by_requirements(requeriments):
        """
        TODO agrojas -> refactor this to query
        Iterates over the files in the datasets directory and verifies wich of those comply with the requested
        requirements for the current model training. The last of the datasets that complies with the requirements
        is then returned by this method.
        :param requeriments: a dictionary with requirements for the dataset to be returned
        :return: the name of the file that complies with the requested requirements.
        """
        logging.info("Search with requirements {}".format(requeriments))
        features = requeriments['features']['list']
        feat_range = requeriments['features']['range']
        target_range = requeriments['target']['range']
        for dataset in Dataset.find_all():
            try:
                logging.info("Dataset {}".format(dataset))
                if set(dataset.features) != set(features):
                    continue
                if dataset.features_max > feat_range[1]:
                    continue
                if dataset.features_min < feat_range[0]:
                    continue
                if dataset.target_max > target_range[1]:
                    continue
                if dataset.target_min < target_range[0]:
                    continue
            except Exception as e:
                logging.error(e)
                continue
            return dataset
        return None
