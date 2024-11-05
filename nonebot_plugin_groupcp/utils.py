import asyncio
import json

import httpx
from httpx import NetworkError
from nonebot import get_plugin_config, logger
from .config import Config

config = get_plugin_config(Config)

# example = {
#             "group": {
#                 "group_id": {
#                     "cp_info": {
#                         "user_id": {
#                             "cp_id": "user_id",
#                             "cp_name": "user_name",
#                         }
#                     },
#                     "no_cp_list": ["user_id"],
#                     "divorce_list": {"user_id": "time"}
#                 }
#             },
#             "time": "2021-08-01 00:00:00"
# }

async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=10)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                await asyncio.sleep(3)
    raise NetworkError(f"{url} 下载失败！")




def check_file_exist():
    # 检查文件夹是否存在，不存在则创建
    if not config.data_path.exists():
        config.data_path.mkdir(parents=True)
        with open(config.group_data_path, "w", encoding="utf8") as f:
            data = {"group": {}, "time": ""}
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()
    else:
        if not config.group_data_path.exists():
            with open(config.group_data_path, "w", encoding="utf8") as f:
                data = {"group": {}, "time": ""}
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.close()


def get_data():
    """
    获取全部数据
    :return:
    """
    check_file_exist()
    with open(config.group_data_path, "r", encoding="utf8") as f:
        data: dict = json.load(f)
        f.close()
    return data


def save_data(data: dict):
    """
    保存数据
    :param data:
    :return:
    """
    check_file_exist()
    with open(config.group_data_path, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close()
    return True


def get_group_data(group_id: str):
    data = get_data()
    return data.get("group", {}).get(group_id, {})


def save_group_data(group_id: str, group_data: dict):
    data = get_data()
    data["group"][group_id] = group_data
    with open(config.group_data_path, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close()
    return True


def get_user_cp_info(group_id: str, user_id: str):
    group_data = get_group_data(group_id)
    # 判断用户的cp是否为空
    if group_data.get("cp_info", {}).get(user_id):
        return group_data.get("cp_info", {}).get(user_id)
    else:
        return {}


def get_cp_info(group_id: str):
    group_data = get_group_data(group_id)
    return group_data.get("cp_info", {})


def save_cp_info(group_id: str, cp_info: dict):
    group_data = get_group_data(group_id)
    group_data["cp_info"] = cp_info
    # if "cp_info" not in group_data:
    #     group_data["cp_info"] = {user_cp_info["cp_id"]:cp_info, cp_info["cp_id"]:user_cp_info}
    # group_data["cp_info"][user_cp_info["cp_id"]] = cp_info
    # group_data["cp_info"][cp_info["cp_id"]] = user_cp_info
    save_group_data(group_id, group_data)
    return True



async def get_user_img(user_id: str):
    """
    获取用户的qq头像
    :param user_id:
    :return:
    """
    url = f"https://q.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    # 使用requests库获取图片
    img = await download_url(url)
    return img


def get_nocp_list(group_id: str):
    """
    获取没有cp的用户列表
    :param group_id:
    :return:
    """
    group_data = get_group_data(group_id)
    return group_data.get("no_cp_list", [])


def save_nocp_list(group_id: str, no_cp_list: list):
    """
    保存没有cp的用户列表
    :param group_id:
    :param no_cp_list:
    :return:
    """
    group_data = get_group_data(group_id)
    group_data["no_cp_list"] = no_cp_list
    save_group_data(group_id, group_data)
    return True


def get_divorce_list(group_id: str):
    group_data = get_group_data(group_id)
    return group_data.get("divorce_list", {})


def save_divorce_list(group_id: str, divorce_list: dict):
    group_data = get_group_data(group_id)
    group_data["divorce_list"] = divorce_list
    save_group_data(group_id, group_data)
    return True





