"""主窗口 — 项目选择 → 工作台"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from gui.left_panel import LeftPanel
from gui.tool_panel import ToolPanel
from gui.widgets.log_bar import LogBar
from gui.project_panel import NewProjectDialog
from utils.config_manager import ConfigManager
from utils.project_manager import ProjectManager
from tools.tool_registry import ToolRegistry


class MainWindow:
    APP_TITLE = "violet_tool - 渗透测试工作流"
    MIN_WIDTH = 1020
    MIN_HEIGHT = 680

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.APP_TITLE)
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        config_path = self._get_config_path()
        self.config_manager = ConfigManager(config_path)
        self.tool_registry = ToolRegistry(self.config_manager)
        self.config_manager.merge_tool_defaults(self.tool_registry)
        self.project_manager = ProjectManager(self.config_manager)

        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = max(self.MIN_WIDTH, int(sw * 0.7)), max(self.MIN_HEIGHT, int(sh * 0.75))
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        self.current_project = None
        self._dyn_widgets = []

        # 底部
        self.log_bar = LogBar(self.root)
        self.log_bar.pack(fill=tk.X, side=tk.BOTTOM)
        if not self.config_manager.get("ui.log_visible", True):
            self.log_bar.toggle_visibility()

        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.log_toggle_btn = ttk.Button(self.status_bar, text="▸ 显示日志",
                                         command=self._toggle_log, width=12)
        self.log_toggle_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        ttk.Label(self.status_bar, text="violet_tool v1.0", foreground="gray",
                  font=("", 8)).pack(side=tk.LEFT, padx=5)
        self._sync_log_text()

        self._show_project_selection()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._check_config()
        self._log("info", "violet_tool 启动完成")

    # ═══════════════ 项目选择 ═══════════════

    def _show_project_selection(self):
        self._destroy_dyn()
        self.current_project = None

        f = ttk.Frame(self.root)
        f.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self._register(f)

        ttk.Label(f, text="violet_tool", font=("", 20, "bold")).pack(pady=(30, 5))
        ttk.Label(f, text="选择一个项目开始工作", foreground="gray", font=("", 10)).pack()

        btns = ttk.Frame(f)
        btns.pack(pady=(5, 10))
        ttk.Button(btns, text="＋ 新建项目", command=self._new_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="⚙ 系统设置", command=self._open_project_settings).pack(side=tk.LEFT, padx=5)

        list_f = ttk.Frame(f)
        list_f.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        self._build_project_list(list_f)

    def _build_project_list(self, parent):
        for c in parent.winfo_children():
            c.destroy()

        projects = self.project_manager.list_projects()
        if not projects:
            ttk.Label(parent, text="还没有项目，点击「新建项目」开始",
                      foreground="gray", font=("", 11)).pack(expand=True)
            return

        for p in projects:
            btn = ttk.Button(parent, text=f"  {p['name']}",
                             command=lambda proj=p: self._open_project(proj))
            btn.pack(fill=tk.X, pady=2)

    def _open_project(self, project_info):
        self.current_project = project_info
        self._show_workbench()

    def _new_project(self):
        dlg = NewProjectDialog(self.root)
        self.root.wait_window(dlg.top)
        if dlg.result:
            try:
                self.project_manager.create_project(dlg.result)
                self._log("success", f"创建项目: {dlg.result}")
                self._show_project_selection()
            except Exception as e:
                messagebox.showerror("创建失败", str(e))

    # ═══════════════ 工作台 ═══════════════

    def _show_workbench(self):
        self._destroy_dyn()
        self._build_menu()

        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=tk.X, side=tk.TOP, padx=5, pady=3)
        self._register(top_bar)
        ttk.Button(top_bar, text="← 项目列表", command=self._back_to_selection).pack(side=tk.LEFT)
        if self.current_project:
            ttk.Label(top_bar, text=f"  📁 {self.current_project['name']}",
                      font=("", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self._sync_log_text()

        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        paned.configure(opaqueresize=False)
        paned.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self._register(paned)

        self.left_panel = LeftPanel(paned, on_file_selected=self._on_file_selected, log_callback=self._log)
        self.tool_panel = ToolPanel(paned, self.config_manager, self.tool_registry, log_callback=self._log)

        paned.add(self.left_panel, minsize=200, stretch="never")
        paned.add(self.tool_panel, minsize=400, stretch="always")

        self.left_panel.load_project(self.current_project)
        self.tool_panel.load_project(self.current_project)
        self._log("info", f"打开项目: {self.current_project['name']}")

    def _back_to_selection(self):
        self.tool_panel.clear()
        self._show_project_selection()
        self._log("info", "返回项目列表")

    # ═══════════════ 菜单 ═══════════════

    def _build_menu(self):
        self._menu = tk.Menu(self.root)

        plugins = tk.Menu(self._menu, tearoff=0)
        plugins.add_command(label="FOFA API 配置", command=lambda: self._open_tool_settings("fofa"))
        plugins.add_command(label="EHole 配置", command=lambda: self._open_tool_settings("ehole"))
        plugins.add_command(label="基础信息探测配置", command=lambda: self._open_tool_settings("info_collect"))
        self._menu.add_cascade(label="插件配置", menu=plugins)

        system = tk.Menu(self._menu, tearoff=0)
        system.add_command(label="项目路径", command=self._open_project_settings)
        self._menu.add_cascade(label="系统设置", menu=system)

        help_menu = tk.Menu(self._menu, tearoff=0)
        help_menu.add_command(label="关于 violet_tool", command=self._show_about)
        self._menu.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=self._menu)

    def _open_tool_settings(self, tool_name="fofa"):
        cls = ToolRegistry.get_tool_class(tool_name)
        if cls and hasattr(cls, 'open_settings'):
            cls.open_settings(self.root, self.config_manager, self._log, on_save=self._reload_tools)
        else:
            from gui.settings_dialogs import GenericToolSettings
            GenericToolSettings(self.root, tool_name, self.config_manager, self._log, on_save=self._reload_tools)

    def _open_project_settings(self):
        from gui.settings_dialogs import ProjectPathSettings
        ProjectPathSettings(self.root, self.config_manager, self._log)

    def _reload_tools(self):
        if self.current_project and hasattr(self, 'tool_panel') and self.tool_panel:
            self.tool_panel.load_project(self.current_project)
            self._log("info", "配置已生效")

    def _show_about(self):
        messagebox.showinfo("关于 violet_tool", "violet_tool - 渗透测试工作流\n\n整合 FOFA API 查询、EHole 指纹识别等工具\nv1.0")

    # ═══════════════ 辅助 ═══════════════

    def _register(self, widget):
        self._dyn_widgets.append(widget)

    def _destroy_dyn(self):
        for w in self._dyn_widgets:
            try:
                w.pack_forget() if w.winfo_exists() else None
            except Exception:
                pass
            try:
                w.destroy() if w.winfo_exists() else None
            except Exception:
                pass
        self._dyn_widgets.clear()

    def _on_file_selected(self, filepath):
        self.tool_panel.handle_file_selected(filepath)

    def _toggle_log(self):
        self.log_bar.toggle_visibility()
        self._sync_log_text()

    def _sync_log_text(self):
        if hasattr(self, 'log_toggle_btn'):
            self.log_toggle_btn.config(text="▾ 隐藏日志" if self.log_bar.visible else "▸ 显示日志")

    def _check_config(self):
        if not self.config_manager.get_fofa_key():
            self._log("warning", "FOFA API Key 未设置，请在 插件配置→FOFA API 配置 中设置")
        if not self.config_manager.get_project_base():
            self._log("warning", "项目路径未设置，请在 系统设置→项目路径 中设置")

    @staticmethod
    def _get_config_path():
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "config.json")

    def _log(self, level, message):
        self.log_bar.log(message, level)

    def _on_close(self):
        self.config_manager.set("ui.log_visible", self.log_bar.visible)
        self.root.destroy()

    def run(self):
        self.root.mainloop()
