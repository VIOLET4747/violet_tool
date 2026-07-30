"""FOFA 查询历史管理"""

import json
import os


class HistoryManager:
    """管理每个项目的 FOFA 查询历史（最近 N 条）"""

    MAX_HISTORY = 10

    def __init__(self, history_dir: str):
        """
        Args:
            history_dir: 历史文件存放目录（通常为 {项目}/信息/.history/）
        """
        self.history_dir = history_dir
        self.history_file = os.path.join(history_dir, "fofa_queries.json")
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(self.history_dir, exist_ok=True)

    def load(self) -> list[str]:
        """加载查询历史

        Returns:
            查询语法字符串列表，最近的在前面
        """
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data[:self.MAX_HISTORY]
        except (json.JSONDecodeError, IOError):
            pass
        return []

    def save(self, history: list[str]):
        """保存查询历史"""
        self._ensure_dir()
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history[:self.MAX_HISTORY], f, ensure_ascii=False, indent=2)

    def add(self, query: str):
        """添加一条查询记录

        Args:
            query: FOFA 查询语法
        """
        query = query.strip()
        if not query:
            return
        history = self.load()
        # 去重：如果已存在则移到最前面
        if query in history:
            history.remove(query)
        history.insert(0, query)
        # 保持最多 MAX_HISTORY 条
        self.save(history[:self.MAX_HISTORY])

    def clear(self):
        """清空历史"""
        self.save([])
