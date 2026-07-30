"""配置读写管理"""

import json
import os

DEFAULT_CONFIG = {
    "paths": {
        "projects": ""
    },
    "ui": {
        "log_visible": True
    }
}


class ConfigManager:
    """配置读写管理器"""

    def __init__(self, config_path: str):
        self.config_path = os.path.abspath(config_path)
        self._config = {}
        self.load()

    def load(self):
        """加载配置，不存在则创建默认配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = DEFAULT_CONFIG.copy()
                self.save()
        else:
            self._config = DEFAULT_CONFIG.copy()
            self.save()

    def save(self):
        """保存配置到文件"""
        dirname = os.path.dirname(self.config_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default=None):
        """获取配置项，支持点号分隔的嵌套 key，如 'fofa.key'"""
        keys = key.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default

    def set(self, key: str, value):
        """设置配置项，支持点号分隔的嵌套 key"""
        keys = key.split(".")
        target = self._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()

    def merge_tool_defaults(self, tool_registry):
        """把所有注册工具的 default_config 合并进 config，不覆盖已有值"""
        changed = False
        if "tools" not in self._config:
            self._config["tools"] = {}
        for name, cfg in tool_registry.get_default_tools_config().items():
            if name not in self._config["tools"]:
                self._config["tools"][name] = cfg
                changed = True
        if changed:
            self.save()

    def get_fofa_key(self) -> str:
        return self.get("tools.fofa.key", "")

    def get_fofa_base_url(self) -> str:
        return self.get("tools.fofa.base_url", "https://fofoapi.com")

    def get_project_base(self) -> str:
        return self.get("paths.projects", "")

    def get_enabled_tools(self) -> dict:
        """返回所有已启用的工具配置"""
        all_tools = self.get("tools", {})
        return {name: cfg for name, cfg in all_tools.items()
                if isinstance(cfg, dict) and cfg.get("enabled", False)}

    def get_tool_config(self, tool_name: str) -> dict:
        """获取指定工具的配置"""
        return self.get(f"tools.{tool_name}", {})
