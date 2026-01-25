import os
from typing import Dict, Any, List

from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.internal.permission import Permission

from ys_bot.plugins.nonebot_plugin_management.data_handle.data_util import DataUtil


async def check_admin(event: GroupMessageEvent) -> bool:
    """检查用户是否是管理员"""
    group_id = event.group_id
    user_id = event.get_user_id()
    intenddant = IntendantInformation(group_id)
    return intenddant.is_intendant(user_id)


INTENDANT = Permission(check_admin)


class IntendantInformation(DataUtil):
    def __init__(self, group: int):
        data_dir = "../data/intendant_information"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        file_path = os.path.join(data_dir, f"{group}.json")
        super().__init__(file_path)
        self.group = group
        self.create_json()

    @staticmethod
    def init_intendant_data(group: int) -> Dict[str, Any]:
        """初始化管理员信息的 JSON 数据结构"""
        initial_data = {
            "group_id": group,
            "intendant_information": []  # 字符串列表
        }
        return initial_data

    def create_json(self) -> bool:
        """创建 JSON 文件"""
        init_data = self.init_intendant_data(self.group)
        return super().create_json(init_data)

    def load_data(self) -> Dict[str, Any]:
        """加载 JSON 数据"""
        init_data = self.init_intendant_data(self.group)
        return super().load_data(init_data)

    def add_intendant(self, intendant_id: str) -> bool:
        """添加管理员信息"""
        data = self.load_data()
        intendants = data["intendant_information"]

        # 检查是否已存在
        if intendant_id in intendants:
            return False

        intendants.append(intendant_id)
        return self.save_data(data)

    def get_intendants(self) -> List[str]:
        """获取所有管理员信息"""
        data = self.load_data()
        return data.get("intendant_information", [])

    def remove_intendant(self, intendant_id: str) -> bool:
        """根据管理员ID删除信息"""
        data = self.load_data()
        intendants = data.get("intendant_information", [])

        if intendant_id in intendants:
            intendants.remove(intendant_id)
            return self.save_data(data)
        return False

    def is_intendant(self, user_id: str) -> bool:
        """检查用户是否为管理员"""
        data = self.load_data()
        return user_id in data.get("intendant_information", [])
