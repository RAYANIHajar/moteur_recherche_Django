"""
@author: Mohammed Jassim
"""

import pymongo
import random
import string

from config import config
from mongodb_ml_models.constants import config_file_name


class GenerateID:
    @staticmethod
    def generate_number(size=32):
        return ''.join([random.choice(string.digits) for n in range(size)])

    @staticmethod
    def generate_char(size=32):
        return ''.join([random.choice(string.ascii_letters) for n in range(size)])

    @staticmethod
    def generate_string(size=32):
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])

    @classmethod
    def generate_collection_id(cls):
        random_str = '-'.join(
            [cls.generate_char(6), cls.generate_number(6), cls.generate_string(6),
             cls.generate_string(6), cls.generate_number(4)])

        return random_str


class MongoDb(object):
    def __init__(self, host: str = None, port: int = None):
        if host is None and port is None:
            config_obj = config(config_file_name=config_file_name)
            host = config_obj.get('mongodb', 'host')
            port = config_obj.get('mongodb', 'port')

        self.client = pymongo.MongoClient(f"mongodb://{host}:{port}")
        self.page_data = dict()

    def insert_data(self, data: dict, db_name: str, collection_name: str):
        data["_id"] = GenerateID.generate_string()
        db = self.client[db_name]
        db_collection = db[collection_name]
        db_collection.insert_one(data)
        print("Mongodb value inserted")

    def get_data(self, select_query: dict, db_name: str, collection_name: str):
        db = self.client[db_name]
        db_collection = db[collection_name]
        db_cursor = db_collection.find(select_query)
        result = []

        for each_data in db_cursor:
            result.append(each_data)

        return result

    def upsert(self, db: str, collection_name: str, query: dict, update: dict):
        """
        Insert data if query not exist, else replace
        :param db: Database name
        :param collection_name: Collection name
        :param query: Select query
        :param update: Insert data
        :return:
        """
        db = self.client[db]
        db_collection = db[collection_name]

        db_collection.replace_one(query, update, True)
