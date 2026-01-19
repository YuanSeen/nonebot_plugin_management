from pydantic import BaseModel
from typing import Optional


class Config(BaseModel):
    """Plugin Config Here"""
    # 是否启用入群申请处理
    group_application_enable: bool = True
    # 需要监听的群号列表（为空则监听所有群）
    monitor_groups: Optional[list[str]] = None
    # 入群申请消息模板
    application_message: str = "收到入群申请\nQQ：{user_id}\n问题:{question}\n答案：{answer}\n头像：{avatar_url}\n时间：{time}"
    # 是否显示头像（设置为False则不获取头像，提高响应速度）
    show_avatar: bool = True