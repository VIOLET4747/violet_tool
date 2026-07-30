"""右侧工具面板容器 — 项目信息 + 可拖拽工具选项卡"""

import os
import tkinter as tk
from tkinter import ttk

from gui.widgets.draggable_notebook import DraggableNotebook
from tools.fofa_tool import FofaTool
from tools.ehole_tool import EholeTool


class ToolPanel(ttk.Frame):
    """右侧面板：项目信息 + 可拖拽排序的工具选项卡"""

    def __init__(self, parent, config_manager, tool_registry,
                 log_callback=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.tool_registry = tool_registry
        self.log = log_callback or (lambda lvl, msg: None)
        self.project_info = None
        self.tool_instances = {}
        self.tool_frames = {}

        self._build_ui()

    def _build_ui(self):
        # ── 项目信息栏 ──
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        self.project_name_label = ttk.Label(info_frame, text="未选择项目",
                                            font=("", 11, "bold"))
        self.project_name_label.pack(anchor=tk.W)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)

        # ── 可拖拽工具选项卡 ──
        self.tool_notebook = DraggableNotebook(self)
        self.tool_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 5))

    def load_project(self, project_info: dict):
        """加载项目，创建工具面板"""
        self.project_info = project_info

        self.project_name_label.config(
            text=f"📁 {project_info['name']} ({project_info['type_label']})")

        # 清除旧工具面板
        for frame in self.tool_frames.values():
            frame.destroy()
        self.tool_frames.clear()
        self.tool_instances.clear()

        for tab in self.tool_notebook.tabs():
            self.tool_notebook.forget(tab)

        enabled_tools = self.tool_registry.get_enabled_tools()
        for tool_name, display_name, tool_cls, tool_cfg in enabled_tools:
            instance = tool_cls(tool_cfg, log_callback=self.log)
            instance.project_path = project_info["path"]

            if isinstance(instance, FofaTool):
                instance.set_credentials(
                    self.config_manager.get_fofa_base_url(),
                    self.config_manager.get_fofa_key(),
                )

            tool_frame = ttk.Frame(self.tool_notebook)
            self.tool_notebook.add(tool_frame, text=display_name)

            ui = instance.get_ui(tool_frame, project_info["path"])
            ui.pack(fill=tk.BOTH, expand=True)

            self.tool_instances[tool_name] = instance
            self.tool_frames[tool_name] = tool_frame

        self.log("info", f"加载项目: {project_info['name']}，可用工具: {len(enabled_tools)}")

    def handle_file_selected(self, filepath: str):
        """接收来自左侧文件树的文件选择"""
        ehole = self.tool_instances.get("ehole")
        if ehole and isinstance(ehole, EholeTool):
            ehole.set_url_file(filepath)
            for i in range(self.tool_notebook.index("end")):
                tab_id = self.tool_notebook.tabs()[i]
                if str(tab_id) == str(self.tool_frames.get("ehole", "")):
                    self.tool_notebook.select(i)
                    break
            self.log("info", f"文件树: 已选中 {os.path.basename(filepath)} 作为 EHole 输入")
        else:
            active_tab = self.tool_notebook.select()
            for name, frame in self.tool_frames.items():
                if str(frame) == active_tab:
                    tool = self.tool_instances.get(name)
                    if hasattr(tool, 'set_url_file'):
                        tool.set_url_file(filepath)
                        self.log("info", f"文件树: 已选中 {os.path.basename(filepath)}")
                    break

    def clear(self):
        """清除所有工具面板（切换回项目列表时）"""
        for frame in self.tool_frames.values():
            frame.destroy()
        self.tool_frames.clear()
        self.tool_instances.clear()
        for tab in self.tool_notebook.tabs():
            self.tool_notebook.forget(tab)

        self.project_name_label.config(text="未选择项目")
