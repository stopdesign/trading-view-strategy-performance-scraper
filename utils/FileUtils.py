import os
import shutil


def read_file(path: str):
    with open(path, 'r') as f:
        content = f.read()
    return content


def create_folder_with(name: str):
    if not os.path.exists(name):
        os.makedirs(name)


def delete_folder_with(name: str):
    if os.path.exists(name):
        shutil.rmtree(name)
