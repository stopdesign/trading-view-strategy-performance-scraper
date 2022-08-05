from pandas import DataFrame

from network import NotifierClient
from utils import ExcelUtils, FileUtils

tmp_folder = "tmp"


def send_data(message: str, entries: DataFrame, file_name: str):
    stored_file_path = __temp_store_file(entries, file_name, tmp_folder)
    attachments = [__build_multipart_file_payload_for_file(file_name, stored_file_path)]
    NotifierClient.send_email(message, attachments)
    FileUtils.delete_folder_with(name=tmp_folder)


def __temp_store_file(entries: DataFrame, file_name: str, folder: str):
    FileUtils.create_folder_with(name=tmp_folder)
    path = f"{folder}/{file_name}"
    ExcelUtils.write_to_excel_from_df(entries, path)
    return path


def __build_multipart_file_payload_for_file(file_name: str, path: str) -> tuple:
    return "files", (file_name, FileUtils.read_file(path),
                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

