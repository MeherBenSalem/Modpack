# Remnants | The Modpack — Season 1: *The Long Eclipse*

NightBeam Studio's story-driven soulslike RPG modpack for **Minecraft 1.21.1 on NeoForge**. You wake in the ash of
a world whose sun was eaten; relight it one Ember Shrine and one Sovereign at a time. The story is in
[`design/STORY.md`](design/STORY.md).

> Work in progress: the mod list, quests and scripts are being built now.

## Layout

| Path | What it is |
|---|---|
| `design/` | Story bible, progression and mechanics design |
| `src/mods.json` | The curated mod list (source of truth): Modrinth and CurseForge ids, sides, reasons |
| `src/quests/` | Quests as readable YAML: chapters, groups, reward tables |
| `src/pack.json` | Pack name, version, Minecraft and NeoForge versions |
| `pack/` | The built pack in [packwiz](https://packwiz.infra.link/) format: `pack.toml`, `index.toml`, `mods/*.pw.toml`, `config/`, `kubejs/`, `defaultconfigs/` |
| `tools/build_pack.py` | Writes `pack/` from `src/mods.json`; `--export` builds the CurseForge zip, the Modrinth `.mrpack` and the server mod list in `dist/` |
| `tools/build_quests.py` | Compiles `src/quests/` into FTB Quests files under `pack/config/ftbquests/` |
| `tools/test_server.py` | Boots the pack on a real NeoForge dedicated server and reports errors |
| `tools/test_client.py` | Boots the real client headless (Xvfb); `--menu` screenshots the title screen |
| `art/` | Pack icon, logo, menu background and title card ([`art/README.md`](art/README.md)) |
| `tools/build_menu.py` | Writes the FancyMenu main menu (`pack/config/fancymenu/`) from `art/out/` |

## Build

```bash
python3 tools/build_quests.py --check   # quests -> pack/config/ftbquests
python3 tools/build_pack.py --export    # pack/ + dist/*.zip, dist/*.mrpack, dist/server-mods.tsv
python3 tools/test_server.py            # boot test on NeoForge (Java 21)
node art/render.cjs art/shots/ember_shrine_sunset.png && python3 tools/build_menu.py   # art + main menu
```

Needs Python 3.11+ with PyYAML, and Java 21 for the boot test.
