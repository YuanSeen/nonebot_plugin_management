import json
import os
from datetime import datetime
from typing import Dict, Any, List

class InvitationInformationUtil:
    def __init__(self, group):

        data_dir = "../data/invitation_information"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        file_path = os.path.join(data_dir, f"{group}.json")
        self.file_path = file_path
        self.group = group


    @staticmethod
    def init_data(group: int) -> Dict[str, Any]:
        """初始化 JSON 数据结构"""
        initial_data = {
            "group_id": group,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "invitation_information": []
        }
        return initial_data

    def create_json(self) -> bool:
        """创建 JSON 文件"""
        try:
            # 如果文件已存在，先备份或跳过
            if os.path.exists(self.file_path):
                return False

            data = self.init_data(self.group)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"创建文件失败: {e}")
            return False

    def load_data(self) -> Dict[str, Any]:
        """加载 JSON 数据"""
        try:
            if not os.path.exists(self.file_path):
                # 如果文件不存在，先创建
                self.create_json()

            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载数据失败: {e}")
            return self.init_data(self.group)

    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存数据到 JSON 文件"""
        try:
            # 更新最后修改时间
            data["last_update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False

    def add_invitation(self, inviter,invitee) -> bool:
        """添加邀请信息"""
        data = self.load_data()
        invitation_data ={f"{invitee}":f"{inviter}"}
        data["invitation_information"].append(invitation_data)
        return self.save_data(data)

    def get_invitations(self) -> List[Dict[str, Any]]:
        """获取所有邀请信息"""
        data = self.load_data()
        return data.get("invitation_information", [])


# 使用示例
if __name__ == "__main__":
    # 创建工具实例
    util = InvitationInformationUtil(group=123456)

    # 创建 JSON 文件
    util.create_json()


    util.add_invitation("3334286764","2714267540")

    # 获取所有邀请信息
    invitations = util.get_invitations()
    print(f"邀请数量: {len(invitations)}")


    # 查看文件内容
    data = util.load_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))