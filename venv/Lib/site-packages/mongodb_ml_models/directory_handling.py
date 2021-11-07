import os
import shutil
from pathlib import Path


class DirectoryHandling:
    @staticmethod
    def remove_directory_with_sub_files(directory_path: str):
        try:
            shutil.rmtree(directory_path)

        except OSError as e:
            print(f"Removing directory {directory_path} failed")

            raise e

    @staticmethod
    def remove_file(file_path: str):
        os.remove(file_path)

    @staticmethod
    def create_directory(directory_path: str, parents=True, exist_ok=True):
        Path(directory_path).mkdir(parents=parents, exist_ok=exist_ok)
