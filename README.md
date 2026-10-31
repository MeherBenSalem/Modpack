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
| `tools/build_pack.py` | Writes `pack/` from `src/mods.json`; `--export` builds the CurseForge zip, the Modrinth `.mrpack` and the self-contained server pack in `dist/` |
| `tools/build_quests.py` | Compiles `src/quests/` into FTB Quests files under `pack/config/ftbquests/` |
| `src/progression.yaml`, `tools/build_progression.py` | The Ember Forge: tiered alloys, seals and every recipe change (storage interlock, story locks), compiled to KubeJS and checked; `tools/dump_recipes.py` indexes the mods' recipes for it |
| `tools/server/` | The server pack's start scripts, JVM flags, `server.properties` and `SERVER.md` |
| `tools/test_server.py` | Unzips the built server pack, starts it with its own `start.sh` and reports errors and warnings |
| `tools/test_client.py` | Boots the real client headless (Xvfb); `--menu` screenshots the title screen, `--server host:port` joins a server |
| `art/` | Pack icon, logo, menu background and title card ([`art/README.md`](art/README.md)) |
| `tools/build_menu.py` | Writes the FancyMenu title screen and Drippy loading screen (`pack/config/fancymenu/`) from `art/out/` |
| `tools/build_threshold.py` | Writes the Threshold (the first-join starting area): dimension, build function, advancements, layout |
| `tools/build_voice.py` | Masters the Keeper's narration (`src/voice/`) into `kubejs/assets/remnants/sounds/vo/` |
| `tools/check_cf.py` | Checks every CurseForge project/file id against the live project before an export |

## Build

```bash
python3 tools/dump_recipes.py && python3 tools/build_progression.py   # the Ember Forge -> kubejs
python3 tools/build_quests.py --check   # quests -> pack/config/ftbquests
python3 tools/build_pack.py --export    # pack/ + dist/*-curseforge.zip, dist/*.mrpack, dist/*-server.zip
python3 tools/test_server.py            # boot the server pack (Java 21); --hold 900 keeps it up for a join
python3 tools/test_client.py --server localhost:25599 --curseforge --xmx 5G   # headless client joins it
node art/render.cjs art/shots/ember_shrine_sunset.png && python3 tools/build_menu.py   # art + main menu
python3 tools/build_threshold.py         # the starting area
python3 tools/build_voice.py --kokoro <model-dir>   # narration (recordings in src/voice/raw/ win)
python3 tools/check_cf.py                # before uploading: every CurseForge id is the right project
```

Needs Python 3.11+ with PyYAML, and Java 21 for the boot test.
