"""底部可隐藏日志栏"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class LogBar(ttk.Frame):
    """底部日志栏，支持显示/隐藏、不同级别日志"""

    MAX_LINES = 200
    LEVEL_COLORS = {
        "info": "black",
        "success": "green",
        "warning": "orange",
        "error": "red",
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.visible = True
        self._build_ui()

    def _build_ui(self):
        # 工具栏（始终显示，不随日志隐藏）
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(toolbar, text="📋 日志", font=("", 9, "bold")).pack(side=tk.LEFT, padx=5)

        ttk.Button(toolbar, text="清空", width=6,
                   command=self.clear).pack(side=tk.RIGHT, padx=2)

        # 日志内容区（可隐藏）
        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.X, side=tk.TOP)

        # 文本框
        self.text = tk.Text(self.content, height=4, wrap=tk.WORD, state=tk.DISABLED,
                            font=("Consolas", 9), bg="#f8f8f8", relief=tk.SUNKEN, borderwidth=1)
        self.text.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))

        # 滚动条
        scrollbar = ttk.Scrollbar(self.text, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)

        # 右键菜单
        self.context_menu = tk.Menu(self.text, tearoff=0)
        self.context_menu.add_command(label="清空日志", command=self.clear)
        self.context_menu.add_command(label="复制选中", command=self._copy_selected)
        self.text.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _copy_selected(self):
        try:
            selected = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected:
                self.text.clipboard_clear()
                self.text.clipboard_append(selected)
        except tk.TclError:
            pass

    def log(self, message: str, level: str = "info"):
        """添加一条日志

        Args:
            message: 日志内容
            level: 'info' | 'success' | 'warning' | 'error'
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = self.LEVEL_COLORS.get(level, "black")

        # 创建 tag（如果不存在）
        tag_name = f"level_{level}"
        if tag_name not in self.text.tag_names():
            self.text.tag_configure(tag_name, foreground=color)

        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, f"[{timestamp}] ", ("time",))
        self.text.insert(tk.END, f"{message}\n", (tag_name,))

        # 限制行数
        line_count = int(self.text.index("end-1c").split(".")[0])
        if line_count > self.MAX_LINES:
            excess = line_count - self.MAX_LINES
            self.text.delete("1.0", f"{excess + 1}.0")

        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

        # 配置时间 tag
        if "time" not in self.text.tag_names():
            self.text.tag_configure("time", foreground="gray")

    def info(self, message: str):
        self.log(message, "info")

    def success(self, message: str):
        self.log(message, "success")

    def warning(self, message: str):
        self.log(message, "warning")

    def error(self, message: str):
        self.log(message, "error")

    def clear(self):
        """清空日志"""
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.configure(state=tk.DISABLED)

    def toggle_visibility(self):
        """切换显示/隐藏日志（按钮栏始终保留）"""
        if self.visible:
            self.content.pack_forget()
            self.visible = False
        else:
            self.content.pack(fill=tk.X, side=tk.TOP)
            self.visible = True
