from typing import Optional

from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    # 是否启用入群申请处理
    group_application_enable: bool = True
    # 需要监听的群号列表（为空则监听所有群）
    monitor_groups: Optional[list[str]] = None
    # 是否显示头像（设置为False则不获取头像，提高响应速度）
    show_avatar: bool = True
