"""左侧面板 — 文件树（项目选中后显示）"""

import os
import subprocess
import tkinter as tk
from tkinter import ttk


class LeftPanel(ttk.Frame):
    """VSCode 风格文件树侧边栏"""

    def __init__(self, parent, on_file_selected=None, log_callback=None):
        super().__init__(parent, width=260)
        self.on_file_selected = on_file_selected
        self.log = log_callback or (lambda l, m: None)
        self.current_project = None
        self._file_nodes = {}
        self.pack_propagate(False)

        self._build_ui()

    def _build_ui(self):
        # 项目信息头
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=5, pady=5)

        self.project_title_label = ttk.Label(header, text="", font=("", 10, "bold"))
        self.project_title_label.pack(side=tk.LEFT)

        # 文件树
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 5))

        self.file_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.bind("<Double-1>", self._on_file_double_click)
        self.file_tree.bind("<MouseWheel>",
                            lambda e: self.file_tree.yview_scroll(int(-1 * e.delta / 120), "units"))

        # 右键菜单
        self.file_menu = tk.Menu(self.file_tree, tearoff=0)
        self.file_menu.add_command(label="选为输入", command=self._file_to_input)
        self.file_menu.add_command(label="打开", command=self._open_selected_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="复制路径", command=self._copy_file_path)
        self.file_menu.add_command(label="在资源管理器中打开", command=self._open_in_explorer)
        self.file_tree.bind("<Button-3>", self._show_file_menu)

    def load_project(self, project_info: dict):
        """加载项目文件树"""
        self.current_project = project_info
        self.project_title_label.config(text=f"📁 {project_info['name']}")
        self._build_file_tree(project_info["path"])

    def _build_file_tree(self, root_path: str):
        self.file_tree.delete(*self.file_tree.get_children())
        self._file_nodes = {}

        def add_dir(parent_iid, dirpath):
            try:
                entries = sorted(os.listdir(dirpath),
                                 key=lambda e: (not os.path.isdir(os.path.join(dirpath, e)), e.lower()))
            except PermissionError:
                return
            for entry in entries:
                if entry.startswith("."):
                    continue
                full = os.path.join(dirpath, entry)
                if os.path.isdir(full):
                    iid = self.file_tree.insert(parent_iid, tk.END, text=f"📁 {entry}", open=False)
                    self._file_nodes[iid] = full
                    add_dir(iid, full)
                else:
                    iid = self.file_tree.insert(parent_iid, tk.END, text=f"  {entry}")
                    self._file_nodes[iid] = full

        add_dir("", root_path)

    # ── 文件交互 ──

    def _get_selected_file_path(self):
        sel = self.file_tree.selection()
        if not sel:
            return None
        return self._file_nodes.get(sel[0])

    def _on_file_double_click(self, event):
        path = self._get_selected_file_path()
        if path and os.path.isfile(path):
            os.startfile(path)

    def _show_file_menu(self, event):
        item = self.file_tree.identify_row(event.y)
        if item and item in self._file_nodes:
            self.file_tree.selection_set(item)
            try:
                self.file_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.file_menu.grab_release()

    def _file_to_input(self):
        path = self._get_selected_file_path()
        if path and os.path.isfile(path) and self.on_file_selected:
            self.on_file_selected(path)
            self.log("info", f"选中: {os.path.basename(path)}")

    def _open_selected_file(self):
        path = self._get_selected_file_path()
        if path and os.path.isfile(path):
            os.startfile(path)

    def _copy_file_path(self):
        path = self._get_selected_file_path()
        if path:
            self.clipboard_clear()
            self.clipboard_append(path)
            self.log("info", f"已复制: {path}")

    def _open_in_explorer(self):
        path = self._get_selected_file_path()
        if path:
            subprocess.run(["explorer", "/select,", path])

    def clear(self):
        self.file_tree.delete(*self.file_tree.get_children())
        self._file_nodes = {}
        self.project_title_label.config(text="")
        self.current_project = None
