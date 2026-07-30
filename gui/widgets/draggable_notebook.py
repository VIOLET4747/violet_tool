"""可拖拽排序的标签页面板 — 完全自绘，支持按住拖动排序"""

import tkinter as tk
from tkinter import ttk


class DraggableNotebook(ttk.Frame):
    """模拟浏览器标签页：上方可拖拽排序的标签栏 + 下方内容区"""

    TAB_BG = "#e0e0e0"
    TAB_ACTIVE_BG = "#f5f5f5"
    TAB_HOVER_BG = "#d0d0d0"
    TAB_DRAG_BG = "#c0d0ff"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tab_widgets = []      # list of (content_frame, text)
        self.tab_labels = []       # list of Label widgets in the tab bar
        self.active_idx = -1
        self._drag_from = -1
        self._drag_to = -1
        self._drag_widget = None   # floating label during drag

        # 标签栏
        self.tab_bar = tk.Frame(self, height=28, bg="#c8c8c8")
        self.tab_bar.pack(fill=tk.X, side=tk.TOP)
        self.tab_bar.pack_propagate(False)

        # 内容区
        self.content_area = ttk.Frame(self)
        self.content_area.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # 标签栏滚动（标签太多时）
        self.tab_canvas = tk.Canvas(self.tab_bar, height=26, highlightthickness=0, bg="#c8c8c8")
        self.tab_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 18))

        self.tab_container = tk.Frame(self.tab_canvas, bg="#c8c8c8")
        self._canvas_window = self.tab_canvas.create_window((0, 0), window=self.tab_container, anchor="nw")

        self.tab_container.bind("<Configure>", lambda e: self.tab_canvas.configure(
            scrollregion=self.tab_canvas.bbox("all")))

        # 右侧加号区域
        plus_frame = tk.Frame(self.tab_bar, width=18, bg="#c8c8c8")
        plus_frame.pack(side=tk.RIGHT, fill=tk.Y)
        plus_frame.pack_propagate(False)

    def add(self, content: tk.Widget, text: str):
        """添加一个标签页"""
        idx = len(self.tab_widgets)
        self.tab_widgets.append((content, text))

        # 创建标签按钮
        lbl = tk.Label(self.tab_container, text=f" {text} ", bg=self.TAB_BG,
                       fg="#333", font=("", 9), padx=6, pady=2,
                       relief=tk.RAISED, borderwidth=1, cursor="hand2")
        lbl.pack(side=tk.LEFT, padx=(0, 1))
        self.tab_labels.append(lbl)

        # 点击切换
        lbl.bind("<Button-1>", lambda e, i=idx: self.select(i))

        # 拖拽事件
        lbl.bind("<ButtonPress-1>", lambda e, i=idx: self._start_drag(e, i), add=True)
        lbl.bind("<B1-Motion>", lambda e, i=idx: self._on_drag(e, i), add=True)
        lbl.bind("<ButtonRelease-1>", lambda e, i=idx: self._end_drag(e, i), add=True)

        # 悬浮效果
        lbl.bind("<Enter>", lambda e, l=lbl: l.configure(bg=self.TAB_HOVER_BG) if self._drag_from < 0 else None)
        lbl.bind("<Leave>", lambda e, l=lbl: l.configure(
            bg=self.TAB_ACTIVE_BG if self.tab_labels.index(l) == self.active_idx else self.TAB_BG)
                if self._drag_from < 0 else None)

        # 内容默认隐藏
        content.pack_forget()

        if self.active_idx < 0:
            self.select(0)

    def select(self, idx: int):
        """切换到指定标签页"""
        if idx < 0 or idx >= len(self.tab_widgets):
            return

        try:
            # 隐藏旧内容
            if 0 <= self.active_idx < len(self.tab_widgets):
                old_content, _ = self.tab_widgets[self.active_idx]
                if old_content.winfo_exists():
                    old_content.pack_forget()
                if self.active_idx < len(self.tab_labels):
                    self.tab_labels[self.active_idx].configure(
                        bg=self.TAB_BG, relief=tk.RAISED)

            # 显示新内容
            self.active_idx = idx
            content, _ = self.tab_widgets[idx]
            if content.winfo_exists() and self.content_area.winfo_exists():
                content.pack(in_=self.content_area, fill=tk.BOTH, expand=True)
            self.tab_labels[idx].configure(bg=self.TAB_ACTIVE_BG, relief=tk.SUNKEN)
        except tk.TclError:
            pass

    def tabs(self):
        """返回所有标签内容 widget 的列表（兼容旧接口）"""
        return [w for w, _ in self.tab_widgets]

    def tab(self, widget, option: str):
        """获取标签属性（兼容旧接口）"""
        for i, (w, text) in enumerate(self.tab_widgets):
            if str(w) == str(widget):
                if option == "text":
                    return text
        return ""

    def index(self, what) -> int:
        """获取索引"""
        if what == "current":
            return self.active_idx
        if what == "end":
            return len(self.tab_widgets)
        return -1

    def forget(self, widget):
        """移除标签页"""
        for i, (w, text) in enumerate(self.tab_widgets):
            if str(w) == str(widget):
                del self.tab_widgets[i]
                lbl = self.tab_labels.pop(i)
                lbl.destroy()
                w.pack_forget()
                if self.active_idx >= len(self.tab_widgets):
                    self.active_idx = len(self.tab_widgets) - 1
                if self.active_idx >= 0:
                    self.select(self.active_idx)
                return

    def insert(self, pos, widget, text: str = ""):
        """在指定位置插入标签页"""
        for i, (w, _) in enumerate(self.tab_widgets):
            if str(w) == str(widget):
                # 已存在，移动位置
                del self.tab_widgets[i]
                old_lbl = self.tab_labels.pop(i)
                old_lbl.destroy()
                break

        if pos == "end" or pos >= len(self.tab_widgets):
            pos = len(self.tab_widgets)

        self.tab_widgets.insert(pos, (widget, text))

        lbl = tk.Label(self.tab_container, text=f" {text} ", bg=self.TAB_BG,
                       fg="#333", font=("", 9), padx=6, pady=2,
                       relief=tk.RAISED, borderwidth=1, cursor="hand2")
        self.tab_labels.insert(pos, lbl)

        # 重新 pack 所有标签（按新顺序）
        for label in self.tab_labels:
            label.pack_forget()
        for label in self.tab_labels:
            label.pack(side=tk.LEFT, padx=(0, 1))

        # 重新绑定索引
        for i, label in enumerate(self.tab_labels):
            for bind_seq in label.bind():
                label.unbind(bind_seq)
            label.bind("<Button-1>", lambda e, idx=i: self.select(idx))
            label.bind("<ButtonPress-1>", lambda e, idx=i: self._start_drag(e, idx), add=True)
            label.bind("<B1-Motion>", lambda e, idx=i: self._on_drag(e, idx), add=True)
            label.bind("<ButtonRelease-1>", lambda e, idx=i: self._end_drag(e, idx), add=True)
            label.bind("<Enter>", lambda e, l=label: l.configure(bg=self.TAB_HOVER_BG) if self._drag_from < 0 else None)
            label.bind("<Leave>", lambda e, l=label, i=i: l.configure(
                bg=self.TAB_ACTIVE_BG if i == self.active_idx else self.TAB_BG)
                        if self._drag_from < 0 else None)

        if self.active_idx < 0:
            self.select(0)

    def _start_drag(self, event, idx: int):
        """开始拖拽"""
        self._drag_from = idx
        self._drag_to = idx
        self.tab_labels[idx].configure(bg=self.TAB_DRAG_BG)

    def _on_drag(self, event, idx: int):
        """拖拽中"""
        if self._drag_from < 0 or idx != self._drag_from:
            return

        # 计算鼠标位置相对于标签栏的 x
        abs_x = event.widget.winfo_rootx() + event.x

        # 找到鼠标下的目标标签
        target = -1
        for i, lbl in enumerate(self.tab_labels):
            if i == self._drag_from:
                continue
            x1 = lbl.winfo_rootx()
            x2 = x1 + lbl.winfo_width()
            if x1 <= abs_x <= x2:
                target = i
                break

        # 也检测标签之间的空隙
        if target < 0:
            for i, lbl in enumerate(self.tab_labels):
                x2 = lbl.winfo_rootx() + lbl.winfo_width()
                if i < len(self.tab_labels) - 1:
                    x_next = self.tab_labels[i + 1].winfo_rootx()
                    if x2 <= abs_x <= x_next:
                        target = i + 1 if i + 1 != self._drag_from else i
                        break
                elif abs_x > x2 and i != self._drag_from:
                    target = len(self.tab_labels) - 1
                    break
            if target < 0 and abs_x < self.tab_labels[0].winfo_rootx():
                target = 0

        if target >= 0 and target != self._drag_to:
            # 执行移动
            self._move_tab(self._drag_from, target)
            self._drag_from = target
            self._drag_to = target

    def _end_drag(self, event, idx: int):
        """结束拖拽"""
        if 0 <= idx < len(self.tab_labels):
            self.tab_labels[idx].configure(
                bg=self.TAB_ACTIVE_BG if idx == self.active_idx else self.TAB_BG)
        self._drag_from = -1
        self._drag_to = -1

    def _move_tab(self, from_idx: int, to_idx: int):
        """移动标签从 from_idx 到 to_idx"""
        if from_idx == to_idx:
            return
        tab_data = self.tab_widgets.pop(from_idx)
        lbl = self.tab_labels.pop(from_idx)

        if to_idx > from_idx:
            to_idx -= 1  # pop 之后索引前移

        self.tab_widgets.insert(to_idx, tab_data)
        self.tab_labels.insert(to_idx, lbl)

        # 重新 pack
        for label in self.tab_labels:
            label.pack_forget()
        for label in self.tab_labels:
            label.pack(side=tk.LEFT, padx=(0, 1))

        # 重新绑定所有标签的事件（lambda 捕获了新索引）
        for i, label in enumerate(self.tab_labels):
            for bind_seq in label.bind():
                label.unbind(bind_seq)
            label.bind("<Button-1>", lambda e, idx=i: self.select(idx))
            label.bind("<ButtonPress-1>", lambda e, idx=i: self._start_drag(e, idx), add=True)
            label.bind("<B1-Motion>", lambda e, idx=i: self._on_drag(e, idx), add=True)
            label.bind("<ButtonRelease-1>", lambda e, idx=i: self._end_drag(e, idx), add=True)
            label.bind("<Enter>", lambda e, l=label: l.configure(bg=self.TAB_HOVER_BG) if self._drag_from < 0 else None)
            label.bind("<Leave>", lambda e, l=label, i=i: l.configure(
                bg=self.TAB_ACTIVE_BG if i == self.active_idx else self.TAB_BG)
                        if self._drag_from < 0 else None)

        # 更新 active_idx
        if self.active_idx == from_idx:
            self.active_idx = to_idx
        elif from_idx < self.active_idx <= to_idx:
            self.active_idx -= 1
        elif to_idx <= self.active_idx < from_idx:
            self.active_idx += 1

        self.select(self.active_idx)
