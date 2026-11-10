# Remnants | The Modpack — Season 1: *The Long Eclipse*

NightBeam Studio's story-driven soulslike RPG modpack for **Minecraft 1.21.1 on NeoForge**. You wake in the ash of
a world whose sun was eaten; relight it one Ember Shrine and one Sovereign at a time. The story is in
[`design/STORY.md`](design/STORY.md).

> Work in progress: the mod list, quests and scripts are being built now.

## Layout

| Path | What it is |
|---|---|
| `design/` | Story bible, progression and mechanics design; [`design/PROGRESSION_GRAPH.md`](design/PROGRESSION_GRAPH.md) is the dependency graph of the whole pack |
| `src/mods.json` | The curated mod list (source of truth): Modrinth and CurseForge ids, sides, reasons |
| `src/quests/` | Quests as readable YAML: chapters, groups, reward tables |
| `src/pack.json` | Pack name, version, Minecraft and NeoForge versions |
| `pack/` | The built pack in [packwiz](https://packwiz.infra.link/) format: `pack.toml`, `index.toml`, `mods/*.pw.toml`, `config/`, `kubejs/`, `defaultconfigs/` |
| `tools/build_pack.py` | Writes `pack/` from `src/mods.json`; `--export` builds the CurseForge zip, the Modrinth `.mrpack` and the self-contained server pack in `dist/` |
| `tools/build_quests.py` | Compiles `src/quests/` into the Core RPG - Quests Engine book under `pack/config/corerpg_quests/book/` |
| `tools/dump_advancement_titles.py` | Indexes every advancement title from the mods' jars (`research/registry/advancement_titles.json`) so untitled advancement tasks show the advancement's name |
| `src/stat_locks.yaml`, `tools/build_stat_locks.py` | RPG Stats gates: gear on attributes, ore level gates, level-up rewards (`config/ras/`) |
| `tools/update_mods.py` | Moves every mod to its newest 1.21.1 NeoForge file on Modrinth and CurseForge (`--write`) |
| `src/progression.yaml`, `tools/build_progression.py` | The Ember Forge: tiered alloys, seals and every recipe change (storage interlock, story locks), compiled to KubeJS and checked; `tools/dump_recipes.py` indexes the mods' recipes for it |
| `tools/server/` | The server pack's start scripts, JVM flags, `server.properties` and `SERVER.md` |
| `tools/test_server.py` | Unzips the built server pack, starts it with its own `start.sh` and reports errors and warnings |
| `tools/test_client.py` | Boots the real client headless (Xvfb); `--menu` screenshots the title screen, `--server host:port` joins a server |
| `art/` | Pack icon, logo, menu background and title card ([`art/README.md`](art/README.md)) |
| `tools/build_menu.py` | Writes the FancyMenu title screen and Drippy loading screen (`pack/config/fancymenu/`) from `art/out/` |
| `pack/kubejs/client_scripts/remnants/community.js` | Adds the NightBeam Community Server to the Multiplayer list once per install and the "Need a server?" sponsor button (`design/LAUNCH.md`) |
| `tools/build_threshold.py` | Writes the Threshold (the first-join starting area): dimension, build function, advancements, layout |
| `tools/build_voice.py` | Masters the Keeper's narration (`src/voice/`) into `kubejs/assets/remnants/sounds/vo/` |
| `tools/check_cf.py` | Checks every CurseForge project/file id against the live project before an export |
| `tools/dump_live.py` | Boots the server pack once with a dev-only script and records what the game really registers (ids, tags, every recipe after KubeJS, loot tables) in `research/registry/live/` |
| `tools/validate_pack.py`, `src/validation.yaml` | Checks the quests, the Ember Forge and the progression graph against that record: book in sync, no cycles, every id real, every asked-for item obtainable and available by its act, every gate craftable in time, the Fragment budget. `--why <item>` explains how an item is obtained |
| `tools/publish_cf.py`, `tools/publish_mr.py` | Upload a release to CurseForge (modpack zip + server pack) and Modrinth (`.mrpack`); run by the "Publish to CurseForge" and "Publish to Modrinth" workflows |

## Build

```bash
python3 tools/dump_recipes.py && python3 tools/build_progression.py   # the Ember Forge -> kubejs
python3 tools/build_quests.py --check   # quests -> pack/config/corerpg_quests/book
python3 tools/validate_pack.py          # the whole graph against the game's real recipes (after a mod update: tools/dump_live.py first)
python3 tools/build_pack.py --export    # pack/ + dist/*-curseforge.zip, dist/*.mrpack, dist/*-server.zip
python3 tools/test_server.py            # boot the server pack (Java 21); --hold 900 keeps it up for a join
python3 tools/test_client.py --server localhost:25599 --curseforge --xmx 5G   # headless client joins it
node art/render.cjs art/shots/ember_shrine_sunset.png && python3 tools/build_menu.py   # art + main menu
python3 tools/build_threshold.py         # the starting area
python3 tools/build_voice.py --kokoro <model-dir>   # narration (recordings in src/voice/raw/ win)
python3 tools/check_cf.py                # before uploading: every CurseForge id is the right project
```

Needs Python 3.11+ with PyYAML, and Java 21 for the boot test.
