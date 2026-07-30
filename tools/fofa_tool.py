"""FOFA API 查询工具"""

import base64
import json
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime

import requests

from tools.base_tool import BaseTool
from utils.history_manager import HistoryManager
from gui.widgets.result_table import ResultTable


class FofaTool(BaseTool):
    name = "fofa"
    display_name = "FOFA 查询"

    # 默认查询字段（与 API 返回顺序一致）
    DEFAULT_FIELDS = "host,ip,port,domain,title,server,protocol,os,country,region,city,asn,org,icp,link,product,product_category,lastupdatetime"

    def __init__(self, config: dict, log_callback=None):
        super().__init__(config, log_callback=log_callback)
        self.base_url = ""
        self.api_key = ""
        self.project_path = ""
        self.current_results = {"columns": [], "rows": []}

    @classmethod
    def open_settings(cls, parent, config_manager, log_callback=None, on_save=None):
        """打开 FOFA 专属配置对话框"""
        import base64
        import threading
        import requests
        from tkinter import messagebox

        log = log_callback or (lambda l, m: None)

        top = tk.Toplevel(parent)
        top.title("设置 - FOFA API")
        top.geometry("550x280")
        top.resizable(False, False)
        top.transient(parent)
        top.grab_set()

        top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 280) // 2
        top.geometry(f"+{x}+{y}")

        frame = ttk.Frame(top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="FOFA API 配置", font=("", 10, "bold")).pack(anchor=tk.W)

        # API Key
        ttk.Label(frame, text="API Key", font=("", 9)).pack(anchor=tk.W, pady=(10, 3))
        key_var = tk.StringVar(value=config_manager.get_fofa_key())
        key_entry = ttk.Entry(frame, textvariable=key_var, font=("Consolas", 10), show="*", width=50)
        key_entry.pack(fill=tk.X, pady=(0, 2))
        show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="显示 Key", variable=show_key_var,
                        command=lambda: key_entry.configure(show="" if show_key_var.get() else "*")).pack(anchor=tk.W)

        ttk.Label(frame, text="获取 Key: 登录 https://fofoapi.com → 用户中心", foreground="gray", font=("", 8)).pack(anchor=tk.W, pady=(0, 10))

        # Base URL
        ttk.Label(frame, text="Base URL", font=("", 9)).pack(anchor=tk.W, pady=(0, 3))
        url_var = tk.StringVar(value=config_manager.get_fofa_base_url())
        ttk.Entry(frame, textvariable=url_var, font=("Consolas", 10)).pack(fill=tk.X)

        # 按钮
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(15, 0))

        def test_connection():
            key = key_var.get().strip()
            url = url_var.get().strip().rstrip("/")
            if not key:
                messagebox.showwarning("提示", "请先填写 API Key")
                return

            def do_test():
                try:
                    test_query = base64.b64encode(b'domain="baidu.com"').decode()
                    resp = requests.get(
                        f"{url}/api/v1/search/all?qbase64={test_query}&key={key}&size=1",
                        timeout=15,
                    )
                    data = resp.json()
                    if "error" in data:
                        top.after(0, lambda: messagebox.showerror("连接失败", f"API 返回: {data.get('error')}"))
                    else:
                        total = data.get("size", 0)
                        top.after(0, lambda: messagebox.showinfo("连接成功", f"FOFA API 连接成功！\n可查询 {total} 条"))
                        log("success", "FOFA API 连接测试成功")
                except Exception as e:
                    top.after(0, lambda: messagebox.showerror("连接失败", str(e)))

            threading.Thread(target=do_test, daemon=True).start()

        ttk.Button(btn_row, text="测试连接", command=test_connection).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="保存", command=lambda: _save(
            top, config_manager, key_var.get().strip(), url_var.get().strip(), log, on_save
        )).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_row, text="取消", command=top.destroy).pack(side=tk.RIGHT, padx=2)

    @staticmethod
    def _save(top, config_manager, key, url, log, on_save=None):
        config_manager.set("tools.fofa.key", key)
        config_manager.set("tools.fofa.base_url", url.rstrip("/"))
        log("success", "FOFA 配置已保存")
        if on_save:
            on_save()
        top.destroy()

    def set_credentials(self, base_url: str, api_key: str):
        """设置 API 凭据"""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def get_ui(self, parent: tk.Widget, project_path: str) -> tk.Widget:
        self.project_path = project_path

        frame = ttk.Frame(parent, padding=5)

        # ── 查询输入区 ──
        input_frame = ttk.LabelFrame(frame, text="查询语法", padding=5)
        input_frame.pack(fill=tk.X, pady=(0, 5))

        # 语法输入行
        query_row = ttk.Frame(input_frame)
        query_row.pack(fill=tk.X)

        ttk.Label(query_row, text="语法:").pack(side=tk.LEFT)
        self.query_entry = ttk.Entry(query_row)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.query_entry.bind("<Return>", lambda e: self._do_search())
        self.query_entry.bind("<Control-Return>", lambda e: self._do_search())

        # 历史下拉
        ttk.Label(query_row, text="历史:").pack(side=tk.LEFT, padx=(5, 0))
        self.history_var = tk.StringVar()
        self.history_combo = ttk.Combobox(query_row, textvariable=self.history_var,
                                          state="readonly", width=30)
        self.history_combo.pack(side=tk.LEFT, padx=5)
        self.history_combo.bind("<<ComboboxSelected>>", self._on_history_selected)

        # 按钮行
        btn_row = ttk.Frame(input_frame)
        btn_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_row, text="🔍 查询", command=self._do_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="📊 先看统计", command=self._do_stats).pack(side=tk.LEFT, padx=2)

        self.progress_var = tk.StringVar(value="")
        ttk.Label(btn_row, textvariable=self.progress_var, foreground="gray").pack(side=tk.LEFT, padx=10)

        self.status_label = ttk.Label(btn_row, text="", foreground="blue")
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # ── 结果区 ──
        self.result_table = ResultTable(frame)
        self.result_table.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        # 默认导出到项目信息目录
        self.result_table.export_dir = os.path.join(project_path, "信息")

        # 加载历史
        self._load_history()

        return frame

    def _load_history(self):
        """加载当前项目的 FOFA 查询历史"""
        history_dir = os.path.join(self.project_path, "信息", ".history")
        hm = HistoryManager(history_dir)
        queries = hm.load()
        self.history_combo["values"] = queries
        if queries:
            self.history_var.set("")
            self.query_entry.delete(0, tk.END)
        self._history_queries = queries

    def _on_history_selected(self, event):
        selected = self.history_var.get()
        if selected:
            self.query_entry.delete(0, tk.END)
            self.query_entry.insert(0, selected)

    def _save_history(self, query: str):
        history_dir = os.path.join(self.project_path, "信息", ".history")
        hm = HistoryManager(history_dir)
        hm.add(query)
        self._load_history()

    def _do_stats(self):
        """先查询统计信息"""
        query = self.query_entry.get().strip()
        if not query:
            self.status_label.config(text="请输入查询语法", foreground="red")
            return

        if not self.api_key:
            self.status_label.config(text="请先在配置中设置 FOFA API Key", foreground="red")
            return

        self.status_label.config(text="正在查询统计...", foreground="blue")
        self.progress_var.set("")

        threading.Thread(target=self._run_stats, args=(query,), daemon=True).start()

    def _run_stats(self, query: str):
        try:
            qbase64 = base64.b64encode(query.encode("utf-8")).decode("utf-8")
            url = f"{self.base_url}/api/v1/search/stats?qbase64={qbase64}&key={self.api_key}"
            resp = requests.get(url, timeout=30)
            data = resp.json()

            if data.get("error"):
                err = data.get("error")
                self._log("error", f"FOFA 统计失败: {err}")
                self._update_status(f"统计失败: {err}", "red")
                return

            total = data.get("size", 0)
            distinct_ip = data.get("distinct", {}).get("ip", 0)
            msg = f"总量约 {total} 条"
            if distinct_ip:
                msg += f"，独立 IP {distinct_ip} 个"
            self._log("info", f"FOFA 统计: {msg}")
            self._update_status(msg, "blue")
            self.progress_var.set(f"总量约 {total} 条")

        except Exception as e:
            self._log("error", f"FOFA 统计出错: {e}")
            self._update_status(f"统计出错: {e}", "red")

    def _do_search(self):
        """执行 FOFA 查询"""
        query = self.query_entry.get().strip()
        if not query:
            self.status_label.config(text="请输入查询语法", foreground="red")
            return

        if not self.api_key:
            self.status_label.config(text="请先在配置中设置 FOFA API Key", foreground="red")
            return

        self.status_label.config(text="正在查询...", foreground="blue")
        self.progress_var.set("查询中...")

        # 保存历史
        self._save_history(query)

        threading.Thread(target=self._run_search, args=(query,), daemon=True).start()

    def _run_search(self, query: str):
        try:
            all_results = []
            page = 1

            qbase64 = base64.b64encode(query.encode("utf-8")).decode("utf-8")
            url = (f"{self.base_url}/api/v1/search/all"
                   f"?qbase64={qbase64}&key={self.api_key}"
                   f"&size=1000&fields={self.DEFAULT_FIELDS}")

            resp = requests.get(url, timeout=60)
            data = resp.json()

            if data.get("error"):
                err = data.get("error")
                self._log("error", f"FOFA 查询失败: {err}")
                self._update_status(f"查询失败: {err}", "red")
                return

            results = data.get("results", [])
            if results:
                all_results.extend(results)

            # 字段名来自 DEFAULT_FIELDS
            columns = self.DEFAULT_FIELDS.split(",")

            # 自动翻页
            total = data.get("size", 0)
            while data.get("next") and len(all_results) < total:
                page += 1
                next_path = data["next"]
                next_full_url = f"{self.base_url}{next_path}&key={self.api_key}"
                resp2 = requests.get(next_full_url, timeout=60)
                data = resp2.json()
                more = data.get("results", [])
                if more:
                    all_results.extend(more)
                self.progress_var.set(f"已获取 {len(all_results)} 条...")

            # 转换为表格行（results 是 list of lists）
            rows = []
            for item in all_results:
                if isinstance(item, list):
                    # list → 补全不足长度的列
                    row = list(item)
                    while len(row) < len(columns):
                        row.append("")
                    rows.append(row[:len(columns)])
                elif isinstance(item, dict):
                    # 兼容 dict 格式
                    row = [str(item.get(col, "")) for col in columns]
                    rows.append(row)

            self.current_results = {"columns": columns, "rows": rows}

            # 回到主线程更新 UI
            self.result_table.after(0, lambda: self._display_results(columns, rows))

        except Exception as e:
            self._log("error", f"FOFA 查询出错: {e}")
            self._update_status(f"查询出错: {e}", "red")
            self.progress_var.set("")

    def _display_results(self, columns: list[str], rows: list[list]):
        self.result_table.set_data(columns, rows)
        self._log("success", f"FOFA 查询完成，返回 {len(rows)} 条结果")
        self._update_status(f"共 {len(rows)} 条结果", "green")
        self.progress_var.set(f"共 {len(rows)} 条")

    def _update_status(self, msg: str, color: str):
        def _update():
            self.status_label.config(text=msg, foreground=color)
        self.result_table.after(0, _update)

    def _log(self, level: str, message: str):
        if self.log:
            self.log(level, message)
