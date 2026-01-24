# data_util.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class DataUtil:
    def __init__(self, file_path: str):
        self.file_path = file_path

    @staticmethod
    def init_data(init_data: Dict[str, Any]) -> Dict[str, Any]:
        """初始化 JSON 数据结构"""
        init_data.update({
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        return init_data

    def create_json(self, init_data: Dict[str, Any]) -> bool:
        """创建 JSON 文件"""
        try:
            if os.path.exists(self.file_path):
                return False

            data = self.init_data(init_data)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"创建文件失败: {e}")
            return False

    def load_data(self, init_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """加载 JSON 数据"""
        try:
            if not os.path.exists(self.file_path):
                if init_data is not None:
                    self.create_json(init_data)
                else:
                    return {}

            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载数据失败: {e}")
            return init_data or {}

    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存数据到 JSON 文件"""
        try:
            data["last_update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False

    def update_field(self, field_name: str, value: Any) -> bool:
        """更新指定字段的值"""
        data = self.load_data()
        data[field_name] = value
        return self.save_data(data)

    def get_field(self, field_name: str, default: Any = None) -> Any:
        """获取指定字段的值"""
        data = self.load_data()
        return data.get(field_name, default)

    def delete_field(self, field_name: str) -> bool:
        """删除指定字段"""
        data = self.load_data()
        if field_name in data:
            del data[field_name]
            return self.save_data(data)
        return True