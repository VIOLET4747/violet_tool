"""新建项目弹窗"""

import tkinter as tk
from tkinter import ttk, messagebox


class NewProjectDialog:

    def __init__(self, parent):
        self.result = None

        self.top = tk.Toplevel(parent)
        self.top.title("新建项目")
        self.top.geometry("400x140")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.top.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = parent.winfo_rootx() + (pw - 400) // 2 if pw > 0 else 0
        y = parent.winfo_rooty() + (ph - 140) // 2 if ph > 0 else 0
        self.top.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self.top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="项目名称:", font=("", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.name_var, font=("", 11))
        entry.pack(fill=tk.X, pady=(0, 10))
        entry.focus_set()
        entry.bind("<Return>", lambda e: self._confirm())

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="确定", command=self._confirm).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_row, text="取消", command=self.top.destroy).pack(side=tk.RIGHT, padx=2)

    def _confirm(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入项目名称")
            return
        if any(c in name for c in '<>:"/\\|?*'):
            messagebox.showwarning("提示", "项目名不能包含特殊字符")
            return
        self.result = name
        self.top.destroy()
