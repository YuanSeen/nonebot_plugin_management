import os
from typing import Dict, Any, List

from ys_bot.plugins.nonebot_plugin_management.data_handle.data_util import DataUtil


class BlacklistInformation(DataUtil):
    def __init__(self, group: int):
        data_dir = "../data/blacklist_information"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        file_path = os.path.join(data_dir, f"{group}.json")
        super().__init__(file_path)
        self.group = group
        self.create_json()

    @staticmethod
    def init_blacklist_data(group: int) -> Dict[str, Any]:
        """初始化黑名单信息的 JSON 数据结构"""
        initial_data = {
            "group_id": group,
            "blacklist_information": []  # 字符串列表
        }
        return initial_data

    def create_json(self) -> bool:
        """创建 JSON 文件"""
        init_data = self.init_blacklist_data(self.group)
        return super().create_json(init_data)

    def load_data(self) -> Dict[str, Any]:
        """加载 JSON 数据"""
        init_data = self.init_blacklist_data(self.group)
        return super().load_data(init_data)

    def add_to_blacklist(self, user_id: str) -> bool:
        """添加用户到黑名单"""
        data = self.load_data()
        blacklist = data["blacklist_information"]

        # 检查是否已存在
        if user_id in blacklist:
            return False

        blacklist.append(user_id)
        return self.save_data(data)

    def get_blacklist(self) -> List[str]:
        """获取所有黑名单用户"""
        data = self.load_data()
        return data.get("blacklist_information", [])

    def remove_from_blacklist(self, user_id: str) -> bool:
        """从黑名单中移除用户"""
        data = self.load_data()
        blacklist = data.get("blacklist_information", [])

        if user_id in blacklist:
            blacklist.remove(user_id)
            return self.save_data(data)
        return False

    def is_in_blacklist(self, user_id: str) -> bool:
        """检查用户是否在黑名单中"""
        data = self.load_data()
        return user_id in data.get("blacklist_information", [])

    def clear_blacklist(self) -> bool:
        """清空黑名单"""
        data = self.load_data()
        data["blacklist_information"] = []
        return self.save_data(data)
