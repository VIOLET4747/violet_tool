"""工具基类 — 所有工具必须实现此接口"""

import tkinter as tk


class BaseTool:
    """工具基类，定义统一接口。

    新增工具：
    1. 继承 BaseTool，实现 get_ui() 方法
    2. 在 tool_registry.py 的 TOOL_CLASSES 中注册
    3. 设置 default_config 类属性

    配置会自动合并，首次运行时生成 config.json
    """

    name: str = "base"
    display_name: str = "Base"
    default_config: dict = {}  # 子类定义默认配置，自动写入 config.json

    def __init__(self, config: dict, log_callback=None):
        """
        Args:
            config: 工具的配置字典
            log_callback: callable(level, message)，用于写入日志栏
        """
        self.config = config
        self.log = log_callback or (lambda lvl, msg: None)

    def get_ui(self, parent: tk.Widget, project_path: str) -> tk.Widget:
        """返回工具的面板 UI

        Args:
            parent: 父容器
            project_path: 当前项目的路径

        Returns:
            工具面板的 tk Widget
        """
        raise NotImplementedError("子类必须实现 get_ui()")
