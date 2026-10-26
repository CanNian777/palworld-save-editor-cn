# 从源码构建

本文说明如何从干净的源码构建「幻兽帕鲁存档编辑器 1.0」，包括开发运行、前端构建和打包为 Windows 可执行文件。

本项目是独立的桌面存档编辑器，不注入游戏进程、不替换游戏文件，也不是游戏内 DLL 或脚本模组。程序在本地运行，只读写用户选择的存档目录。

## 源码结构

| 路径 | 内容 |
| --- | --- |
| `src/palworld_save_studio/` | Python 应用、Flask API、存档编辑服务、桌面入口、离线目录数据 |
| `src/palworld_save_studio/webui/` | 前端构建产物，由构建流程生成，不手工编辑 |
| `src/palworld_save_studio/ooz_compat.py` | Oodle 压缩兼容层（见下文「已知问题」） |
| `src/palworld_save_studio/avatar.ico` | 窗口图标，打包时注入 |
| `frontend/src/` | Vue 3 + TypeScript 界面、Pinia store、API 客户端、样式 |
| `frontend/pnpm-lock.yaml` | 前端依赖锁定文件 |
| `tests/` | Python 单元测试与存档往返测试 |
| `build_executable.ps1` | 完整构建脚本（前端 → 测试 → PyInstaller → 归档 → 校验和） |
| `requirements.txt` | Python 依赖 |
| `LICENSE` / `NOTICE` | GPL-3.0 许可证与来源声明 |

## 环境要求

- Windows 10 / 11 x64
- Python 3.11 或更高（推荐 3.12）
- Node.js 20 或更高，且 `corepack` 可用
- Git
- 安装依赖时需要联网
- **不需要** Palworld 本体、游戏存档或任何签名证书

在 PowerShell 中确认：

```powershell
git --version
python --version
node --version
corepack --version
```

前端通过 `package.json` 的 `packageManager` 字段固定在 **pnpm 9.15.9**，Corepack 会自动选用该版本。

## 快速构建

```powershell
git clone https://github.com/CanNian777/palworld-save-editor-cn.git
cd palworld-save-editor-cn
.\build_executable.ps1
```

脚本会依次完成：

1. `corepack pnpm install --frozen-lockfile` 安装前端依赖
2. 运行前端测试与 TypeScript 类型检查
3. `corepack pnpm build` 生成前端产物
4. 把 `frontend/dist` 复制到 `src/palworld_save_studio/webui/`
5. 新建 `venv` 并安装 Python 依赖
6. 运行 Python 测试
7. 用 PyInstaller 打包为单文件 exe
8. 生成分发 ZIP 与 SHA-256 校验和

产物位于 `dist/`：

```text
dist\PalworldSaveEditor.exe
dist\PalworldSaveEditor.exe.sha256
dist\PalworldSaveEditor-Windows-x64.zip
dist\PalworldSaveEditor-Windows-x64.zip.sha256
```

> **注意**：脚本第 5 步会从 Git 安装 `pyooz`，该包在部分环境下需要 C++ 编译工具链。如果这一步失败，请改用下面的手动流程。

## 手动构建

### 1. 后端依赖

```powershell
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
pip install loguru orjson
```

`pyooz` 若编译失败（`Failed building wheel for pyooz`），改用预编译 wheel：

```powershell
pip install path\to\pyooz-0.0.8-cp38-abi3-win_amd64.whl
pip install --no-deps palworld-save-tools
```

注意模块名是 `ooz`，不是 `pyooz`。

### 2. 前端

```powershell
cd frontend
corepack pnpm install
corepack pnpm build
```

把产物复制进 Python 包：

```powershell
Copy-Item 'dist\*' '..\src\palworld_save_studio\webui\' -Recurse -Force
```

### 3. 开发运行

```powershell
cd ..
python -m palworld_save_studio --mode gui --nocli
```

后端会监听 `127.0.0.1:58080`，桌面窗口由 pywebview 承载。

### 4. 打包 exe

```powershell
python -m PyInstaller --clean --noconfirm --onefile --windowed `
  --icon 'src\palworld_save_studio\avatar.ico' `
  --add-data 'src\palworld_save_studio\webui;webui' `
  --add-data 'src\palworld_save_studio\assets;assets' `
  --add-data 'src\palworld_save_studio\avatar.ico;.' `
  --hidden-import 'ooz' `
  --paths 'src' `
  --name 'PalworldSaveEditor' `
  'src\palworld_save_studio\__main__.py'
```

关键参数说明：

- `--windowed`：不显示控制台窗口
- `--add-data ... avatar.ico;.`：窗口图标通过 `ASSETS_PATH / "avatar.ico"` 读取，必须放进包内根目录
- `--hidden-import ooz`：`ooz` 是运行时动态导入的，PyInstaller 不会自动发现
- `--paths src`：项目使用 `src` 布局，不改用可编辑安装时需要显式指定

## 已知问题

### 保存时报 `module 'ooz' has no attribute 'compress'`

pip 上的 `pyooz` 只有 `decompress`，没有 `compress`，而保存需要重新压缩。本项目通过 `src/palworld_save_studio/ooz_compat.py` 在导入 `palworld_save_tools` 之前注册一个同名的 `ooz` 模块，用系统里的 `oo2core_*_win64.dll` 提供压缩：

- `decompress` → `OodleLZ_Decompress`
- `compress` → `OodleLZ_Compress`（Kraken + Normal）

**本项目不分发 Oodle 二进制**。请从本机已安装的其他 Unreal 引擎游戏取得该 DLL（Palworld 自身的 `Pal\Binaries\Win64\`、Delta Force、Fortnite 等），然后：

```powershell
$env:PALFORGE_OODLE = 'D:\path\to\oo2core_8_win64.dll'
```

未设置时程序会自动搜索常见游戏安装目录；找不到则打开存档仍可用，但保存会失败并给出提示。

### exe 打开存档报「解析失败」

中文 Windows 控制台默认 GBK，而 `palworld_save_tools` / `loguru` 会输出 `ℹ` 等符号，编码失败会被包装成存档解析错误。`__main__.py` 已在最开始把 `stdout` / `stderr` 重配置为 UTF-8 并对打包后为 `None` 的情况做了兜底，修改入口文件时不要把这些代码移到业务导入之后。

### 前端产物不生效

Flask 只服务 `src/palworld_save_studio/webui/`，不是 `frontend/dist/`。改完前端必须复制过去并重启后端。

## 验证

```powershell
.\dist\PalworldSaveEditor.exe --help
Get-FileHash .\dist\PalworldSaveEditor.exe -Algorithm SHA256
Get-Content .\dist\PalworldSaveEditor.exe.sha256
```

PyInstaller 不保证两次构建字节完全一致（打包元数据、绝对路径会影响结果），因此以源码、锁定依赖和测试作为可复现依据，而不是比对二进制哈希。

## 许可

本项目基于 [Palworld Save Studio](https://github.com/RayChen200318/palworld-save-studio) 修改，遵循 GPL-3.0，详见 [`LICENSE`](LICENSE) 与 [`NOTICE`](NOTICE)。

按 GPL-3.0 要求，分发可执行文件时必须同时提供完整源码，并保留原有版权声明。
