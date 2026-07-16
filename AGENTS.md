# AGENTS.md

## 语言

- 默认使用简体中文回答。代码、命令、报错、API 名称保持原文。

## 项目概况

NetEase 版 Minecraft 基岩版 Music Plus 附加包。多种方块乐器 + 纸带物品，支持 MIDI 解析/播放。

**不是**常规 Python 包——没有 pytest、pyproject.toml、package.json、CI、Gradle、lint/typecheck 脚本。 脚本依赖运行时 `mod.*`
API，本地无法 import 或 py_compile。 脚本语言为严格的 **CPython 2.7**，不需要考虑向 Python 3 的升级兼容。

## 结构

```
bp/                                 # Behavior pack
  manifest.json                     # format_version: 2, min_engine_version: [1, 19, 0]
  music_plus_scripts/
    modMain.py                      # 入口：EasyMod 注册所有 server/client 模块
    QuModLibs/                      # 框架（勿改，除非目标就是框架本身）
    server/                         # 服务端逻辑
    client/                         # 客户端逻辑（含 music/ MIDI 播放引擎）
    mido/                           # Vendored MIDI 解析库
    utils/                          # 通用工具模块
  netease_blocks/music_plus/        # 方块行为 JSON（每种乐器一个）
  netease_items_beh/music_plus/     # paper_tape.json
  netease_tab/, netease_group/      # 创造模式分类

rp/                                 # Resource pack
  manifest.json                     # format_version: 2, min_engine_version: [1, 19, 0]
  blocks.json                       # 方块声音定义
  sounds/sound_definitions.json     # 乐器采样映射
  sounds/music_plus/<instrument>/   # .ogg 采样文件
  textures/terrain_texture.json     # 方块纹理映射
  textures/item_texture.json        # 物品图标映射
  texts/zh_CN.lang                  # 仅中文，无 en_US.lang

.ref/                               # gitignored 参考资料，非交付源码
```

## 模块注册（关键）

新增 **事件监听或网络端点**模块须在 `modMain.py` 中通过 `MUSIC_PLUS_MOD.Server()` / `.Client()`
注册，否则运行时不会加载。完整的注册列表以 `modMain.py` 为准。

## 客户端/服务端通信

- 客户端和服务端是 **隔离的运行时**。跨侧通信只能用 QuMod 的 `Call` / `@AllowCall`。
- 服务端→客户端主要调用：`Call("*", "play_midi_music", {...})`、`Call("*", "stop_music_at_pos", {...})`。
- 客户端→服务端：`Call(player_id, "write_paper_tape_midi", {...})`。
- 服务端事件装饰器：`@Listen(Events.ServerItemUseOnEvent)` 等（from `QuModLibs.Server`）。
- 客户端可调用函数：`@AllowCall`（from `QuModLibs.Client`）。

## 方块乐器注册表

所有方块乐器在 `server/action/block_instrument.py` 的 `BLOCK_INSTRUMENT_REGISTRY` 中定义（以该文件为准）。

每种乐器在以下位置 **必须保持同步**（漏改任何一处都会导致问题）：

| 数据       | 路径模式                                                          |
|------------|-------------------------------------------------------------------|
| 方块行为   | `bp/netease_blocks/music_plus/<name>.json`                        |
| 方块纹理键 | `rp/textures/terrain_texture.json` 中 `music_plus:<name>`         |
| 方块声音   | `rp/blocks.json` 中 `music_plus:<name>`                           |
| 采样文件   | `rp/sounds/music_plus/<name>/*.ogg`                               |
| 采样映射   | `rp/sounds/sound_definitions.json` 中 `music_plus.<name>.*`       |
| 语言名称   | `rp/texts/zh_CN.lang` 中 `tile.music_plus:music_plus_<name>.name` |
| 脚本注册   | `BLOCK_INSTRUMENT_REGISTRY`                                       |

物品 `music_plus:paper_tape` 的耦合文件：

- 行为：`bp/netease_items_beh/music_plus/paper_tape.json`
- 资源：`rp/netease_items_res/music_plus/paper_tape.json`
- 图标：`rp/textures/item_texture.json`
- 语言：`rp/texts/zh_CN.lang`

命名空间统一为 `music_plus`。方块 ID 格式为 `music_plus:music_plus_<name>`。

## 禁忌

- **勿改 `QuModLibs/`**——除非目标就是框架。
- **勿发明构建/测试/lint 命令**——不存在。
- **勿本地执行 Python**——`mod.*` 只在游戏运行时可用。
- **勿单侧改 ID**——方块/物品 ID 在行为 JSON、资源 JSON、纹理映射、语言文件、声音定义、脚本间耦合。
- **勿信 `.ref/`**——仅供参考，当前行为以 `bp/`、`rp/` 为准。
- **勿信编辑器/运行时状态文件**——`studio.json`、`.mcdev.json`、`.mcs`、`work.mcscfg` 等是 gitignored 本地状态。
- **勿过度拆分函数**——保持一般的通用性和可读性即可，非必要不要把一个函数拆得过于琐碎。

## SDK 特性

- 部分模块注册路径是 **字符串**；移动或重命名相关的模块文件/类时，须同步更新 `modMain.py` 中的注册字符串。
- 查询网易游戏 API 时，优先使用 Context7（library ID
  `/mcneteasedevs/mc-netease-sdk`，<https://context7.com/mcneteasedevs/mc-netease-sdk>），其次再用通用搜索。
- QuModLibs 框架文档：<https://qumod.cc/>。
- 仓库中大量 JSON 遵循微软基岩版内容格式；遇到 Bedrock JSON/schema 问题时优先查阅 <https://wiki.bedrock.dev/>，不要猜字段名或结构。
- 客户端和服务端是 **独立运行时**。跨侧通信必须走现有的 `Call` / `@AllowCall` 流程，不要假设本地事件广播能穿越边界。
- `BlockEntityData` **不是**普通 dict：不要对它使用 `in`、`has_key` 或其他标准字典成员检查。判断某个 key 是否存在/已初始化时，先读取值（如
  `value = be_data["foo"]`），再检查该值是否为 `None`；初始化默认值也用同样的模式。
- 事件回调的参数字典结构是 **固定的**，直接用 `args["key"]` 取值即可；不要用 `.get()` 再做空值防御或
  try/except——这些参数由引擎保证存在。

## 验证

- JSON 编辑后用 `python -m json.tool <file>` 验证语法。
- 新增声音：检查 `.ogg` 路径与 `sound_definitions.json` 条目匹配。
- 新增 Python 模块：检查 `modMain.py` 中的注册字符串。
- 新增方块/物品：逐项检查上面「方块乐器注册表」中的所有耦合路径。
- `.gitattributes` 强制 LF 换行；`.lang` 文件保持 UTF-8 中文。
