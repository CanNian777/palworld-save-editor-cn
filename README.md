# 幻兽帕鲁存档编辑器 1.0

一个离线的 Palworld（幻兽帕鲁）存档编辑器。直接读写存档文件，不需要启动游戏。

> **本项目是 [Palworld Save Studio](https://github.com/RayChen200318/palworld-save-studio) 的修改版**
> 原项目 © 2026 RayChen200318，GPL-3.0。
> 本项目在其基础上重做了界面、更名、并修复了保存时必然失败的 Oodle 压缩依赖缺陷。
> 完整差异见下方「与原版的差异」。

[English](README.en.md)

---

## 功能

- **帕鲁**：等级、昵称、星级、物种、IV、友好度、被动特性、主动技能
- **玩家**：昵称、等级、属性点、科技点、观赏笼权限
- **科技**：按等级浏览，逐项解锁 / 锁定，支持全部解锁
- **物品**：背包、关键物品、武器槽、装备槽，支持移动、复制、删除
- **对象浏览**：搜索与筛选，定位容器外 / 异常状态对象
- **安全写入**：修改先进内存草稿，保存前预览将写入的文件，写入前自动备份

支持单机存档与专用服务器（`World` 目录）两种模式。

---

## 与原版的差异

**界面**

- 重写启动页：液态玻璃材质、双栏布局、能力说明
- 统一全局视觉：配色、圆角、边框、字号收敛到一套 design token
- 重写仪表盘：统计条 + 快捷入口 + 对象表格
- 帕鲁列表改为虚拟滚动行式列表（保留网格模式）
- 重写模态框、设置面板、侧栏与顶栏

**功能**

- 版本号改为 1.0 正式版
- 全站中文品牌名，英文界面自动切换
- 后端错误信息中文化（22 条固定文案 + 6 条模式匹配）
- 新增 Oodle 压缩兼容层，修复保存时报 `AttributeError: module 'ooz' has no attribute 'compress'`
- 新增点击波纹、hover 上浮、页面原生过渡等交互反馈
- 设置页新增反馈邮箱

**未改动**

- 存档解析、GVAS 序列化、事务写入、备份策略等核心逻辑
- 原有的数据模型与 API 结构

---

## 环境要求

- Windows 10 / 11
- Python 3.11+
- Node.js 20+（仅构建前端时需要）
- 一个 `oo2core_*_win64.dll`（Oodle 运行时，见下方说明）

---

## 安装

```bash
git clone <this-repo>
cd <repo>

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### 关于 Oodle 运行时

保存存档需要重新压缩，依赖 Unreal 的 Oodle 库。**本项目不分发该二进制文件。**

请从本机已安装的其他 Unreal 引擎游戏中取得 `oo2core_*_win64.dll`（例如 Palworld 自身的 `Pal\Binaries\Win64\`、Delta Force、Fortnite 等），然后任选一种方式：

1. 设置环境变量指向它：

```bat
set PALFORGE_OODLE=D:\path\to\oo2core_8_win64.dll
```

2. 或者让程序自动搜索常见游戏安装路径。

未找到该文件时，打开存档仍可用，但保存会失败并给出明确提示。

---

## 运行

```bat
python -m palworld_save_studio --mode gui --nocli
```

启动后选择存档文件夹（需要包含 `Level.sav` 与 `Players` 子目录），或点击「检测 Steam 存档」自动定位。

| 参数 | 说明 |
|---|---|
| `--mode gui` | 以桌面窗口运行（默认） |
| `--mode web` | 只启动后端，用浏览器访问 |
| `--path` | 直接指定存档路径 |
| `--nocli` | 不启动命令行交互 |

---

## 构建前端

本项目使用 pnpm（版本固定在 `package.json` 的 `packageManager` 字段）：

```bash
cd frontend
corepack pnpm install
corepack pnpm build
```

如果你已经全局安装 pnpm，直接 `pnpm install && pnpm build` 也可以。

构建产物输出到 `frontend/dist`，需要复制到 `src/palworld_save_studio/webui/` 才能被后端加载。

---

## 打包为 exe

```powershell
.\build_executable.ps1
```

完整的构建流程、手动分步命令和常见问题（pyooz 编译失败、Oodle 运行时、GBK 编码）见 [SOURCE_BUILD_GUIDE.md](SOURCE_BUILD_GUIDE.md)。

---

## 已知限制

- 保存后如果游戏内数值异常，请用备份回滚（备份位于存档目录旁的 `Palworld-Save-Studio-Backup/`）
- 专用服务器写入前必须完全停止 PalServer，程序只能校验文件是否变化，无法判断进程是否占用
- 存档格式随游戏版本变化，Palworld 大版本更新后可能失效

---

## 许可

GNU General Public License v3.0，见 [LICENSE](LICENSE)。

本项目包含来自以下项目的代码与数据，原始版权归各自作者所有，详见 [NOTICE](NOTICE)：

- [Palworld Save Studio](https://github.com/RayChen200318/palworld-save-studio) — 本项目的直接来源
- [KrisCris/Palworld-Pal-Editor](https://github.com/KrisCris/Palworld-Pal-Editor)
- [RayChen200318/Palworld-Pal-Editor-1.0](https://github.com/RayChen200318/Palworld-Pal-Editor-1.0)
- [oMaN-Rod/palworld-save-pal](https://github.com/oMaN-Rod/palworld-save-pal)

依据 GPLv3，任何人分发本软件时必须同时提供完整源码，并保留上述版权声明。

---

## 免责声明

非官方粉丝工具，与 Pocketpair, Inc. 无任何关联。使用本工具修改存档可能造成数据损坏或存档失效，请自行备份并承担风险。

---

## 反馈

cannian984@gmail.com
