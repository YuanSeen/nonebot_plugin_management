import json
from datetime import datetime
from typing import Optional
from nonebot import on_request, logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupRequestEvent,
    RequestEvent,
    MessageSegment,
    NoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent
)
from nonebot.plugin.on import on_notice

from .config import Config
from nonebot import get_plugin_config

from .data_handle.blacklist_information_util import BlacklistInformation
from .data_handle.invitation_information_util import InvitationInformationUtil

"""
功能：
1、监听入群请求，并群内发送相关信息
2、监听群人员增减，通过邀请进入群里会记录邀请人信息
"""

config = get_plugin_config(Config)

# 创建请求处理器
group_request = on_request(priority=5, block=True)
group_increase_notice = on_notice(priority=5, block=True)
group_decrease_notice = on_notice(priority=5, block=True)


@group_request.handle()
async def handle_group_application(bot: Bot, event: RequestEvent):
    # 只处理群聊相关的请求事件
    if not isinstance(event, GroupRequestEvent):
        return
    # 检查是否启用插件
    if not config.group_application_enable:
        return
    # 检查是否在需要监听的群组列表中
    if config.monitor_groups:
        if str(event.group_id) not in config.monitor_groups:
            return

    # 获取用户信息
    user_id = event.user_id
    group_id = event.group_id
    comment = event.comment if hasattr(event, 'comment') else "无"
    way = event.sub_type

    # 获取头像URL
    avatar_url = ""
    if config.show_avatar:
        try:
            avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
        except Exception as e:
            avatar_url = "获取失败"
            logger.error(f"[入群申请] 获取头像失败: {e}")
    else:
        avatar_url = "未启用"

    # 格式化时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    answer_content = comment if comment else ""
    way = "申请入群" if comment else "邀请入群"

    message = MessageSegment.image(avatar_url) + MessageSegment.text(f"QQ：{user_id}") + MessageSegment.text(
        f"\n时间：{current_time}") + MessageSegment.text(f"\n方式：{way}") + MessageSegment.text(f"\n{answer_content}")

    await bot.send_group_msg(group_id=group_id, message=message)

@group_increase_notice.handle()
async def increase_notice(bot: Bot, event: GroupIncreaseNoticeEvent):
    """处理群成员变动通知"""
    # 检查是否启用插件
    if not config.group_application_enable:
        return
    # 群成员增加事件
    user_id = event.user_id
    group_id = event.group_id

    operator_id = getattr(event, 'operator_id', 0)

    # 群成员邀请信息记录器
    util = InvitationInformationUtil(group=group_id)
    util_black = BlacklistInformation(group_id)

    # 检查是否在需要监听的群组列表中
    if config.monitor_groups:
        if str(group_id) not in config.monitor_groups:
            return

    #确认是否是黑名单内，是->移除群聊，结束当前处理
    if util_black.is_in_blacklist(str(user_id)):
        await bot.set_group_kick(group_id=group_id, user_id=user_id)
        return

    # 获取头像URL
    avatar_url = ""
    if config.show_avatar:
        try:
            avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
        except Exception as e:
            avatar_url = "获取失败"
            logger.error(f"[群成员变动] 获取头像失败: {e}")
    else:
        avatar_url = "未启用"

    # 格式化时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 判断增加类型
    if event.sub_type == "approve":
        # 管理员同意入群
        way = "同意申请入群"
        operator_text = f"\n操作人：{operator_id}" if operator_id else ""
    elif event.sub_type == "invite":
        # 邀请入群
        way = "邀请入群"
        operator_text = f"\n邀请人：{operator_id}" if operator_id else ""
        util.add_invitation(f"{user_id}",f"{operator_id}")
    else:
        way = "未知方式入群"
        operator_text = ""

    message = MessageSegment.image(avatar_url) + MessageSegment.text(f"QQ：{user_id}") + MessageSegment.text(
        f"\n时间：{current_time}") + MessageSegment.text(f"\n方式：{way}") + MessageSegment.text(operator_text)

    await bot.send_group_msg(group_id=group_id, message=message)

@group_decrease_notice.handle()
async def decrease_notice(bot: Bot, event: GroupDecreaseNoticeEvent):
    """处理群成员变动通知"""
    # 检查是否启用插件
    if not config.group_application_enable:
        return
    # 群成员减少事件
    user_id = event.user_id
    group_id = event.group_id
    operator_id = getattr(event, 'operator_id', 0)

    # 初始化记录器
    util = BlacklistInformation(group_id)

    # 检查是否在需要监听的群组列表中
    if config.monitor_groups:
        if str(group_id) not in config.monitor_groups:
            return

    # 获取头像URL
    avatar_url = ""
    if config.show_avatar:
        try:
            avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
        except Exception as e:
            avatar_url = "获取失败"
            logger.error(f"[群成员变动] 获取头像失败: {e}")
    else:
        avatar_url = "未启用"

    # 格式化时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 判断减少类型
    if event.sub_type == "leave":
        # 主动退群
        way = "主动退群"
        operator_text = ""
    elif event.sub_type == "kick":
        # 被踢出群
        if util.is_in_blacklist(str(user_id)):
            #是否为机器人按照黑名单驱逐
            way = "发现黑名单"
            operator_text = "驱逐"
        else:
            way = "被踢出群，"
            operator_text = f"已拉进黑名单\n操作人：{operator_id}" if operator_id else ""
            util.add_to_blacklist(str(user_id))
    else:
        way = "未知方式离开"
        operator_text = ""

    message = MessageSegment.image(avatar_url) + MessageSegment.text(f"QQ：{user_id}") + MessageSegment.text(
        f"\n时间：{current_time}") + MessageSegment.text(f"\n方式：{way}") + MessageSegment.text(operator_text)

    await bot.send_group_msg(group_id=group_id, message=message)
