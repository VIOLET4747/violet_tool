# violet_tool

渗透测试工作流桌面工具，整合 FOFA API 查询、EHole 指纹识别、基础信息探测等工具。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

首次启动会自动生成 `config.json`。在菜单栏配置 Key 和路径后即可使用。

## 界面流程

```
启动 → 项目选择页 → 选择或新建项目 → 工作台（左边文件树 + 右边工具面板）
```

- **项目选择页**：查看全部项目，新建项目，配置系统路径
- **工作台**：左侧文件树（右键文件可「选为输入」传给工具），右侧可拖拽排序的工具选项卡

## 内置工具

| 工具 | 用途 |
|------|------|
| FOFA 查询 | 输入语法 → 调用 fofoapi.com API → 表格预览 → 导出 CSV/JSON/URL |
| EHole 指纹识别 | 选 URL 文件 → 打开 CMD 手动运行 → 粘贴结果 → 自动保存 |
| 基础信息探测 | 预设采集项（IP、端口等），手动收集后粘贴，统一保存到一个文件 |

## 配置说明

`config.json` 结构：

```
tools     → 各工具的配置（FOFA Key、EHole 路径等）
paths     → 项目基础目录
ui        → 界面设置
```

菜单栏分 **插件配置**（工具设置）和 **系统设置**（项目路径），保存后即时生效。

## 项目结构

```
violet_tool/
├── main.py
├── config.json              ← 不提交 git
├── gui/                     ← 界面层
│   ├── main_window.py
│   ├── left_panel.py
│   ├── tool_panel.py
│   ├── project_panel.py
│   ├── settings_dialogs.py
│   └── widgets/
│       ├── draggable_notebook.py
│       ├── log_bar.py
│       └── result_table.py
├── tools/                   ← 工具层
│   ├── base_tool.py
│   ├── tool_registry.py
│   ├── fofa_tool.py
│   ├── ehole_tool.py
│   └── info_collect_tool.py
└── utils/                   ← 基础功能
    ├── config_manager.py
    ├── project_manager.py
    └── history_manager.py
```

## 新增工具

1. 在 `tools/` 下新建文件，继承 `BaseTool`，实现 `get_ui()` 和可选的 `open_settings()`
2. 在 `tool_registry.py` 注册
3. 在 `config.json` 的 `tools` 下添加配置项

详见 `tools/base_tool.py` 中的接口说明。

## 打包

```bash
pip install pyinstaller
build.bat
# 输出: dist/violet_tool.exe
```
