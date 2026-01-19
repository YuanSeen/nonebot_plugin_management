import json
from datetime import datetime
from nonebot import on_request, logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupRequestEvent,
    RequestEvent, MessageSegment
)
from .config import Config
from nonebot import get_plugin_config

config = get_plugin_config(Config)

# 创建请求处理器
group_request = on_request(priority=5, block=True)


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
    if way == "add":
        way = "申请加入"
    elif way == "invite":
        way = "邀请加入"

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

    answer_content = comment if comment else "无答案内容"

    message = MessageSegment.image(avatar_url)+MessageSegment.text(f"QQ：{user_id}")+MessageSegment.text(f"\n{answer_content}")+MessageSegment.text(f"\n时间：{current_time}")+MessageSegment.text(f"\n方式：{way}")


    await bot.send_group_msg(group_id=group_id, message=message)
