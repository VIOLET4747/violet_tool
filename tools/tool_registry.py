"""工具注册表 — 从 config.json 加载已启用的工具"""

from tools.fofa_tool import FofaTool
from tools.ehole_tool import EholeTool
from tools.info_collect_tool import InfoCollectTool

# 工具名 → 工具类的映射
TOOL_CLASSES = {
    "fofa": FofaTool,
    "ehole": EholeTool,
    "info_collect": InfoCollectTool,
}


class ToolRegistry:
    """工具注册管理器"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    @staticmethod
    def get_tool_class(tool_name: str):
        """获取工具类（不实例化）"""
        return TOOL_CLASSES.get(tool_name)

    @classmethod
    def get_default_tools_config(cls) -> dict:
        """从所有注册的工具类中提取 default_config"""
        tools_cfg = {}
        for name, tool_cls in TOOL_CLASSES.items():
            cfg = getattr(tool_cls, "default_config", {}).copy()
            if cfg:
                cfg.setdefault("enabled", True)
                tools_cfg[name] = cfg
        return tools_cfg

    def get_enabled_tools(self):
        """获取所有已启用的工具类列表

        Returns:
            [(name, display_name, tool_class), ...]
        """
        enabled_configs = self.config_manager.get_enabled_tools()
        result = []
        for name, cfg in enabled_configs.items():
            cls = TOOL_CLASSES.get(name)
            if cls:
                result.append((name, cls.display_name, cls, cfg))
        return result

    def create_tool_instance(self, tool_name: str, log_callback=None):
        """创建一个工具实例

        Args:
            tool_name: 工具名（如 'fofa'）
            log_callback: 日志回调函数

        Returns:
            BaseTool 实例，或 None
        """
        cls = TOOL_CLASSES.get(tool_name)
        if not cls:
            return None
        cfg = self.config_manager.get_tool_config(tool_name)
        return cls(cfg, log_callback=log_callback)
