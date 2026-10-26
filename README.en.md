# Palworld Save Editor 1.0

An offline save editor for Palworld. Reads and writes save files directly — the game does not need to be running.

> **This project is a modified version of [Palworld Save Studio](https://github.com/RayChen200318/palworld-save-studio).**
> Original work © 2026 RayChen200318, GPL-3.0.
> This fork redesigns the interface, renames the product, and fixes an Oodle-compression dependency bug that made every save attempt fail.
> See "Differences from upstream" below for the full list.

---

## Features

- **Pals** — level, nickname, rank, species, IVs, friendship, passive traits, active skills
- **Players** — nickname, level, stat points, technology points, display-cage permission
- **Technology** — browse by level, toggle individual entries, unlock all
- **Items** — inventory, key items, weapon slots, equipment slots; move, duplicate, delete
- **Object browser** — search and filter, including objects outside containers and anomalous entries
- **Safe writes** — edits stay in an in-memory draft; preview affected files before committing; automatic backup

Supports both local saves and dedicated-server `World` directories.

---

## Differences from upstream

**Interface**
- Rebuilt the launch screen with a liquid-glass treatment and two-column layout
- Unified global design tokens: color, radius, border, type scale
- Rebuilt the dashboard around a stat strip, quick-action list, and object table
- Pal list switched to a virtualized row layout (grid mode retained)
- Rebuilt modals, settings panel, sidebar and top bar

**Functionality**
- Version bumped to 1.0
- Full Chinese branding with automatic English switching
- Backend error messages localized to Chinese (22 fixed strings + 6 patterns)
- Added an Oodle compatibility layer fixing `AttributeError: module 'ooz' has no attribute 'compress'`
- Added click ripple, hover lift, and native page transitions
- Added a feedback address to the settings panel

**Untouched**
- Save parsing, GVAS serialization, transactional writes, backup strategy
- Existing data model and API surface

---

## Requirements

- Windows 10 / 11
- Python 3.11+
- Node.js 20+ (frontend build only)
- An `oo2core_*_win64.dll` (Oodle runtime — see below)

---

## Install

```bash
git clone <this-repo>
cd <repo>

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### About the Oodle runtime

Re-compressing a save requires Unreal's Oodle library. **This project does not redistribute that binary.**

Obtain `oo2core_*_win64.dll` from another Unreal Engine game already installed on your machine (Palworld's own `Pal\Binaries\Win64\`, Delta Force, Fortnite, …), then either:

1. Point an environment variable at it:

```bat
set PALFORGE_OODLE=D:\path\to\oo2core_8_win64.dll
```

2. Or let the app scan common game install locations automatically.

Without it, opening saves still works, but saving will fail with an explicit message.

---

## Run

```bat
python -m palworld_save_studio --mode gui --nocli
```

Pick a save folder (must contain `Level.sav` and a `Players` directory), or use "Detect Steam save".

| Flag | Meaning |
|---|---|
| `--mode gui` | Desktop window (default) |
| `--mode web` | Backend only, open in a browser |
| `--path` | Point directly at a save folder |
| `--nocli` | Skip the interactive CLI |

---

## Build the frontend

This project uses pnpm (pinned via the `packageManager` field in `package.json`):

```bash
cd frontend
corepack pnpm install
corepack pnpm build
```

If pnpm is already installed globally, `pnpm install && pnpm build` works too.

Output goes to `frontend/dist`; copy it into `src/palworld_save_studio/webui/` for the backend to serve.

---

## Package as exe

The repository ships `build_executable.ps1`:

```powershell
.\build_executable.ps1
```

See [SOURCE_BUILD_GUIDE.md](SOURCE_BUILD_GUIDE.md) for the full pipeline, manual step-by-step commands, and troubleshooting.

---

## Known limitations

- If in-game values look wrong after saving, roll back from the backup in `Palworld-Save-Studio-Backup/`
- For dedicated servers, PalServer must be fully stopped first; the app can only detect file changes, not process locks
- Save format changes with game updates; a major Palworld release may break compatibility

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).

This project contains code and data from the following projects, each retaining its own copyright (see [NOTICE](NOTICE)):

- [Palworld Save Studio](https://github.com/RayChen200318/palworld-save-studio) — direct upstream
- [KrisCris/Palworld-Pal-Editor](https://github.com/KrisCris/Palworld-Pal-Editor)
- [RayChen200318/Palworld-Pal-Editor-1.0](https://github.com/RayChen200318/Palworld-Pal-Editor-1.0)
- [oMaN-Rod/palworld-save-pal](https://github.com/oMaN-Rod/palworld-save-pal)

Under GPLv3, anyone distributing this software must also make the complete source available and preserve these notices.

---

## Disclaimer

Unofficial fan tool, not affiliated with Pocketpair, Inc. Modifying saves may corrupt data. Back up your saves and use at your own risk.

---

## Feedback

cannian984@gmail.com
