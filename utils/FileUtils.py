import datetime
import json
import logging
import os
import shutil

from utils import TimeUtils


def read_file(path: str):
    with open(path, 'r') as f:
        content = f.read()
    return content


def write_file(path: str, content):
    with open(path, 'w') as f:
        f.write(content)
    return path


def delete_folder_with(name: str):
    if os.path.exists(name):
        shutil.rmtree(name)


def write_json(path: str, content):
    with open(path, 'w') as f:
        json.dump(content, f, cls=DateTimeEncoder)
    return path


def read_json_from(path: str):
    try:
        if os.path.exists(path):
            content = read_file(path)
            return json.loads(content, object_hook=date_time_decoder_hook)
        else:
            return None
    except Exception as e:
        logging.error(e)
        return None


def create_folder_with(name: str):
    if not os.path.exists(name):
        os.makedirs(name)


def create_folders_with_file(file_name: str, *folders) -> str:
    path_file_and_folders = get_path(file_name, *folders)
    if not os.path.exists(path_file_and_folders):
        with open(path_file_and_folders, "w"):
            pass
    return path_file_and_folders


def get_path(file_name: str, *sub_folders):
    if len(sub_folders) > 0:
        create_folders_for(*sub_folders)
    path = get_path_for(*sub_folders, file_name)
    return path


def get_path_for(*args) -> str:
    return os.path.sep.join(args)


def create_folders_for(*sub_folders):
    os.makedirs(get_path_for(*sub_folders), exist_ok=True)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime):
            return TimeUtils.get_time_stamp_from(z, '%d-%b-%yT%H:%M:%S.%f')
        else:
            return super().default(z)


def date_time_decoder_hook(obj):
    ret = {}
    for key, value in obj.items():
        if key in {'date'}:
            ret[key] = TimeUtils.get_date_from_str(date_str=value, time_format='%d-%b-%yT%H:%M:%S.%f')
        else:
            ret[key] = value
    return ret


def date_decode_to_date_time(obj):
    ret = {}
    time_format = '%d-%b-%yT%H:%M:%S.%f'
    for key, value in obj.items():
        if key in {'date'}:
            ret[key] = TimeUtils.to_UTC_str(time_millis=value, time_format=time_format)
        else:
            ret[key] = value
    ret['receivedAt'] = TimeUtils.get_time_stamp_formatted(time_format=time_format)
    return ret

