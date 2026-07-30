"""设置弹窗（通用工具设置 + 项目路径设置）"""

import tkinter as tk
from tkinter import ttk


class GenericToolSettings:
    """通用工具设置对话框"""

    def __init__(self, parent, tool_name: str, config_manager, log_callback=None, on_save=None):
        self.config_manager = config_manager
        self.tool_name = tool_name
        self.log = log_callback or (lambda l, m: None)
        self.on_save = on_save
        cfg = config_manager.get_tool_config(tool_name)

        self.top = tk.Toplevel(parent)
        self.top.title(f"设置 - {tool_name}")
        self.top.geometry("500x200")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self._center(parent)

        frame = ttk.Frame(self.top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"工具: {tool_name}", font=("", 10, "bold")).pack(anchor=tk.W)

        ttk.Label(frame, text="程序路径", font=("", 9)).pack(anchor=tk.W, pady=(10, 3))
        path_row = ttk.Frame(frame)
        path_row.pack(fill=tk.X)
        self.path_var = tk.StringVar(value=cfg.get("path", ""))
        ttk.Entry(path_row, textvariable=self.path_var, font=("Consolas", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_row, text="浏览", command=self._browse).pack(side=tk.LEFT, padx=5)

        ttk.Label(frame, text="启用", font=("", 9)).pack(anchor=tk.W, pady=(10, 3))
        self.enabled_var = tk.BooleanVar(value=cfg.get("enabled", True))
        ttk.Checkbutton(frame, text="启用此工具", variable=self.enabled_var).pack(anchor=tk.W)

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(btn_row, text="保存", command=self._save).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_row, text="取消", command=self.top.destroy).pack(side=tk.RIGHT, padx=2)

    def _center(self, parent):
        self.top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
        self.top.geometry(f"+{x}+{y}")

    def _browse(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")])
        if path:
            self.path_var.set(path)

    def _save(self):
        self.config_manager.set(f"tools.{self.tool_name}.path", self.path_var.get().strip())
        self.config_manager.set(f"tools.{self.tool_name}.enabled", self.enabled_var.get())
        self.log("success", f"{self.tool_name} 配置已保存")
        if self.on_save:
            self.on_save()
        self.top.destroy()


class ProjectPathSettings:
    """项目路径设置"""

    def __init__(self, parent, config_manager, log_callback=None):
        self.config_manager = config_manager
        self.log = log_callback or (lambda l, m: None)

        self.top = tk.Toplevel(parent)
        self.top.title("设置 - 项目路径")
        self.top.geometry("550x180")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 180) // 2
        self.top.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self.top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="日常 SRC 项目基础路径", font=("", 9)).pack(anchor=tk.W, pady=(0, 3))
        self.daily_var = tk.StringVar(value=config_manager.get_project_base("daily"))
        ttk.Entry(frame, textvariable=self.daily_var, font=("Consolas", 10)).pack(fill=tk.X, pady=(0, 12))

        ttk.Label(frame, text="公司项目基础路径", font=("", 9)).pack(anchor=tk.W, pady=(0, 3))
        self.company_var = tk.StringVar(value=config_manager.get_project_base("company"))
        ttk.Entry(frame, textvariable=self.company_var, font=("Consolas", 10)).pack(fill=tk.X)

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(btn_row, text="保存", command=self._save).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_row, text="取消", command=self.top.destroy).pack(side=tk.RIGHT, padx=2)

    def _save(self):
        self.config_manager.set("paths.daily_projects", self.daily_var.get().strip())
        self.config_manager.set("paths.company_projects", self.company_var.get().strip())
        self.log("success", "项目路径已保存")
        self.top.destroy()
