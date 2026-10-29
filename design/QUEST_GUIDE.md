# Writing quests for Remnants S1

Quests are YAML in `src/quests/chapters/*.yaml`, compiled by `tools/build_quests.py` into FTB Quests 2101 files. The
format is documented at the top of `tools/build_quests.py`; `src/quests/chapters/s1_01_embers.yaml` is the reference
chapter. Read `design/STORY.md` first: every quest serves the story or teaches a system.

## Rules

1. **Valid ids only.** Every modded item, entity, structure, dimension and advancement must exist in
   `research/registry/` (`<ns>_en_us.json` lang dumps, `<ns>_ids.json` advancement/structure/dimension/loot ids).
   Run `python3 tools/build_quests.py --check --out <scratch dir>` and fix every `UNKNOWN` line. Vanilla ids
   (`minecraft:`) are not checked, so double-check them for 1.21.1.
2. **Detect, don't trust.** Prefer `advancement`, `kill`, `structure`, `dimension` and `item` tasks. Use `checkmark`
   only for things the game can't detect (reading, choosing, hiring a sellsword).
   - Runeborn's Sovereigns and Much More Dungeons' guardians are renamed vanilla mobs: use their advancements
     (`runeborn:feats/fell_*`, `muchmoredungeons:slay_*_guardian`), never a kill task.
   - Item tags: `{tag: minecraft:logs, count: 16}`.
3. **One idea per quest**, 2–6 lines of description. Second person. Dark-fantasy tone, short sentences, a little dry
   humour. The Keeper's lines are in `&o"…"&r`. Use the mods' own names (runes, Ember Shrine, Valor, Remnant,
   Sovereign, Hunter's Moon) so players can look them up.
4. **Wording:** fights are "soulslike"; never name another game, studio or franchise.
5. **Colour codes:** `&6` gold for key terms, `&c` danger, `&a` safe, `&b` FP/magic, `&7` asides, `&e` keys,
   `&o` italic, `&r` reset.
6. **Rewards** are modest and on-theme: XP, the pack's reward tables, Runeborn consumables (runes, tempering stones),
   Remnant Shards, food. No netherite before Act IV, no Tome of Ascension before Act II. Boss quests can use
   `{table: sovereign_tribute}`. Put new tables in `src/quests/reward_tables/<your_chapter>.yaml` (unique keys,
   prefix them with your chapter name).
7. **Layout:** leave out `pos` and the compiler lays quests out by dependency depth; add `pos` only to fix a messy
   chapter. Use `shape: gear` / `size: 2.0` for bosses, `hexagon` for milestones.
8. **Dependencies** across chapters: `chapter_key/quest_key` (e.g. `s1_act1_embers/kindle`). Side chapters should
   start from a main-story quest so they unlock at the right time.
9. **Keys:** the pack's default keys are R weapon art, I status/codex, Left Alt dodge, K level up, G command wheel,
   U roster, M map, N minimap, B marker, P skill tree, Z/X/C/V ability casts, Y Archive codex, H/O/` memories, J
   Archive objectives.
10. **Chapter keys** never change once released: quest ids are derived from `chapter` + `key`.

## Main-story anchors side chapters can depend on

| Quest | Meaning |
|---|---|
| `s1_prologue/rise` | the very start |
| `s1_prologue/village` | found a village (end of the Prologue) |
| `s1_act1_embers/kindle` | first Ember Shrine (Act I core) |
| `s1_act1_embers/sellsword` | hired a sellsword |
| `s1_act1_embers/dusk_rider` | first Sovereign down (end of Act I) |
| `s1_act2_hunt/hunters_moon` | first Hunter's Moon (Act II) |
| `s1_act2_hunt/sylvara` | end of Act II |
| `s1_act3_deep/ysolde` | end of Act III |
| `s1_act4_ash/vaelorn` | end of Act IV |
| `s1_act5_realm/enter` | entered the Eclipsed Realm |
| `s1_act5_realm/hollow_sovereign` | the finale |
