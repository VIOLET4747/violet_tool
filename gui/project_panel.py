"""新建项目弹窗"""

import tkinter as tk
from tkinter import ttk, messagebox


class NewProjectDialog:
    """新建项目弹窗"""

    def __init__(self, parent):
        self.result = None

        self.top = tk.Toplevel(parent)
        self.top.title("新建项目")
        self.top.geometry("380x180")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        # 居中
        self.top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 380) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 180) // 2
        self.top.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # 项目类型
        ttk.Label(frame, text="项目类型:", font=("", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.type_var = tk.StringVar(value="daily")
        type_frame = ttk.Frame(frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(type_frame, text="📂 日常SRC项目", variable=self.type_var,
                        value="daily").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="🏢 公司项目", variable=self.type_var,
                        value="company").pack(side=tk.LEFT, padx=(20, 0))

        # 项目名称
        ttk.Label(frame, text="项目名称:", font=("", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=self.name_var, font=("", 11))
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus_set()
        name_entry.bind("<Return>", lambda e: self._confirm())

        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=self._confirm).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_frame, text="取消", command=self.top.destroy).pack(side=tk.RIGHT, padx=2)

    def _confirm(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入项目名称")
            return
        # 检查非法字符
        illegal_chars = '<>:"/\\|?*'
        if any(c in name for c in illegal_chars):
            messagebox.showwarning("提示", f"项目名不能包含以下字符: {illegal_chars}")
            return
        self.result = (self.type_var.get(), name)
        self.top.destroy()
