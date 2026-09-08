# TodoList 改进方案

## 1. 文档信息

- 项目：Desktop Todo Lite
- 目标：在保留现有 Todo 功能的基础上，加入专注功能，重构代码结构，改善视觉与交互，并替换软件图标。
- 当前阶段：实施完成。
- 方案版本：v1.9
- 数据兼容原则：现有任务和设置数据不能因为重构而丢失。

### 版本变更

- v1.1：明确 Todo 和专注是两个独立页面，通过软件顶部的“Todo”和“专注”两个标签切换；同一时刻只展示当前选中的页面。
- v1.2：完成分层重构、Todo/专注页面实现、统一视觉、图标接入、测试和 Windows 打包验证。
- v1.3：修复开机自启启动项命令同步，并为 QApplication、主窗口和 Windows AppUserModelID 显式绑定新图标，保证手动启动与开机自启使用同一图标。
- v1.4：收紧顶部标签与页面卡片的间距，降低默认窗口高度和专注卡片空白，并加入右下角鼠标拖拽缩放能力。
- v1.5：以 `DesktopTodoLite.exe` 作为唯一用户启动入口，保留 EXE 开机自启，移除 `start_todo.bat` 和无用辅助文件，并将打包入口收归 `todolite/app/`。
- v1.6：修复资源管理器/开机自启环境下 PySide6 Qt DLL 搜索路径不完整导致的 `QtCore` 加载失败，增加打包运行时 DLL 路径钩子并完成最小 PATH 验证。
- v1.7：修复 Todo 编辑任务和任务统计弹窗的低对比度文字，并移除统计/专注历史弹窗中与系统标题栏重复的内部关闭按钮。
- v1.8：提高任务统计完成趋势图的坐标可读性，并明确左下角自动缩放按钮的用途。
- v1.9：修复 Todo 编辑任务弹窗点击 `OK` 后内容、日期和重要标记未反映到列表的问题，补充保存回写、列表刷新和三项字段回归验证。

> 计划表中的复选框表示实际完成状态。每完成一个实施步骤，都要回到本文件更新对应复选框、状态和必要的备注。

## 2. 当前实现概况

当前项目是一个小型 PySide6 桌面应用，已经按领域、服务、基础设施和表现层拆分；本轮将进一步收敛用户启动入口：

1. `todolite/app/entrypoint.py` 作为仅供 PyInstaller 使用的内部入口，调用 `todolite.app.run()` 创建 Qt 应用并显示主窗口。
2. `DesktopTodoLite.exe` 是唯一面向用户的启动文件；`autostart.py` 直接将该 EXE 的绝对路径写入 Windows 启动项。
3. Todo 与专注页面、任务和专注服务、数据仓储以及窗口设置均保持现有分层，用户数据继续存放在 `.data/`。
3. `Task` 数据模型与 `TaskStore` 位于 `todolite/storage.py`，任务以列表形式存储在 `.data/tasks.json`。
4. `SettingsStore` 负责 `.data/settings.json`，保存窗口置顶、开机自启和日期折叠状态。
5. `autostart.py` 直接操作 Windows 注册表开机启动项。
6. 主界面使用 `QListWidget` 动态重绘日期分组、任务行和已完成任务；拖拽完成后再从列表项的 Qt Role 数据中推导新的日期和排序值。
7. 统计弹窗直接接收当前任务列表，并使用 `pyqtgraph` 绘制最近 30 天的统计曲线。

现有实现适合功能较少的原型，但随着专注记录加入，会出现以下维护问题：

- 窗口类承担太多职责，任务、专注、设置和系统能力会继续耦合。
- UI 直接修改数据对象并触发存储，业务规则难以单元测试。
- JSON 读写、数据清理、排序规则分散在界面代码中。
- 按钮样式和图标没有统一的主题、尺寸、悬浮提示和无障碍名称。
- 目前没有自动化测试目录，重构后需要补充核心业务测试。

## 3. 目标与非目标

### 3.1 本次目标

- 新增一个完整的专注会话功能：命名、开始、正向计时、暂停、继续、结束和历史记录删除。
- 默认只保留最近七天的专注记录，过期记录自动清理。
- 采用清晰的分层目录，把界面、业务、数据模型、持久化和系统能力拆开。
- 对原有 Todo 功能做完整适配：保留原有行为和数据，同时迁移到新的领域服务、数据仓库和表现层目录。
- 将 Todo 和专注设计为两个独立页面，在软件顶部提供“Todo”和“专注”两个标签；点击标签后只展示对应页面。
- 让两个页面使用同一套卡片、标题栏、图标按钮、颜色、间距、字体和空状态组件，形成统一页面风格。
- 保留现有任务数据、任务操作、统计功能、置顶和开机自启能力。
- 使用统一的符号化按钮、悬浮提示、颜色和间距，提升桌面小组件的精致度。
- 使用一个自定义 SVG 图标，同时应用到窗口、快捷方式和 PyInstaller 构建产物。
- 增加核心业务自动化测试和一套手工验收清单。

### 3.2 本次暂不做

- 不引入数据库、云同步、账号系统或网络接口。
- 不实现多个专注会话并行运行；同一时间只允许一个活动会话。
- 不把专注记录自动转换为 Todo 任务，二者保持独立。
- 不改变现有任务的日期含义；任务日期仍是用户安排任务的日期，而不是完成日期。
- Todo 与专注共用表现层基础设施和页面规范，但不强行共用领域模型；任务和专注仍是两种独立业务对象。

## 4. 专注功能设计

### 4.1 用户流程

专注页面包含一个专注卡片，包含：

1. 专注名称输入框，默认提示“这次准备专注什么？”。
2. 开始按钮，使用 `▶` 或播放图标，并提供“开始专注”悬浮提示。
3. 未开始时显示 `00:00:00`。
4. 运行中显示专注名称和正向计时，操作按钮为暂停 `Ⅱ` 和结束 `■`。
5. 暂停后保留已累计时长，按钮变为继续 `▶`，另一个按钮仍为结束 `■`。
6. 结束后立即生成一条专注历史记录，保存名称和累计时长；主界面回到未开始状态。
7. 通过历史按钮 `◷` 打开专注记录弹窗；每条记录右侧提供 `×` 删除按钮。

按钮保留 `toolTip`、`accessibleName` 和必要的状态文字，不能只依赖符号本身，以避免用户不知道按钮含义或系统字体不支持某个符号。

### 4.2 状态机

专注会话只允许以下状态转换：

```text
IDLE --开始--> RUNNING --暂停--> PAUSED
  ^              |                 |
  |              +--结束----------+
  |                                |
  +-------------结束---------------+

PAUSED --继续--> RUNNING
```

规则：

- 名称为空时不能开始，输入内容需去除首尾空格。
- RUNNING 状态只显示一个活动计时器，不能再次创建第二个会话。
- PAUSED 状态不增加时长。
- END 操作把累计时长写入历史记录，然后清除活动状态。
- 结束后的记录可以单独删除，不影响 Todo 任务。
- 退出程序或发生异常关闭时，活动状态应保存在 `.data/focus_state.json`；下次启动恢复当前会话，而不是静默丢失。若上次处于 RUNNING，按照保存的时间戳继续计算；若处于 PAUSED，则从暂停时长继续。

### 4.3 计时实现

UI 层使用 Qt `QTimer` 定期刷新显示，建议刷新间隔为 250ms 或 500ms，但它只负责刷新，不负责保存业务时长。

业务层使用“累计秒数 + 当前运行起点”的方式计算：

- `accumulated_seconds`：之前已经完成的运行区间总时长。
- `running_since`：当前 RUNNING 区间的开始时间；PAUSED 时为空。
- 当前运行时长 = `accumulated_seconds + now - running_since`。
- 暂停时把当前区间合并进 `accumulated_seconds`，并清空 `running_since`。

持久化时间使用带时区的 ISO 8601 时间；计算时统一使用北京时间或明确的 UTC 时间，显示时转换为本地时间。计时显示格式统一为 `HH:MM:SS`，小时数允许超过 24，不采用日期格式。

### 4.4 数据模型

建议新增 `FocusSession`：

```python
FocusSession(
    id: str,
    name: str,
    duration_seconds: int,
    started_at: str,
    ended_at: str,
)
```

活动中的临时状态建议单独使用 `FocusState`：

```python
FocusState(
    status: Literal["idle", "running", "paused"],
    name: str,
    accumulated_seconds: int,
    started_at: str | None,
    running_since: str | None,
)
```

这样历史记录是不可变的完成结果，活动状态是可恢复的编辑中数据，二者不会混在同一个列表里。

### 4.5 专注记录保留策略

- 记录保存到 `.data/focus_sessions.json`。
- 默认保留最近七个自然日，包括今天，即 `record_date >= today - 6 days`。
- 记录日期以 `ended_at` 的北京时间日期为准，而不是 Todo 的 `task_date`。
- 应用启动时清理一次；新记录生成后再清理一次。
- 删除单条记录立即写盘并刷新列表。
- 清理只针对已结束记录，不影响当前活动会话。
- “后台生成”在本项目中表示结束后自动写入独立的历史数据，不插入 Todo 列表；由于 JSON 文件很小，不需要为此引入线程。

### 4.6 原有 Todo 功能改造设计

原有 Todo 不是只做代码搬迁，而是和专注功能一起适配新的架构与页面规范。所有原有 Todo 能力都要通过新的任务服务完成，再由新的任务 UI 展示。

#### 功能保持

以下行为保持不变，重构后必须通过回归测试：

- 回车添加任务，并可选择任务日期和重要标记。
- 按日期分组，日期倒序显示；未完成任务位于已完成任务之前。
- 重要任务使用图标或强调色区分，并保持当前的优先排序逻辑。
- 点击左侧复选框切换完成状态，完成任务显示删除线。
- 双击任务文本编辑内容、日期和重要状态。
- 删除任务、拖拽排序，以及把未完成任务拖到其他日期组并同步任务日期。
- 每个日期组可以折叠或展开已完成任务。
- 两天前的已完成任务只从主列表隐藏，不立即删除；已完成记录仍可进入统计窗口。
- 已完成任务按现有 30 天规则清理，未完成任务不能被自动清理。

#### Todo 页面改造

Todo 和专注属于两个独立页面，不同时堆叠在同一页面中。主窗口只负责顶部标签导航和页面容器，用户通过顶部标签在两个页面之间切换：

1. 顶部固定显示两个标签：`Todo` 和 `专注`；当前标签使用强调色、底部指示线或高亮背景表示。
2. 点击 `Todo` 标签时，页面容器只显示 Todo 页面；点击 `专注` 标签时，页面容器只显示专注页面。
3. 使用 `QStackedWidget` 或等价的页面栈承载两个页面，不能通过把两个页面内容同时放在一个布局中再隐藏零散控件来实现。
4. Todo 页面内部使用与专注页面相同的 `SurfaceCard`、标题栏、圆角、边距和背景层级。
5. Todo 标题栏使用 `✓` 或任务清单 SVG，右侧放置统计 `▥`、更多 `⋯` 等图标按钮。
6. 添加任务区域保持“输入框 + 日期选择 + 重要开关 + 回车提交”的效率优先交互；可增加 `＋` 图标按钮作为鼠标操作入口，但不能取消回车提交。
7. 日期分组标题使用统一的 `SectionHeader`，配合展开/收起箭头和已完成数量，不再使用孤立的纯文本按钮。
8. 任务行使用统一的 `TaskRow`：复选框、任务文本、重要标识和 `×` 删除按钮的尺寸、间距和悬浮效果与专注记录行一致。
9. 空任务列表使用共享的 `EmptyState` 组件，例如显示“今天还没有任务，先安排一件小事吧”。
10. 任务统计弹窗沿用统一的窗口外观、关闭按钮、卡片和列表样式；图表数据由统计服务提供，而不是由窗口直接扫描任务列表。

#### 页面切换与状态保持

- 顶部标签栏属于主窗口壳层，不属于 Todo 页面或专注页面，切换逻辑集中在 `navigation.py`。
- 页面切换只改变当前显示页面，不销毁页面对象；返回某个页面时应保留该页面的滚动位置、输入内容和专注计时显示。
- 专注计时不依赖当前是否正在显示专注页面；切换到 Todo 页面后，专注服务和 `QTimer` 仍继续运行，切回专注页面时显示最新时长。
- Todo 页面和专注页面各自处理内部交互，但不能直接切换对方的控件；跨页面通信通过主窗口控制器或应用服务完成。
- 标签必须支持鼠标点击、键盘焦点和快捷键（建议 `Ctrl+1` 切换 Todo、`Ctrl+2` 切换专注），并提供明确的 active/inactive 样式。

#### Todo 与专注的共用代码

两类功能必须共用以下表现层和基础设施，不能各写一套相似实现：

| 共用模块 | Todo 使用方式 | 专注使用方式 |
|---|---|---|
| `SurfaceCard` | Todo 主卡片、统计卡片 | 专注主卡片、历史记录卡片 |
| `SectionHeader` | 日期分组标题、统计区域标题 | 专注标题、历史区域标题 |
| `IconButton` | 统计、菜单、删除、折叠 | 开始、暂停、继续、结束、历史、删除 |
| `theme.py` | 任务文本、完成态、重要态、危险操作颜色 | 运行态、暂停态、结束态、历史颜色 |
| `metrics.py` | 任务行高度、分组间距、输入区域尺寸 | 计时器、按钮和记录行尺寸 |
| `formatters.py` | 日期、任务提示和空状态文字 | `HH:MM:SS`、记录日期和时长文字 |
| 资源加载器 | 任务、统计、菜单、删除图标 | 播放、暂停、停止、历史、删除图标 |

业务层不共用任务和专注的具体规则，但共用同一套 repository 基类约定、原子 JSON 写入、时钟接口和错误处理方式。

#### Todo 服务拆分

`task_service.py` 应提供清晰的任务用例，而不是让窗口直接修改 `self.tasks`：

- `list_grouped_for_display()`：按日期分组并应用活动/完成/重要/顺序规则。
- `add_task()`：校验内容、日期和重要状态，生成 ID 与排序值。
- `complete_task()`：切换完成状态并重排活动任务。
- `edit_task()`：修改内容、日期和重要状态；跨日期时重新计算顺序。
- `delete_task()`：按 ID 删除。
- `reorder_tasks()`：接收 UI 报告的可见任务顺序，更新顺序和跨组日期。
- `toggle_completed_group()`：保存每个日期的完成组折叠状态。

`main_window.py` 只负责把按钮和拖拽信号转发给 `task_service`，接收结果后刷新 Todo 卡片；它不能直接访问 `.data/tasks.json`，也不能把任务排序规则重新写回窗口类。

## 5. 目标代码结构

重构采用“领域模型—应用服务—基础设施—表现层”的轻量分层，不引入复杂框架。建议目录如下：

```text
TODOList/
├─ DesktopTodoLite.exe             # 唯一用户启动入口（构建产物）
├─ DesktopTodoLite.spec            # PyInstaller 单文件构建配置
├─ requirements.txt
├─ README.md
├─ assets/
│  ├─ icon.svg                     # 主图标源文件
│  ├─ icon.ico                     # Windows 构建图标
│  └─ icons/                       # 播放、暂停、结束、删除、统计等 SVG
├─ docs/
│  └─ IMPROVEMENT_PLAN.md
├─ tests/
│  ├─ unit/
│  │  ├─ test_task_service.py
│  │  ├─ test_focus_service.py
│  │  ├─ test_retention_service.py
│  │  └─ test_json_repository.py
│  └─ fixtures/
├─ todolite/
│  ├─ __init__.py
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ bootstrap.py              # QApplication、主题、资源和窗口组装
│  │  ├─ entrypoint.py             # 仅供 PyInstaller 使用的内部入口
│  │  └─ window_controller.py      # 主窗口事件编排
│  ├─ domain/
│  │  ├─ __init__.py
│  │  ├─ task.py                   # Task 模型和任务排序值对象
│  │  ├─ focus.py                  # FocusSession、FocusState、状态定义
│  │  └─ settings.py               # 设置模型和默认值
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ task_service.py           # 添加、编辑、完成、删除、排序、分组
│  │  ├─ focus_service.py          # 开始、暂停、继续、结束、恢复
│  │  ├─ retention_service.py      # 任务和专注历史清理策略
│  │  └─ statistics_service.py     # 统计聚合，不依赖 Qt 控件
│  ├─ infrastructure/
│  │  ├─ __init__.py
│  │  ├─ paths.py                  # 数据目录和资源目录
│  │  ├─ clock.py                  # 可替换的系统时钟和业务日期
│  │  ├─ json_store.py             # 通用原子 JSON 读写
│  │  ├─ task_repository.py        # 任务数据适配与兼容旧格式
│  │  ├─ focus_repository.py       # 专注记录和活动状态读写
│  │  ├─ settings_repository.py    # 设置读写
│  │  └─ autostart.py              # Windows 注册表能力
│  └─ presentation/
│     ├─ __init__.py
│     ├─ windows/
│     │  ├─ main_window.py         # 主窗口外壳、顶部标签和页面栈
│     │  └─ focus_history_dialog.py
│     ├─ pages/
│     │  ├─ todo_page.py           # 独立 Todo 页面
│     │  └─ focus_page.py          # 独立专注页面
│     ├─ widgets/
│     │  ├─ task_list.py
│     │  ├─ task_row.py
│     │  ├─ task_group_header.py
│     │  ├─ surface_card.py         # Todo 和专注共用卡片容器
│     │  ├─ section_header.py       # Todo 分组和专注区域共用标题
│     │  ├─ empty_state.py          # Todo、历史记录共用空状态
│     │  ├─ tab_bar.py              # 顶部 Todo/专注标签栏
│     │  ├─ focus_record_row.py
│     │  └─ icon_button.py
│     ├─ dialogs/
│     │  ├─ task_edit_dialog.py
│     │  └─ statistics_dialog.py
│     ├─ styles/
│     │  ├─ theme.py               # 全局 QSS 和颜色常量
│     │  └─ metrics.py             # 尺寸、圆角、间距、字号
│     └─ formatters.py              # 时长、日期、提示文本格式化
└─ pyproject.toml                  # 可选：测试、格式化和构建配置
```

### 5.1 各层职责

| 层级 | 主要职责 | 不应该做的事 |
|---|---|---|
| `domain` | 定义任务、专注记录、活动状态和纯数据规则 | 不导入 PySide6，不读写文件 |
| `services` | 编排业务操作和状态转换 | 不创建 Qt 控件，不直接依赖具体 JSON 文件名 |
| `infrastructure` | 文件、路径、注册表、时间和外部系统适配 | 不决定界面如何显示 |
| `presentation` | 主窗口外壳、顶部标签、Todo 页面、专注页面、控件、信号和视觉布局 | 不直接拼 JSON，不实现复杂业务规则 |
| `app` | 依赖注入和应用启动 | 不承载具体任务逻辑 |

核心调用链统一为：

```text
Qt 控件事件
  -> window_controller
  -> task_service / focus_service
  -> repository
  -> 返回新状态
  -> presentation 刷新
```

所有服务通过构造函数接收 repository 和 clock，测试时可以注入临时目录和可控时钟，不需要启动真实窗口。

### 5.2 现有代码迁移映射

| 现有代码 | 重构后去向 | 迁移说明 |
|---|---|---|
| `todolite/storage.py::Task` | `domain/task.py` | 保留字段和旧 JSON 字段名 |
| `todolite/storage.py::TaskStore` | `infrastructure/task_repository.py` | 抽取通用原子 JSON 读写 |
| `todolite/settings_store.py` | `domain/settings.py` + `infrastructure/settings_repository.py` | 设置模型与文件操作分离 |
| `todolite/paths.py` | `infrastructure/paths.py` | 增加资源目录和专注数据路径 |
| `todolite/ui.py::TodoWindow` 的数据与操作逻辑 | `services/task_service.py` | 把任务增删改、完成、分组、排序和清理从窗口中移出 |
| `todolite/autostart.py` | `infrastructure/autostart.py` | 只保留系统注册表适配 |
| `ui.py::TodoWindow` 的窗口布局 | `presentation/windows/main_window.py` + `presentation/widgets/tab_bar.py` | 只负责组装顶部标签、页面栈和共用菜单 |
| 原有 Todo 页面内容 | `presentation/pages/todo_page.py` | Todo 独立页面，只保留任务输入、分组列表和 Todo 统计入口 |
| 新增专注页面内容 | `presentation/pages/focus_page.py` | 专注独立页面，只保留专注面板和历史入口 |
| `ui.py::TaskListWidget` | `presentation/widgets/task_list.py` | 保留拖拽能力，改为向任务服务报告顺序 |
| `ui.py::GroupHeaderRow` | `presentation/widgets/task_group_header.py` + `section_header.py` | 日期分组标题使用共用标题组件 |
| `ui.py::TaskRow` | `presentation/widgets/task_row.py` + `icon_button.py` | 保留复选框、重要标记和编辑入口，删除改为统一 `×` 图标 |
| `ui.py::TaskEditDialog` | `presentation/dialogs/task_edit_dialog.py` | 只负责编辑表单和校验展示，保存交给任务服务 |
| `ui.py::TaskStatsDialog` | `presentation/dialogs/statistics_dialog.py` | 图表数据由 `statistics_service` 提供 |

迁移过程中先保留原有行为，再逐步替换调用方，避免一次性重写导致功能回归。

## 6. 页面与视觉改进

### 6.1 视觉方向

保留当前半透明悬浮卡片的特点，但统一成“轻量桌面工具”风格：

- 主背景使用深蓝灰半透明渐变，卡片层级更清晰。
- 主操作使用一枚强调色，危险操作使用低饱和红色。
- 统一圆角、内边距、控件高度和字体层级。
- 专注卡片在运行状态下使用轻微强调边框或呼吸色，不使用过度动画。
- Todo、专注和统计分别位于对应页面/弹窗中，但使用同一套卡片容器和视觉层级，避免功能各自使用一套风格。

### 6.2 符号和图标规范

| 功能 | 推荐符号/图标 | 交互要求 |
|---|---|---|
| 开始专注 | `▶` | tooltip：开始专注 |
| 暂停 | `Ⅱ` 或暂停 SVG | tooltip：暂停专注 |
| 继续 | `▶` | tooltip：继续专注 |
| 结束 | `■` 或停止 SVG | tooltip：结束并保存 |
| 删除 | `×` | tooltip：删除；危险色；支持确认 |
| 历史记录 | `◷` | tooltip：专注历史 |
| 统计 | `▥` 或统计 SVG | tooltip：任务统计 |
| 重要任务 | `❗` 或星标 SVG | 保留文字/提示，避免仅靠颜色区分 |
| 菜单 | `⋯` | tooltip：更多设置 |

优先使用自带 SVG/Qt 图标保证跨字体一致性；emoji 只作为任务重要标识或轻量装饰，不让核心操作依赖 emoji 字体。

### 6.3 专注历史弹窗

弹窗显示：

- 标题“专注历史”。
- 最近七天的记录，按结束时间倒序。
- 每项显示名称、日期、时长，例如 `论文实验 · 01:25:40`。
- 空状态显示友好提示，而不是空白区域。
- 删除按钮为 `×`，点击后删除对应记录并立即保存。
- 窗口支持拖动、关闭按钮、键盘焦点和 tooltip。

### 6.4 顶部标签和两个页面的统一展示规范

- 主窗口顶部固定显示两个标签：`Todo` 和 `专注`；标签栏下方只有当前标签对应的页面内容。
- 标签栏使用统一的高度、左右间距、字体和 active/inactive 状态；当前标签使用强调色或底部指示线，未选中标签降低对比度。
- Todo 页面和专注页面使用相同的页面内边距、`SurfaceCard` 背景、圆角、边框和内容宽度策略。
- 两个页面标题栏使用相同的“左侧功能图标 + 标题 + 右侧图标操作”布局。
- 两类列表行使用相同的高度、左右内边距、删除按钮位置和悬浮反馈。
- Todo 的完成态、专注的暂停态都使用低饱和弱化颜色；活动态和重要态使用强调色，但不只依赖颜色传达信息。
- Todo 的 `×` 删除按钮与专注历史的 `×` 删除按钮共用组件和危险操作样式。
- Todo 的统计和专注历史都使用统一的弹窗边框、关闭按钮、列表背景和空状态组件。
- 页面中的文字按钮只保留必要的标题和说明，操作按钮优先使用图标，并为所有图标提供 tooltip、accessible name 和键盘焦点。

### 6.5 页面高度与窗口缩放

- 默认主窗口调整为约 `430×420`，减少专注页面下方卡片的无效留白；Todo 列表在较小窗口中继续通过列表区域滚动展示。
- 标签栏与页面卡片之间使用紧凑间距，页面内边距统一收紧，Todo 和专注仍保持相同的卡片布局规则。
- 无边框窗口右下角提供可见的缩放手柄，鼠标拖动可同时调整窗口宽度和高度。
- 设置最小窗口尺寸为 `360×360`，保证输入框、计时器、操作按钮和标签仍有可用空间。
- 缩放手柄使用独立的 `ResizeGrip` 组件，窗口尺寸变化后自动重新定位，不参与 Todo 或专注业务逻辑。

## 7. 图标设计与发布方式

### 7.1 图标方案

设计一个简单的“勾选 + 时钟”组合符号：

- 外形：圆角方形或圆形底板，适配 Windows 小图标。
- 主图形：白色勾选线，右上或旁侧叠加一个小型时钟/进度圆环。
- 背景：蓝紫到青绿色的简洁渐变，与主窗口深蓝灰风格协调。
- 线条粗细和留白按 16、24、32、48、64、128、256 像素分别检查。
- 小尺寸下优先保证轮廓可识别，去掉过细的装饰。

### 7.2 使用位置

1. 在 `assets/icon.svg` 保存可编辑源文件。
2. 必要时生成 `assets/icon.ico`，包含 Windows 常用尺寸。
3. 启动时通过 `QApplication.setWindowIcon(QIcon(...))` 设置窗口图标。
4. PyInstaller 构建时通过 `--icon assets/icon.ico` 或 `.spec` 文件设置 exe 图标。
5. 资源路径使用统一的 `resource_path()`，兼容源码运行和 PyInstaller one-file 模式。
6. 不把二进制图标散落到业务模块中，所有图标由资源层统一加载。

### 7.3 Windows 开机自启图标修复

Windows 的 `Run` 注册表项只保存启动命令，本身没有独立的图标字段；开机后任务栏/窗口显示的图标来自启动进程的 exe、AppUserModelID 和窗口图标。因此统一处理以下三层：

1. `autostart.py` 根据当前运行方式生成启动命令：打包运行指向 `DesktopTodoLite.exe`，源码运行优先指向 `pythonw.exe` 和当前入口脚本。
2. 当设置仍为开启时，应用启动阶段自动检查并修复缺失或过期的 `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run` 值，避免旧路径继续启动旧程序。
3. 启动 QApplication 前设置固定的 Windows AppUserModelID，创建主窗口时再次设置新图标，确保 Windows 将窗口归属于带新图标的应用。

若历史环境中的启动项已丢失，用户只需正常启动一次应用；若 Windows 仍缓存旧入口，可在设置中关闭再开启一次“开机自启”。

### 7.4 单一 EXE 启动与发布方式

本轮调整后，用户侧只保留双击 `DesktopTodoLite.exe` 这一种启动方式：

1. 将 PyInstaller 的分析入口从根目录 `main.py` 收归 `todolite/app/entrypoint.py`，根目录不再保留可被误认为启动器的 Python 文件。
2. 使用 PyInstaller one-file、windowed 模式生成根目录 `DesktopTodoLite.exe`，内置新图标和 `assets` 资源；用户直接双击该文件即可运行。
3. 开机自启继续使用当前 EXE 的绝对路径写入 `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`，不再依赖 BAT、conda 或 Python 命令。
4. 启动时校验旧的 Run 值：如果仍指向旧 BAT、旧脚本或旧 EXE，会自动替换为当前 `DesktopTodoLite.exe`。
5. 删除 `start_todo.bat` 及确认未被代码、测试、构建引用的临时说明文件；保留 `requirements.txt`、spec、测试和正式文档，便于后续维护和重新发布。
6. 不删除 `.data`，继续兼容现有 Todo、设置和专注记录；打包 EXE 旁边的 `.data` 仍作为运行数据目录。

### 7.5 PySide6 打包运行时兼容

PyInstaller one-file EXE 解包后，PySide6 的 `QtCore.pyd`、`Qt6Core.dll` 和 `shiboken6` DLL 位于不同子目录；资源管理器和 Windows 开机自启不一定继承开发环境的 PATH。为避免 `DLL load failed while importing QtCore`：

1. 在 PySide6 及业务模块导入前执行 `qt_runtime_hook.py`。
2. 将临时解包根目录、`PySide6` 和 `shiboken6` 目录注册到 Windows DLL 搜索路径及 PATH。
3. 继续由 PyInstaller 官方 Qt hook 收集 Qt、插件、VC 运行库和资源文件。
4. 用最小 PATH 启动 `DesktopTodoLite.exe`，确认程序保持运行，验证其不依赖 Anaconda/Python 环境。

## 8. 数据兼容与迁移

- 继续读取现有 `.data/tasks.json`，字段保持 `id/text/completed/created_at/task_date/important/order`。
- 继续读取现有 `.data/settings.json`，未知设置字段忽略，缺失字段使用默认值。
- 新增 `.data/focus_sessions.json` 和 `.data/focus_state.json`；文件不存在时按空历史、空活动状态处理。
- 读取旧任务时保留当前的容错逻辑：文件损坏、非列表、空任务内容不能导致应用崩溃。
- 通用 JSON 存储类继续使用临时文件和原子替换；写入失败时要向上层返回可处理的错误。
- 重构完成后先用当前 `.data` 做回归测试，再测试空目录启动和损坏 JSON 启动。
- 不在本次任务中删除旧文件，不自动清理用户未完成的任务。
- Todo 与专注必须共用表现层基础组件；禁止为两类功能复制两份卡片、标题栏、图标按钮和空状态样式。
- Todo 与专注必须是两个独立页面，通过顶部标签和页面栈切换；不能把两套主要内容同时展示在一个页面中。

## 9. 测试与验收标准

### 9.1 单元测试

- 开始专注时名称为空、只有空格时会被拒绝。
- RUNNING → PAUSED 后时长停止增加。
- PAUSED → RUNNING 后从原累计时长继续。
- 多次暂停/继续的总时长计算正确。
- 结束会生成正确名称、时长和时间戳的记录。
- 结束后活动状态被清空，不能重复结束生成重复记录。
- 活动状态重启恢复正确。
- 七天边界内记录保留，边界外记录被清理。
- 单条删除只删除指定 ID。
- 损坏或缺失的专注 JSON 不会阻止程序启动。
- 原有 Todo 的添加、完成、编辑、删除、分组、排序、折叠、统计和保留策略不回归。
- Todo 和专注卡片使用同一套卡片容器、标题栏、按钮、间距、颜色和资源加载器。
- 顶部存在 `Todo` 和 `专注` 两个标签，切换后只展示选中的页面；切换过程中专注计时不会停止，Todo 页面状态不会丢失。

### 9.2 手工验收

- 启动应用后主窗口图标和 exe 图标均为新图标。
- 开始专注后计时从 `00:00:00` 开始并持续增长。
- 暂停后等待数秒，显示时间不变；继续后继续增长。
- 结束专注后历史中出现一条记录，重启应用后仍存在。
- 删除历史记录后立即消失，重启后不会恢复。
- 专注期间 Todo 任务仍可正常查看和操作。
- Todo 和专注在主窗口中具有一致的卡片层级、标题栏、列表行、删除按钮和空状态表现。
- Todo 原有的回车添加、双击编辑、复选框完成、拖拽排序和跨日期拖拽全部可用。
- 任务行、专注按钮、统计按钮和菜单按钮的符号、悬浮提示及点击范围清晰。
- 较长任务名称、较长专注名称和较长计时不会破坏布局。
- 空历史、空任务列表和不同日期下的页面布局正常。
- Windows 开机自启和窗口置顶功能仍可用。

### 9.3 完成标准

只有满足以下条件，才认为本次改进完成：

1. 计划表全部实施项完成并打勾。
2. 现有任务数据在重构前后内容一致。
3. 专注的开始、暂停、继续、结束、恢复、清理和删除均通过测试。
4. 新窗口和图标在直接点击 EXE、Windows 开机自启和 PyInstaller 构建中可用；用户侧不再需要启动脚本。
5. 没有把业务逻辑重新集中回单个窗口文件。
6. README 更新了新的运行方式、数据文件和构建说明。

## 10. 分阶段实施计划

| 完成 | 编号 | 步骤 | 主要产出 | 验证方式 |
|---|---:|---|---|---|
| [x] | 0 | 阅读现有代码并形成改进方案 | 本文档 | 方案覆盖专注、原有 Todo 适配、顶部双标签页面、共用结构、页面、图标、测试和验收 |
| [x] | 1 | 建立新目录和共用基础模块 | `domain/`、`services/`、`infrastructure/`、`presentation/`、`tests/` 以及共用卡片/标题/图标按钮 | 目录与公共 UI 组件已建立并完成导入验证 |
| [x] | 2 | 抽取通用 JSON 存储和路径能力 | `json_store.py`、新的 repository 和资源路径 | 已完成原子读写、损坏文件容错、数据路径和统一北京时间时钟验证 |
| [x] | 3 | 迁移原有 Todo 领域模型和任务服务 | `domain/task.py`、`task_service.py` | 已迁移任务模型、增删改、完成、分组、排序和清理逻辑，并完成服务级验证 |
| [x] | 4 | 拆分并改造原有 Todo 页面 | `presentation/pages/todo_page.py`、任务列表、任务行、编辑弹窗 | Todo 页面已独立并接入 TaskService，完成空列表、添加、分组、完成态、编辑、删除和拖拽链路验证 |
| [x] | 5 | 实现专注领域模型和可控时钟 | `domain/focus.py`、clock 接口 | 已加入 FocusSession/FocusState、状态校验和统一北京时间时钟，并完成模型验证 |
| [x] | 6 | 实现专注 repository 和七天清理 | `focus_repository.py`、`retention_service.py` | 已分离保存历史/活动状态，并完成七天边界、排序和容错验证 |
| [x] | 7 | 实现专注服务和状态恢复 | `focus_service.py`、活动状态持久化 | 已完成开始、暂停、继续、结束、重复状态校验和活动状态持久化，并通过可控时钟验证 |
| [x] | 8 | 实现独立专注页面和专注历史弹窗 | `presentation/pages/focus_page.py`、`focus_record_row.py`、`focus_history_dialog.py` 已接入共用组件 | 已验证开始、暂停、继续、结束、历史展示和记录删除链路 |
| [x] | 9 | 抽取统计服务和迁移统计弹窗 | `statistics_service.py`、`statistics_dialog.py` | 统计聚合已脱离窗口，并完成 30 天曲线和日期明细验证 |
| [x] | 10 | 统一 Todo/专注主题和符号化按钮 | `theme.py`、`metrics.py`、`icon_button.py`、`surface_card.py`、SVG 图标 | 两类页面已接入统一主题、卡片、列表行、删除按钮、空状态和符号操作，并通过 offscreen 验证 |
| [x] | 11 | 设计并接入新软件图标 | `assets/icon.svg`、`assets/icon.ico`、Qt 资源加载 | 已完成勾选+时钟图标设计、SVG/ICO 资源和窗口图标加载验证 |
| [x] | 12 | 接入主窗口顶部双标签和页面栈 | `main_window.py`、`tab_bar.py`、`QStackedWidget` 页面容器 | 已接入顶部 Todo/专注双标签、页面栈和 Ctrl+1/Ctrl+2 快捷键，并验证切换时计时器保持运行 |
| [x] | 13 | 接入新的应用组装入口 | `bootstrap.py`、`window_controller.py`、原入口 | 已完成服务组装、全局主题、窗口图标和主入口导入验证；本轮将入口进一步收归 `app/entrypoint.py` |
| [x] | 14 | 完成回归测试和构建验证 | 测试报告、PyInstaller 构建产物 | 8 个单元测试通过、compileall 通过、offscreen 页面回归通过，PyInstaller exe 已生成并完成启动冒烟测试 |
| [x] | 15 | 更新文档并清理旧实现 | README、迁移说明、无重复旧模块 | README 已更新，旧集中式模块已移除，引用核对、编译和测试通过 |
| [x] | 16 | 修复 Windows 开机自启与新图标一致性 | `autostart.py`、`windows_identity.py`、`bootstrap.py`、`main_window.py` | 启动项缺失/过期时自动同步当前命令；应用、窗口和 PyInstaller 构建均显式使用新图标；测试、编译和打包启动冒烟通过 |
| [x] | 17 | 收紧页面布局并加入窗口手动缩放 | `metrics.py`、`resize_grip.py`、`main_window.py`、Todo/专注页面 | 默认窗口高度降至 420，标签与卡片间距缩小，右下角拖拽可同时调整宽高，8 个单元测试、编译和 offscreen 缩放冒烟测试通过 |
| [x] | 18 | 改为 EXE 单一启动入口并清理旧启动方式 | `todolite/app/entrypoint.py`、`DesktopTodoLite.spec`、`autostart.py`、README、清理文件 | 根目录已生成可直接双击的 `DesktopTodoLite.exe`；开机自启继续由当前 EXE 命令维护；已移除 `start_todo.bat` 和未引用辅助文件；回归测试、打包启动和启动项命令检查通过 |
| [x] | 19 | 修复打包后 QtCore DLL 加载失败 | `todolite/app/qt_runtime_hook.py`、`DesktopTodoLite.spec`、README | EXE 内置 Qt DLL 和运行时钩子；最小 Windows PATH 启动保持运行；单元测试和编译检查通过 |
| [x] | 20 | 修复弹窗文字对比度并去除重复关闭按钮 | `theme.py`、`task_edit_dialog.py`、`statistics_dialog.py`、`focus_history_dialog.py` | 编辑任务和任务统计文字清晰可读；统计与专注历史仅保留系统标题栏关闭按钮；8 个单元测试、compileall、offscreen UI 冒烟和新版 EXE 最小 PATH 启动验证通过 |
| [x] | 21 | 加深完成趋势图坐标并说明自动缩放控件 | `statistics_dialog.py`、`IMPROVEMENT_PLAN.md` | 横纵坐标刻度文字和轴线已提高对比度；保留左下角 `A` 自动缩放按钮并增加“自动缩放图表”提示；8 个单元测试、compileall、offscreen UI 冒烟和新版 EXE 最小 PATH 启动验证通过 |
| [x] | 22 | 修复 Todo 编辑任务保存后列表未同步 | `todo_page.py`、任务服务及 `tests/unit/test_todo_page.py` | 修正 PySide6 对话框结果常量判断，避免点击 `OK` 后在取值前抛出实例属性错误；内容、日期和重要标记均写回并立即反映在新日期分组；9 个单元/UI 回归测试、compileall 及打包启动验证通过 |

## 11. 风险与处理方式

| 风险 | 影响 | 处理方式 |
|---|---|---|
| 重构过程中任务行为变化 | 用户已有任务排序或显示异常 | 先写任务服务测试，保留旧 JSON 字段和回归数据 |
| 程序异常退出造成专注丢失 | 用户专注时间丢失 | 每次状态变化立即保存活动状态，启动时恢复 |
| 系统时间被修改 | 时长计算异常 | 对运行区间做非负保护，必要时记录异常并使用累计值 |
| Windows 字体不支持某些 emoji | 按钮显示方框 | 核心按钮使用 SVG，emoji 只做非关键装饰 |
| PyInstaller 找不到资源 | 发布版缺少图标或图标按钮 | 统一资源路径和构建参数，构建后在干净目录验证 |
| 主窗口继续膨胀 | 后续功能难以维护 | 规定 UI 不直接读写 JSON，新增能力必须经过 service/repository |
| 北京时间与系统本地时间不一致 | 日期边界显示不一致 | 引入统一时钟和日期工具，所有业务日期明确使用北京时间 |

## 12. 后续维护约定

- 新增功能先增加领域模型/服务，再接入 UI。
- UI 文件只负责布局、信号连接和展示状态，不直接操作文件。
- 所有持久化数据都要有容错读取和原子写入。
- 每完成计划表中的一个步骤，立即更新本文档的复选框和验证结果。
- 若实现过程中改变需求或目录方案，在“文档信息”或对应章节补充变更记录。
