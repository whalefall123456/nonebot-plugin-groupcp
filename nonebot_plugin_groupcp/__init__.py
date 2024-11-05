import random

from nonebot import get_plugin_config, require
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_message, on_command
from nonebot.adapters.onebot.v11 import Message, Event, MessageEvent, MessageSegment, GroupMessageEvent,Bot
from nonebot_plugin_userinfo import get_user_info

require("nonebot_plugin_userinfo")

from .config import Config
from .utils import *

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-groupcp",
    description="娶群友，和群友组cp",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
# 初始化数据
check_file_exist()

marry_applicant = on_command("娶群友", priority=10, block=False)
divorce_applicant = on_command("离婚", priority=10, block=False)


@marry_applicant.handle()
async def marry_applicant_handle(bot:Bot, event: GroupMessageEvent):
    # 从事件中取出群号，以及用户id
    group_id = event.group_id
    user_id = event.user_id
    user_name = event.sender.nickname
    # 读取该群的cp信息，，判断用户是否存在cp
    cp_info = get_user_cp_info(str(group_id), str(user_id))
    if cp_info:
        # 如果存在cp，则提示用户已经有cp了,并返回cp的信息
        # cp_nickname = bot.call_api("get_group_member_info", group_id=group_id, user_id=cp_info["cp_id"])["card"]
        cp_name = cp_info["cp_name"]
        cp_img = await get_user_img(cp_info["cp_id"])
        message = Message.template("你已经有cp了，对方是{}{}").format(
            cp_name, MessageSegment.image(cp_img)
        )
        await marry_applicant.finish(message)
    # 如果不存在cp，则从列表中随机选取一个用户，然后将两者组成cp
    else:
        no_cp_list = get_nocp_list(str(group_id))
        if not no_cp_list:
            no_cp_list = await bot.call_api("get_group_member_list", group_id=group_id, no_cache=False)
            no_cp_list = [i["user_id"] for i in no_cp_list]
        no_cp_list.remove(user_id)
        # 随机从列表中选取一个用户
        cp_id = random.choice(no_cp_list)
        no_cp_list.remove(cp_id)
        # 获取用户的昵称
        cp_name = (await get_user_info(bot, event, str(cp_id))).user_name
        cp_img = await get_user_img(cp_id)
        # 将两者组成cp
        save_cp_info(str(group_id), {"cp_id": str(user_id), "cp_name": user_name}, {"cp_id": str(cp_id), "cp_name": cp_name}, no_cp_list)
        message = Message.template("恭喜你娶到了{}{}").format(
            cp_name, MessageSegment.image(cp_img)
        )
        await marry_applicant.finish(message)


@divorce_applicant.handle()
async def divorce_applicant_handle(bot:Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id
    user_cp_info = get_user_cp_info(str(group_id), str(user_id))
    if user_cp_info:



