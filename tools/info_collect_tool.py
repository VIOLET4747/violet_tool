"""基础信息探测模块 — 预设采集项，手动收集后粘贴保存，自动加载上次内容"""

import os
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from tools.base_tool import BaseTool


class InfoCollectTool(BaseTool):
    name = "info_collect"
    display_name = "基础信息探测"
    default_config = {
        "items": [
            {"name": "IP", "hint": "https://site.ip138.com/", "type": "url"},
            {"name": "端口", "hint": "tscan 端口扫描", "type": "text"},
            {"name": "收集API路径", "hint": "google插件 findsomething LoveJS", "type": "text"},
            {"name": "网站架构信息", "hint": "插件 — Wappalyzer", "type": "text"}
        ]
    }

    def __init__(self, config: dict, log_callback=None):
        super().__init__(config, log_callback=log_callback)
        self.items = config.get("items", [])
        self.project_path = ""
        self.text_widgets = {}
        self.status_label = None

    @classmethod
    def open_settings(cls, parent, config_manager, log_callback=None, on_save=None):
        log = log_callback or (lambda l, m: None)

        top = tk.Toplevel(parent)
        top.title("设置 - 基础信息探测")
        top.geometry("780x500")
        top.resizable(True, True)
        top.transient(parent)
        top.grab_set()

        top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 780) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 500) // 2
        top.geometry(f"+{x}+{y}")

        frame = ttk.Frame(top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="信息采集项配置", font=("", 10, "bold")).pack(anchor=tk.W)

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        columns = ("name", "hint", "type")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                            selectmode="browse", height=8)
        tree.heading("name", text="名称", anchor=tk.W)
        tree.heading("hint", text="提示内容", anchor=tk.W)
        tree.heading("type", text="类型", anchor=tk.W)
        tree.column("name", width=100, minwidth=70)
        tree.column("hint", width=400, minwidth=200)
        tree.column("type", width=80, minwidth=60, anchor=tk.CENTER)

        ts = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        ts.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=ts.set)
        tree.pack(fill=tk.BOTH, expand=True)

        cfg = config_manager.get_tool_config("info_collect")
        items = list(cfg.get("items", []))
        TYPE_LABELS = {"text": "纯文本", "url": "超链接", "launch": "启动程序"}

        def refresh_table():
            tree.delete(*tree.get_children())
            for item in items:
                t = item.get("type", "text")
                tree.insert("", tk.END, values=(item["name"], item["hint"], TYPE_LABELS.get(t, t)))
        refresh_table()

        # ── 操作函数 ──
        def add_item():
            dlg = _ItemEditDialog(top, "新增采集项", "", "", "text")
            top.wait_window(dlg.top)
            if dlg.result:
                items.append({"name": dlg.result[0], "hint": dlg.result[1], "type": dlg.result[2]})
                refresh_table()

        def edit_item():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("提示", "请先选择一条")
                return
            idx = tree.index(sel[0])
            old = items[idx]
            dlg = _ItemEditDialog(top, "编辑采集项", old["name"], old["hint"], old.get("type", "text"))
            top.wait_window(dlg.top)
            if dlg.result:
                items[idx] = {"name": dlg.result[0], "hint": dlg.result[1], "type": dlg.result[2]}
                refresh_table()

        def delete_item():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            del items[idx]
            refresh_table()

        def move_up():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            if idx > 0:
                items[idx], items[idx - 1] = items[idx - 1], items[idx]
                refresh_table()
                tree.selection_set(tree.get_children()[idx - 1])

        def move_down():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            if idx < len(items) - 1:
                items[idx], items[idx + 1] = items[idx + 1], items[idx]
                refresh_table()
                tree.selection_set(tree.get_children()[idx + 1])

        # ── 按钮布局（两行）──
        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill=tk.X, pady=(5, 0))

        row1 = ttk.Frame(btn_bar)
        row1.pack(fill=tk.X)
        ttk.Button(row1, text=" 新增 ", command=add_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text=" 编辑 ", command=edit_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text=" 删除 ", command=delete_item).pack(side=tk.LEFT, padx=2)
        ttk.Separator(row1, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(row1, text=" ▲ 上移 ", command=move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text=" ▼ 下移 ", command=move_down).pack(side=tk.LEFT, padx=2)

        row2 = ttk.Frame(btn_bar)
        row2.pack(fill=tk.X, pady=(8, 0))

        def save_all():
            config_manager.set("tools.info_collect.items", items)
            log("success", f"信息采集项已保存，共 {len(items)} 项")
            if on_save:
                on_save()
            top.destroy()

        ttk.Button(row2, text=" 保存 ", command=save_all).pack(side=tk.RIGHT, padx=2)
        ttk.Button(row2, text=" 取消 ", command=top.destroy).pack(side=tk.RIGHT, padx=2)

        tree.bind("<Double-1>", lambda e: edit_item())

    # ────────────────── 工具 UI ──────────────────

    def get_ui(self, parent: tk.Widget, project_path: str) -> tk.Widget:
        self.project_path = project_path
        self.text_widgets.clear()

        outer = ttk.Frame(parent)

        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        def _on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_width(event):
            canvas.itemconfig("inner", width=event.width)

        scroll_frame.bind("<Configure>", _on_config)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="inner")
        canvas.bind("<Configure>", _on_width)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_wheel(e):
            canvas.bind_all("<MouseWheel>", _wheel)

        def _unbind_wheel(e):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for item in self.items:
            self._create_item_section(scroll_frame, item.get("name", ""), item.get("hint", ""))

        # 底部按钮
        bottom = ttk.Frame(scroll_frame)
        bottom.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(bottom, text="💾 全部保存", command=self._save_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom, text="清空全部", command=self._clear_all).pack(side=tk.LEFT, padx=2)

        self.status_label = ttk.Label(bottom, text="", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # 加载上次内容
        outer.after(100, self._load_last_file)

        return outer

    def _create_item_section(self, parent, name, hint):
        for item in self.items:
            if item.get("name") == name:
                item_type = item.get("type", "text")
                break
        else:
            item_type = "text"

        section = ttk.LabelFrame(parent, text=f"📋 {name}", padding=5)
        section.pack(fill=tk.X, padx=8, pady=(8, 0))

        hint_frame = ttk.Frame(section)
        hint_frame.pack(fill=tk.X, pady=(0, 5))

        if item_type == "url":
            link = tk.Label(hint_frame, text=f"🔗 {hint}", fg="#2563eb", cursor="hand2",
                            font=("", 9, "italic underline"))
            link.pack(side=tk.LEFT, anchor=tk.W)
            link.bind("<Button-1>", lambda e, u=hint: webbrowser.open(u))
        elif item_type == "launch":
            link = tk.Label(hint_frame, text=f"🚀 {hint}", fg="#16a34a", cursor="hand2",
                            font=("", 9, "italic underline"))
            link.pack(side=tk.LEFT, anchor=tk.W)
            link.bind("<Button-1>", lambda e, c=hint: subprocess.Popen(c, shell=True))
        else:
            ttk.Label(hint_frame, text=f"💡 {hint}", foreground="#6b7280",
                      font=("", 9, "italic"), wraplength=500).pack(side=tk.LEFT, anchor=tk.W)

        text = tk.Text(section, height=4, wrap=tk.WORD, font=("Consolas", 10),
                       relief=tk.SUNKEN, borderwidth=1)
        text.pack(fill=tk.X)

        btn_row = ttk.Frame(section)
        btn_row.pack(fill=tk.X, pady=(3, 0))
        ttk.Button(btn_row, text="💾 保存",
                   command=lambda n=name: self._save_one(n)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="清空",
                   command=lambda t=text: t.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=2)

        self.text_widgets[name] = text

    # ──────────── 保存 / 加载 ────────────

    def _save_one(self, name):
        self._write_combined_file()

    def _save_all(self):
        has = any(
            t and t.get("1.0", tk.END).strip()
            for item in self.items
            for t in [self.text_widgets.get(item.get("name", ""))]
        )
        if not has:
            if self.status_label:
                self.status_label.config(text="没有内容可保存", foreground="red")
            return
        self._write_combined_file()

    def _clear_all(self):
        for text in self.text_widgets.values():
            text.delete("1.0", tk.END)
        if self.status_label:
            self.status_label.config(text="已清空")

    def _write_combined_file(self):
        info_dir = os.path.join(self.project_path, "信息")
        os.makedirs(info_dir, exist_ok=True)
        filepath = os.path.join(info_dir, "信息收集.txt")

        lines = [
            "# 基础信息探测结果",
            f"# 项目: {os.path.basename(self.project_path)}",
            f"# 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        for item in self.items:
            name = item.get("name", "")
            text = self.text_widgets.get(name)
            content = text.get("1.0", tk.END).strip() if text else ""
            lines.append("=" * 60)
            lines.append(f"  {name}")
            lines.append("=" * 60)
            lines.append("")
            lines.append(content if content else "(无内容)")
            lines.append("")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self._log("success", "信息收集已保存")
        if self.status_label:
            self.status_label.config(text="已保存: 信息收集.txt", foreground="green")

    def _load_last_file(self):
        filepath = os.path.join(self.project_path, "信息", "信息收集.txt")
        if not os.path.exists(filepath):
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self._parse_and_fill(content)
            if self.status_label:
                self.status_label.config(text="已加载: 信息收集.txt", foreground="blue")
            self._log("info", "已加载上次信息收集内容")
        except Exception:
            pass

    def _parse_and_fill(self, content):
        sep = "=" * 60
        parts = content.split(sep)
        # 格式: [头部注释块, 标题, 内容, 标题, 内容, ...]
        for i in range(1, len(parts) - 1, 2):
            title = parts[i].strip()
            if i + 1 < len(parts):
                body = parts[i + 1].strip()
                if body == "(无内容)":
                    body = ""
            else:
                body = ""
            if title and title in self.text_widgets:
                w = self.text_widgets[title]
                w.delete("1.0", tk.END)
                if body:
                    w.insert("1.0", body)

    def _log(self, level, message):
        if self.log:
            self.log(level, message)


class _ItemEditDialog:
    """新增 / 编辑采集项弹窗"""

    def __init__(self, parent, title, name, hint, item_type="text"):
        self.result = None

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x220")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.top.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 220) // 2
        self.top.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self.top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="名称", font=("", 9)).pack(anchor=tk.W)
        self.name_var = tk.StringVar(value=name)
        ttk.Entry(frame, textvariable=self.name_var, font=("", 10)).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="提示内容（URL / 命令 / 说明文字）", font=("", 9)).pack(anchor=tk.W)
        self.hint_var = tk.StringVar(value=hint)
        ttk.Entry(frame, textvariable=self.hint_var, font=("", 10)).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="类型", font=("", 9)).pack(anchor=tk.W)
        self.type_var = tk.StringVar(value=item_type)
        cb = ttk.Combobox(frame, textvariable=self.type_var, state="readonly",
                          values=["text", "url", "launch"], width=15)
        cb.pack(anchor=tk.W)
        ttk.Label(frame,
                  text="纯文本: 灰色提示  |  超链接: 蓝色可点击打开浏览器  |  启动程序: 绿色可点击运行命令",
                  foreground="gray", font=("", 7)).pack(anchor=tk.W, pady=(2, 0))

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=(15, 0))

        def confirm():
            n = self.name_var.get().strip()
            if not n:
                messagebox.showwarning("提示", "名称不能为空")
                return
            self.result = (n, self.hint_var.get().strip(), self.type_var.get())
            self.top.destroy()

        ttk.Button(btn_row, text="确定", width=10, command=confirm).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_row, text="取消", width=10, command=self.top.destroy).pack(side=tk.RIGHT, padx=5)
