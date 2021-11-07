"""
@author: Mohammed Jassim
"""

from os import sep, path

import decouple
import gridfs
import io
import joblib

from config import config
from mongodb_ml_models.constants import config_file_name
from mongodb_ml_models.mongodb_handle import MongoDb
from mongodb_ml_models.directory_handling import DirectoryHandling

config_parsing = config(config_file_name=config_file_name)
_host = config_parsing.get('mongodb.model', 'host')
_port = config_parsing.get('mongodb.model', 'port')
_db_name = config_parsing.get('mongodb.model', 'db_name')

enable_db_options = decouple.config('ENABLE_MONGODB_MODEL', default=True, cast=bool)


class ManageModel:
    """
    If you want to save in local and not wish to upload to db then set env variable ENABLE_MONGODB_MODEL=False
    """
    @staticmethod
    def connect_db():
        mongo_client = MongoDb(host=_host, port=_port)

        return mongo_client

    @staticmethod
    def get_root_save_model_path(class_name: str) -> str:
        root_path = f"ml{sep}model{sep}{class_name}"

        return root_path

    @staticmethod
    def get_mongodb_model_collection_object(mongo_db_connect, query):
        mongo_collection = mongo_db_connect.fs.files

        return mongo_collection.find(query)

    @classmethod
    def get_mongodb_model_file_collection(cls, mongo_db_connect, file_name):
        query = {"filename": file_name}

        result = cls.get_mongodb_model_collection_object(mongo_db_connect, query)

        for each_result in result:
            yield each_result

    @classmethod
    def get_mongodb_model_versions(cls, mongo_db_connect, model_name) -> list:
        query = {"model_name": model_name, "model_type": config_parsing.get("mongodb.model", "model_type")}
        versions = []

        for each_versions in cls.get_mongodb_model_collection_object(mongo_db_connect, query):
            versions.append(each_versions["model_version"])

        return versions

    @classmethod
    def get_file_id(cls, mongo_db_connect, file_name):
        for each_result in cls.get_mongodb_model_file_collection(mongo_db_connect, file_name):
            yield each_result['_id']

    @classmethod
    def delete_existing_same_model(cls, file_name, fs, mongo_db_connect):
        for each_id in cls.get_file_id(mongo_db_connect, file_name):
            print(f"Removing existing model: {each_id}")
            fs.delete(each_id)

    @classmethod
    def get_db_file_name(cls, model_class):
        model_type = config_parsing.get('mongodb.model', 'model_type')
        model_name_with_version = cls.get_model_version_name(model_class)

        return f"{model_type}_{model_name_with_version}"

    @staticmethod
    def get_model_version_name(model_class: str) -> str:
        """
        version_name = name_version
        :param model_class: Class name (model.model_training_name)
        :return:
        """
        model_real_name = config_parsing.get(model_class, 'name')
        model_version_number = config_parsing.get(model_class, 'version')

        return f"{model_real_name}_{model_version_number}"

    @classmethod
    def get_model_saved_path_with_name(cls, model_class):
        model_name = config_parsing.get(model_class, 'name')
        version = config_parsing.get(model_class, 'version')

        return path.join(cls.get_root_save_model_path(model_name), version)

    @classmethod
    def create_model_saving_base_file(cls, model_class):
        model_name = config_parsing.get(model_class, 'name')
        DirectoryHandling.create_directory(cls.get_root_save_model_path(model_name))

    @classmethod
    def save_model(cls, binary_model, model_class) -> str:
        """
        Save model and return saved path
        :param binary_model: Binary model
        :param model_class: Model class
        :return: Saved file path
        """
        cls.create_model_saving_base_file(model_class)
        model_path_with_name = cls.get_model_saved_path_with_name(model_class)
        joblib.dump(binary_model, model_path_with_name)

        print(f"Model saved in {model_path_with_name}")

        return model_path_with_name

    @classmethod
    def add_model_name_and_version(cls, mongo_client, file_name, model_class):
        mongo_db_connect = mongo_client.client[_db_name]

        for each_result_data in cls.get_mongodb_model_file_collection(mongo_db_connect, file_name):
            file_id = each_result_data.pop("_id")
            model_name = config_parsing.get(model_class, "name")
            model_version = config_parsing.get(model_class, "version")
            each_result_data["model_name"] = model_name
            each_result_data["model_version"] = model_version
            each_result_data["model_type"] = config_parsing.get("mongodb.model", "model_type")

            mongo_client.upsert(_db_name, "fs.files", {"_id": file_id}, each_result_data)

    @classmethod
    def upload_model(cls, binary_model, model_class):
        model_path_with_name = cls.save_model(binary_model, model_class)

        if enable_db_options:
            mongo_client = cls.connect_db()
            mongo_db_connect = mongo_client.client[_db_name]
            fs = gridfs.GridFS(mongo_db_connect)

            file_name = cls.get_db_file_name(model_class)
            cls.delete_existing_same_model(file_name, fs, mongo_db_connect)

            with io.FileIO(model_path_with_name, 'r') as fileObject:
                fs.put(fileObject, filename=file_name)
                cls.add_model_name_and_version(mongo_client, file_name, model_class)

            print(f"Model uploaded, {file_name}")

    @classmethod
    def download_model(cls, model_class: str):
        cls.create_model_saving_base_file(model_class)
        file_path_with_name = cls.get_model_saved_path_with_name(model_class)

        mongo_client = cls.connect_db()

        fs = gridfs.GridFS(mongo_client.client[_db_name])
        mongo_db_connect = mongo_client.client[_db_name]

        db_file_name = cls.get_db_file_name(model_class)
        model = None

        for each_id in cls.get_file_id(mongo_db_connect, db_file_name):
            with open(file_path_with_name, 'wb') as fileObject:
                fileObject.write(fs.get(each_id).read())
                print(f"Model downloaded. {file_path_with_name}")

            model = joblib.load(file_path_with_name)
            break

        if model:
            return model

        else:
            model_name = config_parsing.get(model_class, 'name')
            model_version = config_parsing.get(model_class, 'version')

            raise FileNotFoundError(f"Model Not found\nModel name: {model_name}\nVersion: {model_version}\n"
                                    f"DB: {_db_name}\nhost: {_host}\nport: {_port}")

    @classmethod
    def get_model(cls, model_class):
        """
        1. If model available in local use local model
        2. If model not available, then download and save and return model
        3. Model path will be ml/model/model_name/version
        :param model_class: Model class name
        :return: Binary model
        """
        model_path_with_name = cls.get_model_saved_path_with_name(model_class)

        if path.exists(model_path_with_name):
            model = joblib.load(model_path_with_name)
            print(f"Model loaded {model_path_with_name}")

        else:
            print(f"Downloading model. {model_path_with_name}")
            model = cls.download_model(model_class)

        return model

    @classmethod
    def get_model_versions(cls, model_class):
        mongo_client = cls.connect_db()
        mongo_db_connect = mongo_client.client[_db_name]
        model_name = config_parsing.get(model_class, "name")
        versions = cls.get_mongodb_model_versions(mongo_db_connect, model_name)

        print(f"Available versions for model '{model_name}': {versions}")

