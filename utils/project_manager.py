"""项目管理 — 创建/列出/打开项目"""

import os
from datetime import datetime

README_TEMPLATE = """# {project_name}

> 本项目由 violet_tool 自动创建
> 创建时间：{create_time}

## 📁 目录结构

```
{project_name}/
├── 说明.md          ← 本文件（项目说明）
├── 信息/            ← 📊 信息收集目录
│   └── .history/    ← FOFA 查询历史
└── 工作/            ← 💻 AI 工作目录
```

## 📊 信息目录 (`信息/`)

存放所有情报收集结果，包括但不限于：
- FOFA 查询导出结果（CSV / JSON / TXT）
- EHole 指纹识别结果
- 子域名收集结果
- 端口扫描结果
- 其他工具的输出文件

> **AI 工具使用建议**：从此目录读取已有情报进行分析，不要再写入此目录。

## 💻 工作目录 (`工作/`)

存放 AI 助手编写的脚本、代码、临时文件等。
所有代码生成、脚本编写等工作产物存放在此目录。

> **AI 工具使用建议**：在此目录创建和编辑脚本，从 `../信息/` 读取数据。

---

*自动生成于 {create_time}*
"""


class ProjectManager:
    """项目管理器"""

    def __init__(self, config_manager):
        """
        Args:
            config_manager: ConfigManager 实例
        """
        self.config = config_manager

    def create_project(self, project_name: str) -> str:
        """创建新项目文件夹

        Args:
            project_name: 自定义文件夹名

        Returns:
            创建的项目完整路径

        Raises:
            ValueError: 项目已存在
            OSError: 创建目录失败
        """
        base_path = self.config.get_project_base()
        if not base_path:
            raise ValueError("未配置项目路径")

        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)

        project_path = os.path.join(base_path, project_name)

        if os.path.exists(project_path):
            raise ValueError(f"项目已存在: {project_path}")

        # 创建目录结构
        info_dir = os.path.join(project_path, "信息")
        work_dir = os.path.join(project_path, "工作")
        history_dir = os.path.join(info_dir, ".history")

        os.makedirs(info_dir, exist_ok=True)
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(history_dir, exist_ok=True)

        # 生成说明.md
        readme_path = os.path.join(project_path, "说明.md")
        readme_content = README_TEMPLATE.format(
            project_name=project_name,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        return project_path

    def list_projects(self) -> list[dict]:
        """列出所有项目

        Returns:
            [{"name": "阿里云", "path": "d:\\...\\阿里云"}, ...]
        """
        projects = []
        base = self.config.get_project_base()
        if not base or not os.path.isdir(base):
            return projects
        try:
            for entry in os.listdir(base):
                entry_path = os.path.join(base, entry)
                if os.path.isdir(entry_path):
                    projects.append({
                        "name": entry,
                        "path": entry_path,
                    })
        except PermissionError:
            pass

        projects.sort(key=lambda p: p["name"].lower())
        return projects

    def get_info_dir(self, project_path: str) -> str:
        """获取项目的信息目录"""
        return os.path.join(project_path, "信息")

    def get_work_dir(self, project_path: str) -> str:
        """获取项目的工作目录"""
        return os.path.join(project_path, "工作")

    def get_history_dir(self, project_path: str) -> str:
        """获取 FOFA 查询历史目录"""
        return os.path.join(project_path, "信息", ".history")

    def list_info_files(self, project_path: str) -> list[dict]:
        """列出信息目录下的文件（不含隐藏目录）

        Returns:
            [{"name": "xxx.txt", "path": "d:\\...\\xxx.txt", "size": 1234, "mtime": datetime}, ...]
        """
        info_dir = self.get_info_dir(project_path)
        if not os.path.isdir(info_dir):
            return []

        files = []
        try:
            for entry in os.listdir(info_dir):
                if entry.startswith("."):
                    continue
                entry_path = os.path.join(info_dir, entry)
                if os.path.isfile(entry_path):
                    stat = os.stat(entry_path)
                    files.append({
                        "name": entry,
                        "path": entry_path,
                        "size": stat.st_size,
                        "mtime": datetime.fromtimestamp(stat.st_mtime),
                    })
        except PermissionError:
            pass

        files.sort(key=lambda f: f["mtime"], reverse=True)
        return files
