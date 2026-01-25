# invitation_information_util.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from ys_bot.plugins.nonebot_plugin_management.data_handle.data_util import DataUtil


class InvitationInformationUtil(DataUtil):
    def __init__(self, group: int):
        data_dir = "../data/invitation_information"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        file_path = os.path.join(data_dir, f"{group}.json")
        super().__init__(file_path)
        self.group = group
        self.create_json()

    @staticmethod
    def init_invitation_data(group: int) -> Dict[str, Any]:
        """初始化邀请信息的 JSON 数据结构"""
        initial_data = {
            "group_id": group,
            "invitation_information": []
        }
        return initial_data

    def create_json(self) -> bool:
        """创建 JSON 文件"""
        init_data = self.init_invitation_data(self.group)
        return super().create_json(init_data)

    def load_data(self) -> Dict[str, Any]:
        """加载 JSON 数据"""
        init_data = self.init_invitation_data(self.group)
        return super().load_data(init_data)

    def add_invitation(self, inviter: str, invitee: str) -> bool:
        """添加邀请信息"""
        data = self.load_data()
        invitation_data = {invitee: inviter}
        data["invitation_information"].append(invitation_data)
        return self.save_data(data)

    def get_invitations(self) -> List[Dict[str, Any]]:
        """获取所有邀请信息"""
        data = self.load_data()
        return data.get("invitation_information", [])

    def get_inviter(self, invitee: str) -> Optional[str]:
        """根据被邀请者查找邀请者"""
        invitations = self.get_invitations()
        for invitation in invitations:
            if invitee in invitation:
                return invitation[invitee]
        return None

    def remove_invitation_by_invitee(self, invitee: str) -> bool:
        """根据被邀请者删除邀请信息"""
        data = self.load_data()
        invitations = data.get("invitation_information", [])

        # 过滤掉包含该被邀请者的条目
        updated_invitations = [
            inv for inv in invitations
            if invitee not in inv
        ]

        if len(updated_invitations) != len(invitations):
            data["invitation_information"] = updated_invitations
            return self.save_data(data)
        return False


# 使用示例
if __name__ == "__main__":
    # 创建工具实例
    util = InvitationInformationUtil(group=123456)

    # 创建 JSON 文件
    util.create_json()

    # 添加邀请信息
    util.add_invitation("3334286764", "2714267540")

    # 查找邀请者
    inviter = util.get_inviter("2714267540")
    print(f"邀请者: {inviter}")

    # 获取所有邀请信息
    invitations = util.get_invitations()
    print(f"邀请数量: {len(invitations)}")

    # 查看文件内容
    data = util.load_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # 删除邀请信息
    util.remove_invitation_by_invitee("2714267540")
    print("删除后邀请数量:", len(util.get_invitations()))