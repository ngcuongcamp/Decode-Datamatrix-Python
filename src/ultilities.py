import datetime
import configparser
import os
import shutil
import time
import logging


config = configparser.ConfigParser()
config.read("./configs/configApp.ini")


config_update = configparser.ConfigParser()
config_update.read("./configs/config.ini")


def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def format_current_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H-%M-%S")
    return formatted_time


def create_daily_folders():
    path = config["PATH"]["IMAGE_NG_DIR"]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(path, current_date)
    for camera_folder in ["CAMERA1", "CAMERA2"]:
        os.makedirs(os.path.join(folder_path, camera_folder), exist_ok=True)


def handle_remove_old_folders():
    folder_to_keep = int(config["PATH"]["FOLDER_TO_KEEP"])
    path = config["PATH"]["IMAGE_NG_DIR"]
    subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
    subfolders.sort()
    if len(subfolders) > folder_to_keep:
        folders_to_delete = subfolders[: len(subfolders) - folder_to_keep]
        for folder_to_delete in folders_to_delete:
            try:
                shutil.rmtree(folder_to_delete)
                print(f"Removed old folder: {folder_to_delete}")
            except Exception as e:
                print(f"Remove error '{folder_to_delete}': {e}")


def setup_logger():
    path_dir_log = "./logs/"
    time_day = time.strftime("%Y_%m_%d")
    logger = logging.getLogger("MyLogger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(f"{path_dir_log}{time_day}.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return logger


# running when start program

handle_remove_old_folders()
create_daily_folders()
logger = setup_logger()
