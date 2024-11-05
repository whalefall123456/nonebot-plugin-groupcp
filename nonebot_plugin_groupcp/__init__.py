import random
import time

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
        message = Message.template("{}你已经有cp了，对方是{}{}").format(
            MessageSegment.at(user_id), cp_name, MessageSegment.image(cp_img)
        )
        await marry_applicant.finish(message)
    # 如果不存在cp，则从列表中随机选取一个用户，然后将两者组成cp
    else:
        no_cp_list = get_nocp_list(str(group_id))
        if not no_cp_list:
            no_cp_list = await bot.call_api("get_group_member_list", group_id=group_id, no_cache=False)
            no_cp_list = [i["user_id"] for i in no_cp_list]
        if user_id in no_cp_list:
            no_cp_list.remove(user_id)
        # 随机从列表中选取一个用户
        cp_id = random.choice(no_cp_list)
        no_cp_list.remove(cp_id)
        # 获取用户的昵称
        cp_name = (await get_user_info(bot, event, str(cp_id))).user_name
        cp_img = await get_user_img(cp_id)
        # 将两者组成cp
        cp_info = get_cp_info(str(group_id))
        cp_info[str(user_id)] = {"cp_id": str(cp_id), "cp_name": cp_name}
        cp_info[str(cp_id)] = {"cp_id": str(user_id), "cp_name": user_name}
        save_cp_info(str(group_id), cp_info, )
        save_nocp_list(str(group_id), no_cp_list)
        message = Message.template("{}恭喜你娶到了{}{}").format(
            MessageSegment.at(user_id), cp_name, MessageSegment.image(cp_img)
        )
        await marry_applicant.finish(message)


@divorce_applicant.handle()
async def divorce_applicant_handle(bot:Bot, event: GroupMessageEvent):
    """
    与群友解除cp关系
    :param bot:
    :param event:
    :return:
    """
    group_id = event.group_id
    user_id = event.user_id
    user_cp_info = get_user_cp_info(str(group_id), str(user_id))
    # 如果用户存在cp则解除cp关系
    if user_cp_info:
        divorce_dict = get_divorce_list(str(group_id))
        if divorce_dict.get(str(user_id), {}):
            # 检查记录的时间，如果超过3分钟则同意申请并删除记录，否则计算剩余时间
            if time.time() - divorce_dict[str(user_id)] > 180:
                cp_info = get_cp_info(str(group_id))
                no_cp_list = get_nocp_list(str(group_id))
                no_cp_list.append(user_id)
                no_cp_list.append(int(user_cp_info["cp_id"]))
                del cp_info[str(user_id)]
                del cp_info[str(user_cp_info["cp_id"])]
                del divorce_dict[str(user_id)]
                save_cp_info(str(group_id), cp_info)
                save_nocp_list(str(group_id), no_cp_list)
                save_divorce_list(str(group_id), divorce_dict)
                message = Message.template("{}你已经与 {} 解除cp关系").format(MessageSegment.at(user_id),user_cp_info["cp_name"])
                await divorce_applicant.finish(message)
            else:
                remain_time = 180 - int(time.time() - divorce_dict[str(user_id)])
                message = Message.template("{}你已经申请过离婚了，剩余时间{}秒").format(MessageSegment.at(user_id),remain_time)
                await divorce_applicant.finish(message)
        else:
            # 记录申请时间
            divorce_dict[str(user_id)] = time.time()
            save_divorce_list(str(group_id), divorce_dict)
            message = Message.template("{}你已经申请离婚，离婚冷静期为3分钟，请3分钟后尝试").format(MessageSegment.at(user_id))
            await divorce_applicant.finish(message)

    else:
        message = Message.template("{}你还没有cp呢").format(MessageSegment.at(user_id))
        await divorce_applicant.finish(message)



# 使用





