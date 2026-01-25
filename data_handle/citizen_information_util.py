import os
from typing import Dict, Any, List

from ys_bot.plugins.nonebot_plugin_management.data_handle.data_util import DataUtil


class CitizenInformation(DataUtil):
    def __init__(self, group: int):
        data_dir = "../data/citizen_information"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        file_path = os.path.join(data_dir, f"{group}.json")
        super().__init__(file_path)
        self.group = group
        self.create_json()

    @staticmethod
    def init_citizen_data(group: int) -> Dict[str, Any]:
        """初始化公民信息的 JSON 数据结构"""
        initial_data = {
            "group_id": group,
            "citizen_information": []  # 字符串列表
        }
        return initial_data

    def create_json(self) -> bool:
        """创建 JSON 文件"""
        init_data = self.init_citizen_data(self.group)
        return super().create_json(init_data)

    def load_data(self) -> Dict[str, Any]:
        """加载 JSON 数据"""
        init_data = self.init_citizen_data(self.group)
        return super().load_data(init_data)

    def add_citizen(self, user_id: str) -> bool:
        """添加公民信息"""
        data = self.load_data()
        citizens = data["citizen_information"]

        # 检查是否已存在
        if user_id in citizens:
            return False

        citizens.append(user_id)
        return self.save_data(data)

    def get_citizens(self) -> List[str]:
        """获取所有公民信息"""
        data = self.load_data()
        return data.get("citizen_information", [])

    def remove_citizen(self, user_id: str) -> bool:
        """根据用户ID删除公民信息"""
        data = self.load_data()
        citizens = data.get("citizen_information", [])

        if user_id in citizens:
            citizens.remove(user_id)
            return self.save_data(data)
        return False

    def is_citizen(self, user_id: str) -> bool:
        """检查用户是否为公民"""
        data = self.load_data()
        return user_id in data.get("citizen_information", [])

    def get_citizen_count(self) -> int:
        """获取公民数量"""
        data = self.load_data()
        return len(data.get("citizen_information", []))

    def clear_citizens(self) -> bool:
        """清空公民列表（谨慎使用）"""
        data = self.load_data()
        data["citizen_information"] = []
        return self.save_data(data)
