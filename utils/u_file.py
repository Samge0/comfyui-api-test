#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-05-10 13:53
# describe：
import base64
import os


"""
File operation related tool classes, mainly including file reading and writing, saving base 64 as a file, file size, file deletion, etc.
"""


def save_base64(_base64: str, _path: str) -> bool:
    """save base 64 to file"""
    try:
        if exists(_path):
            return True
        filedata = base64.b64decode(_base64.replace('\n', ''))
        with open(_path, "wb") as fh:
            fh.write(filedata)
            fh.close()
        return True
    except Exception as e:
        print(f'save base 64 to file error：{e}')
        return False


def save(_txt: str, _path: str, _type: str = 'w+') -> bool:
    """save file"""
    try:
        with open(_path, _type, encoding='utf-8') as f:
            f.write(_txt)
            f.flush()
            f.close()
        return True
    except:
        return False


def read(_path: str) -> str:
    """read-file"""
    result = read_bytes(_path)
    return str(result, encoding='utf-8') if result else ""


def read_bytes(_path: str) -> bytes:
    """read file bytes information"""
    try:
        if not exists(_path):
            return None
        with open(_path, "rb") as f:
            result = f.read()
            result = result.replace(b'\r\n', b'\n') if result else result
            f.close()
            return result
    except:
        return None


def size(file_path) -> float:
    """read file size unit m"""
    if not exists(file_path):
        return 0
    return os.path.getsize(file_path) / 1024 / 1024


def remove(file_path: str):
    """delete file"""
    try:
        os.remove(file_path)
    except:
        pass


def exists(_path: str) -> bool:
    """
    judge whether there is
    :param _path:
    :return:
    """
    return _path and os.path.exists(_path)


def makedirs(_path: str):
    """
    create a multi tier catalog
    :param _path:
    :return:
    """
    if not exists(_path):
        os.makedirs(_path)


def get_goal_dir(goal_dir_name, dir_path: str = os.path.abspath(__file__)):
    """
    truncates the absolute path of the target directory from a directory string
    :param goal_dir_name: destination directory name
    :param dir_path: Specifies the directory address of the current execution file by default.
    :return:
    """
    if not goal_dir_name or goal_dir_name not in dir_path:
        return None
    _index = dir_path.index(goal_dir_name)
    return f"{dir_path[:_index+len(goal_dir_name)]}"
