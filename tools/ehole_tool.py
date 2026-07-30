"""EHole 指纹识别工具 — 打开 CMD 手动运行，粘贴结果后自动保存"""

import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from tools.base_tool import BaseTool


class EholeTool(BaseTool):
    name = "ehole"
    display_name = "EHole 指纹识别"

    def __init__(self, config: dict, log_callback=None):
        super().__init__(config, log_callback=log_callback)
        self.ehole_path = config.get("path", "")
        self.project_path = ""

    @classmethod
    def open_settings(cls, parent, config_manager, log_callback=None, on_save=None):
        """打开 EHole 专属配置对话框"""
        log = log_callback or (lambda l, m: None)

        top = tk.Toplevel(parent)
        top.title("设置 - EHole 指纹识别")
        top.geometry("550x180")
        top.resizable(False, False)
        top.transient(parent)
        top.grab_set()

        top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 180) // 2
        top.geometry(f"+{x}+{y}")

        cfg = config_manager.get_tool_config("ehole")
        frame = ttk.Frame(top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="EHole 配置", font=("", 10, "bold")).pack(anchor=tk.W)

        ttk.Label(frame, text="程序路径", font=("", 9)).pack(anchor=tk.W, pady=(10, 3))
        path_row = ttk.Frame(frame)
        path_row.pack(fill=tk.X)
        path_var = tk.StringVar(value=cfg.get("path", ""))
        ttk.Entry(path_row, textvariable=path_var, font=("Consolas", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        def browse():
            path = filedialog.askopenfilename(filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")])
            if path:
                path_var.set(path)

        ttk.Button(path_row, text="浏览", command=browse, width=6).pack(side=tk.LEFT, padx=5)
        ttk.Label(frame, text="用法: EHole_windows_amd64.exe finger -l <url.txt>", foreground="gray", font=("", 8)).pack(anchor=tk.W, pady=(3, 10))

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(5, 0))

        def save():
            config_manager.set("tools.ehole.path", path_var.get().strip())
            log("success", "EHole 配置已保存")
            if on_save:
                on_save()
            top.destroy()

        ttk.Button(btn_row, text="保存", command=save).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_row, text="取消", command=top.destroy).pack(side=tk.RIGHT, padx=2)

    def get_ui(self, parent: tk.Widget, project_path: str) -> tk.Widget:
        self.project_path = project_path

        frame = ttk.Frame(parent, padding=5)

        # ── 步骤 1：选择 URL 文件 → 打开 CMD ──
        step1 = ttk.LabelFrame(frame, text="步骤 1：在 CMD 中运行 EHole", padding=5)
        step1.pack(fill=tk.X, pady=(0, 5))

        # URL 文件
        url_row = ttk.Frame(step1)
        url_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(url_row, text="URL文件:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_row, textvariable=self.url_var)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(url_row, text="浏览", command=self._browse_url_file, width=6).pack(side=tk.LEFT, padx=2)

        # 命令预览 + 打开 CMD 按钮
        cmd_row = ttk.Frame(step1)
        cmd_row.pack(fill=tk.X, pady=(0, 5))
        self.cmd_var = tk.StringVar()
        ttk.Entry(cmd_row, textvariable=self.cmd_var, state="readonly", font=("Consolas", 9)).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(cmd_row, text="打开 CMD", command=self._open_cmd, width=10).pack(side=tk.LEFT)

        ttk.Label(step1, text="→ CMD 中回车执行，复制结果", foreground="gray", font=("", 8)).pack(anchor=tk.W)

        # ── 步骤 2：粘贴结果 → 保存 ──
        step2 = ttk.LabelFrame(frame, text="步骤 2：粘贴结果并保存", padding=5)
        step2.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(step2, wrap=tk.WORD, font=("Consolas", 10),
                                   relief=tk.SUNKEN, borderwidth=1)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        # 底部按钮
        btn_row = ttk.Frame(step2)
        btn_row.pack(fill=tk.X)

        ttk.Button(btn_row, text="💾 保存结果", command=self._save_result).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="清空", command=lambda: self.result_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=2)

        self.status_label = ttk.Label(btn_row, text="", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # 选择 URL 文件后自动更新命令预览
        self.url_entry.bind("<FocusOut>", lambda e: self._update_cmd_preview())

        return frame

    def set_url_file(self, filepath: str):
        """外部设置 URL 文件路径（供文件树 '选为输入' 调用）"""
        self.url_var.set(filepath)
        self._update_cmd_preview()

    def _browse_url_file(self):
        info_dir = os.path.join(self.project_path, "信息") if self.project_path else ""
        filename = filedialog.askopenfilename(
            initialdir=info_dir,
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )
        if filename:
            self.url_var.set(filename)
            self._update_cmd_preview()

    def _update_cmd_preview(self):
        url_file = self.url_var.get().strip()
        if url_file and self.ehole_path:
            url_path = os.path.normpath(url_file)
            self.cmd_var.set(f'{self.ehole_path} finger -l "{url_path}"')
        else:
            self.cmd_var.set("")

    def _open_cmd(self):
        """打开 CMD 窗口，切换到 EHole 目录并预填命令"""
        url_file = self.url_var.get().strip()

        if not self.ehole_path or not os.path.exists(self.ehole_path):
            messagebox.showwarning("提示", "EHole 路径不存在，请先在设置中配置")
            return

        if not url_file or not os.path.exists(url_file):
            messagebox.showwarning("提示", "URL 文件不存在，请先选择文件")
            return

        # 路径统一用反斜杠，EHole 是 Windows 原生 Go 程序
        ehole_dir = os.path.normpath(os.path.dirname(self.ehole_path))
        url_path = os.path.normpath(url_file)

        # 构造一条 cmd /k 命令：先 cd 到 ehole 目录，再执行 finger
        cmd_line = f'cd /d "{ehole_dir}" && {os.path.basename(self.ehole_path)} finger -l "{url_path}"'
        subprocess.Popen(f'start "EHole" cmd /k "{cmd_line}"', shell=True)

        self.status_label.config(text="请在 CMD 窗口中查看结果，复制后粘贴到下方", foreground="blue")
        self._log("info", f"已打开 CMD 窗口运行 EHole")

    def _save_result(self):
        """保存粘贴的结果到信息目录"""
        content = self.result_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("提示", "请先粘贴 EHole 运行结果")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        info_dir = os.path.join(self.project_path, "信息")
        os.makedirs(info_dir, exist_ok=True)
        result_file = os.path.join(info_dir, f"ehole_{timestamp}.txt")

        url_file = self.url_var.get().strip()
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"# EHole 指纹识别结果\n")
            f.write(f"# 输入文件: {url_file}\n")
            f.write(f"# 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# " + "-" * 50 + "\n\n")
            f.write(content)

        self.status_label.config(text=f"已保存: ehole_{timestamp}.txt", foreground="green")
        self._log("success", f"EHole 结果已保存: {result_file}")

    def _log(self, level: str, message: str):
        if self.log:
            self.log(level, message)
