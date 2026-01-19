import json
import aiohttp
from datetime import datetime
from nonebot import on_request
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupRequestEvent,
    RequestEvent
)
from nonebot.plugin import PluginMetadata
from .config import Config
from nonebot import get_plugin_config

config = get_plugin_config(Config)

# 创建请求处理器
group_request = on_request(priority=1, block=True)


@group_request.handle()
async def handle_group_application(bot: Bot, event: RequestEvent):
    # 只处理群聊相关的请求事件
    if not isinstance(event, GroupRequestEvent):
        return

    # 检查是否启用插件
    if not config.group_application_enable:
        return

    # 检查是否在需要监听的群组列表中
    if config.monitor_groups and str(event.group_id) not in config.monitor_groups:
        return

    # 获取用户信息
    user_id = event.user_id
    group_id = event.group_id
    comment = event.comment if hasattr(event, 'comment') else "无"

    # 获取头像URL
    avatar_url = ""
    if config.show_avatar:
        try:
            avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
        except:
            avatar_url = "获取失败"
    else:
        avatar_url = "未启用"

    # 格式化时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 解析入群答案（通常格式为JSON字符串）
    question_content="无问题内容"
    answer_content = "无答案内容"
    try:
        # 尝试解析JSON格式的评论
        comment_json = json.loads(comment)
        if isinstance(comment_json, dict):
            # 提取答案，根据不同平台格式处理
            if "question" in comment_json:
                question_content = comment_json["question"]
            if "answer" in comment_json:
                answer_content = comment_json["answer"]
        else:
            answer_content = str(comment_json)
    except (json.JSONDecodeError, TypeError, IndexError):
        # 如果不是JSON，直接使用原始评论
        answer_content = comment if comment else "无答案内容"

    # 构建消息
    message = config.application_message.format(
        user_id=user_id,
        question=question_content,
        answer=answer_content,
        avatar_url=avatar_url,
        time=current_time
    )

    message=message+str(event)

    # 发送到群聊
    try:
        await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        # 记录错误但不影响主流程
        print(f"发送入群申请消息失败: {e}")