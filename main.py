#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
violet_tool - 渗透测试工作流工具
整合 FOFA API 查询、EHole 指纹识别等工具
"""

import ctypes
import sys

# ── 高 DPI 适配（必须在创建任何 tk 窗口之前执行）──
if sys.platform == "win32":
    try:
        # Windows 8.1+
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PerMonitorV2
    except AttributeError:
        try:
            # Windows Vista+
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from gui.main_window import MainWindow


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
