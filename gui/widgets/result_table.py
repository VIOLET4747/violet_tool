"""可复用的查询结果表格组件"""

import csv
import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class ResultTable(ttk.Frame):
    """带导出功能的查询结果表格"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = []
        self.rows = []
        self.export_dir = None  # 默认导出目录
        self._build_ui()

    def _build_ui(self):
        # 统计栏
        self.stats_bar = ttk.Frame(self)
        self.stats_bar.pack(fill=tk.X, side=tk.TOP)

        self.stats_label = ttk.Label(self.stats_bar, text="", font=("", 9))
        self.stats_label.pack(side=tk.LEFT, padx=5)

        # Treeview 容器
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = None  # 动态创建
        self.scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        self.scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)

        # 底部导出按钮
        export_frame = ttk.Frame(self)
        export_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=(5, 0))

        ttk.Button(export_frame, text="导出 CSV", command=lambda: self.export("csv")).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="导出 JSON", command=lambda: self.export("json")).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="导出 URL (TXT)", command=lambda: self.export("url")).pack(side=tk.LEFT, padx=2)

        self.export_hint = ttk.Label(export_frame, text="", foreground="gray")
        self.export_hint.pack(side=tk.RIGHT, padx=5)

    def set_data(self, columns: list[str], rows: list[list]):
        """设置表格数据

        Args:
            columns: 列名列表
            rows: 数据行列表，每行是 list
        """
        self.columns = columns
        self.rows = rows

        # 清除旧 tree
        if self.tree:
            self.tree.destroy()
            self.scrollbar_x.pack_forget()
            self.scrollbar_y.pack_forget()

        if not columns:
            self.stats_label.config(text="无数据")
            return

        # 创建新 tree
        tree_frame = self.tree.master if self.tree else self.winfo_children()[1]

        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show="headings", selectmode="extended")

        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=120, minwidth=60)

        for row in rows:
            self.tree.insert("", tk.END, values=row)

        # 滚动条
        self.scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set,
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.stats_label.config(text=f"共 {len(rows)} 条记录")

    def clear(self):
        """清空表格"""
        self.set_data([], [])

    def export(self, fmt: str):
        """导出数据

        Args:
            fmt: 'csv' | 'json' | 'url'
        """
        if not self.rows:
            self.export_hint.config(text="没有数据可导出", foreground="red")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = ""

        from tkinter import filedialog
        if fmt == "csv":
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV 文件", "*.csv")],
                initialfile=f"fofa_{timestamp}.csv",
                initialdir=self.export_dir,
            )
            if filename:
                self._export_csv(filename)
        elif fmt == "json":
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON 文件", "*.json")],
                initialfile=f"fofa_{timestamp}.json",
                initialdir=self.export_dir,
            )
            if filename:
                self._export_json(filename)
        elif fmt == "url":
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt")],
                initialfile=f"url_{timestamp}.txt",
                initialdir=self.export_dir,
            )
            if filename:
                self._export_url_txt(filename)

    def _export_csv(self, filepath: str):
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(self.rows)
        self.export_hint.config(text=f"已导出 CSV: {filepath}", foreground="green")

    def _export_json(self, filepath: str):
        data = [dict(zip(self.columns, row)) for row in self.rows]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.export_hint.config(text=f"已导出 JSON: {filepath}", foreground="green")

    def _export_url_txt(self, filepath: str):
        """只导出 URL（link 字段）"""
        # 尝试找到 link 列
        link_idx = None
        for i, col in enumerate(self.columns):
            if col.lower() in ("link", "url", "href"):
                link_idx = i
                break

        if link_idx is not None:
            urls = [row[link_idx] for row in self.rows if link_idx < len(row) and row[link_idx]]
        else:
            # 没有 link 列，导出第一列
            urls = [row[0] for row in self.rows if row[0]]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(urls))
        self.export_hint.config(text=f"已导出 {len(urls)} 个 URL: {filepath}", foreground="green")
