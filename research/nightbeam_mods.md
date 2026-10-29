# NightBeam Studio mods: audit for "Remnants | The Modpack, Season 1"

Target: **Minecraft 1.21.1 + NeoForge**. Data collected **2026-10-29**.

Sources:
- Modrinth API: `/v2/user/NAIZO/projects`, `/v2/project/{slug}` (body) and `/v2/project/{slug}/version?loaders=["neoforge"]&game_versions=["1.21.1"]`.
- cfwidget: `api.cfwidget.com/author/111805548` and `api.cfwidget.com/{projectId}`.
- The jars themselves, downloaded and verified against Modrinth sha1, sha512 and size. Ballistics was checked against CurseForge's file size. All jars were read as data with Python `zipfile`; nothing was executed.

The linked GitBook docs (`docs-nightbeam.gitbook.io/rpg-mob-leveling`, `nightbeam.gitbook.io/rpg-attribute-system`) are stale: they document RPG Mob Leveling 2.0.1 and RAS 2.x, not the current 3.0 / 5.0 rewrites. `docs.nightbeam.dev/remnants` is a JavaScript-only codex. The Modrinth bodies and the jars are used as ground truth here.

Machine-readable companion: `modpack/research/nightbeam_mods.json`. Lang files: `modpack/research/registry/<modid>_en_us.json`.

## 0. Scope

All 24 NightBeam **Minecraft mods** are covered:
- 23 on Modrinth under user `NAIZO`.
- Remnants | Ballistics, which is CurseForge-only.

Out of scope:
- Paper/Bukkit plugins: Donut Auction, Mail, Orders, RTP & RTP Zone, Shards, Team, Essentials, Leaderboard, and LPCF.
- Hytale mods: HyCommands and HyUltimine.

Several CurseForge entries still carry old names in the cfwidget author record. All were re-resolved by project id:

| Old name in cfwidget | Current mod |
|---|---|
| MOTP - RPG leveling system | RPG Stats |
| RPG Mob Leveling System | RPG Mobs |
| Remnant Bosses | The Eclipsed Realm |
| The Elemental - RPG | Skills and Powers |
| Better With Gold | Fellowship |
| Odyssey Map | Remnants Minimap |
| Robotica | Chronofall |
| The Fisherman House | Fisherman's Coast |
| **The Birth of Steve** (1621994) | **Remnants: Roguelite Dungeons** (same mod id `tbos`; *The Birth of Steve* is now its prologue) |

Every Modrinth mod has a NeoForge 1.21.1 release. For each, the CurseForge 1.21.1 NeoForge file has the same file name and byte size as the Modrinth file.

| # | Mod | Mod id | Version (1.21.1 NeoForge) | Side | Required deps | Decision |
|---|---|---|---|---|---|---|
| 1 | Jauml | `jauml` | `3.0.0+neoforge-1.21.1` | both | - | **include** |
| 2 | Remnants \| RPG Stats, Skills & Progression | `rpg_attribute_system` | `5.0.1+neoforge-1.21.1` | both | jauml | **include** |
| 3 | Runeborn \| Soulslike RPG progression | `runeborn` | `3.0.0+neoforge-1.21.1` | both | - | **include** |
| 4 | Remnants \| RPG Mobs | `remnant_mobs` | `3.0.0` | both | - | **include** |
| 5 | Remnants \| The Eclipsed Realm | `remnant_bosses` | `3.1.0+neoforge-1.21.1` | both | geckolib, jauml | **include** |
| 6 | Remnants: Roguelite Dungeons | `tbos` | `1.0.0+mc1.21.1+neoforge` | both | - | **include** |
| 7 | Remnants \| Skills and Powers | `elementals` | `2.0.1+neoforge-1.21.1` | both | - | **optional** |
| 8 | Remnants \| Fellowship | `better_with_gold` | `2.0.0+neoforge-1.21.1` | both | - | **include** |
| 9 | Mob LootBags | `mob_loot_bags` | `2.0.0+neoforge-1.21.1` | both | - | **optional** |
| 10 | Much More Dungeons | `muchmoredungeons` | `2.0.0+neoforge-1.21.1` | both | - | **include** |
| 11 | Fisherman's Coast | `fisherman_house` | `2.0.0+neoforge-1.21.1` | both | - | **include** |
| 12 | Remnants \| Advanced Minimap & Waypoints | `remnantminimaps` | `2.0.0+neoforge-1.21.1` | client | - | **include** |
| 13 | Smart Villagers AI | `smartvillagers` | `2.0.0+neoforge-1.21.1` | server | - | **optional** |
| 14 | RE:Constructed Wands | `reconstructedwands` | `2.0.0+neoforge-1.21.1` | both | - | **optional** |
| 15 | Better Farming ++ | `better_farming_plus` | `1.0.0+neoforge-1.21.1` | both | - | **optional** |
| 16 | Sprout & Soil | `sprout_and_soil` | `0.3.0+neoforge-1.21.1` | both | - | **exclude** |
| 17 | The Witch Hut | `better_witch_huts` | `1.0.0` | both | jauml | **optional** |
| 18 | The Gingerbread House | `christmas_ginger_house` | `1.0.0` | both | jauml | **exclude** |
| 19 | Genetically Modified Monsters | `gmm` | `1.0.0+neoforge-1.21.1` | both | - | **exclude** |
| 20 | Chronofall | `chronofall` | `2.0.0+neoforge-1.21.1` | both | - | **exclude** |
| 21 | Remnants \| Ballistics | `remnants_ballistics` | `remnants_ballistics-neoforge-1.21.1-0.4.0.jar (CF beta)` | both | - | **exclude** |
| 22 | Core Utilities | `core_utilities` | `2.0.0+1.21.1-neoforge` | both | - | **exclude** |
| 23 | Simple Terminals | `simple_terminals` | `1.1.1+neoforge-1.21.1` | both | - | **optional** |
| 24 | No More 63 AE2 | `no_more_63_ae2` | `0.1.3+neoforge-1.21.1` | both | ae2 | **exclude** |

**Pack baseline these mods impose:**
- NeoForge **21.1.229+**: RAS and Minimap require it. Ballistics would need 21.1.264+.
- **GeckoLib 4.8.4+**: required by The Eclipsed Realm.
- **jauml 3.0.0**: one jar satisfies every `jauml` range declared (`*`, `[1.1.0,)` and `[1.2.0,)`).
- Pin exact versions. Most of these mods had a full 2.0/3.0/5.0 rewrite in the last 10 days:
  - RAS 5.0.1: 10-27
  - Skills and Powers 2.0.1: 10-27
  - Fellowship 2.0.0: 10-28
  - Roguelite Dungeons 1.0.0: **published 10-29, today**

## 1. Critical findings (read before writing quests or configs)

1. **The Eclipsed Realm uses two namespaces.** Entities are `remnants:*` (e.g. `remnants:hollow_sovereign`). Items, blocks, biomes, the dimension and structures are `remnant_bosses:*`.
   - The lang file still contains retired keys from older versions: `bosses:*`, `remnant_ossukage:*`, `entity.remnant_bosses.hollow_sovereign`, and the item keys `archivist`, `regalia` and `warden`, which are armor-material names. **Do not use those.**
   - The jar's `RegistryAliases` class migrates retired ids such as `armored_grub`, `sickleghast` and `kotsukage` to current ones.
2. **Runeborn's seven Sovereigns are not custom entities.** Each is a vanilla mob with a name and boosted stats:

   | Sovereign | Base mob |
   |---|---|
   | Varghast | `minecraft:vindicator` |
   | Sylvara | `minecraft:stray` |
   | Kaelthar | `minecraft:evoker` |
   | Ysolde | `minecraft:wither_skeleton` |
   | Morgrath | `minecraft:piglin_brute` |
   | Vaelorn | `minecraft:ravager` |
   | Dusk Rider | `minecraft:skeleton` riding `minecraft:skeleton_horse` |

   Their summoned "Hollows" are named zombies. Quest "slay X" tasks must use the advancements `runeborn:feats/fell_<name>`, not an entity id.
3. **Much More Dungeons guardians are also named vanilla mobs.** Use `muchmoredungeons:slay_<structure>_guardian` advancements.
   - Its structure ids do not match its display names. For example `muchmoredungeons:dungeon_t2` is the **Cursed Keep, which is tier III**, and `tower_dungeon` is the Arcane Spire. The full mapping is in §2.10.
4. **The RAS Scroll of Rebirth recipe probably does not load on 1.21.1.** It ships as `data/rpg_attribute_system/recipes/tome_of_rebirth_recipe.json`: the pre-1.21 plural folder, with the old `"item"` result key. Treat `rpg_attribute_system:scroll_of_rebirth` as obtainable only via `/give`, rewards or `/ras respec`, or add a recipe by datapack/KubeJS. Verify in game.
5. **Sprout & Soil 0.3.0 is broken on 1.21.1.**
   - All block loot tables and its only recipe are in the pre-1.21 folders `loot_tables/` and `recipes/`, which are ignored.
   - The crop stages are plain `Block`s, not `CropBlock`s.
6. **The Witch Hut and The Gingerbread House hard-require jauml** (`[1.1.0,)` in `neoforge.mods.toml`), although Modrinth lists no dependency.
   - Neither contains the content its page advertises. There are no trader witches, no random loot and no secret rooms: each is one static vanilla-block template with fixed chest contents and **no loot tables**.
7. **No More 63 AE2 hard-requires AE2** `[19.2.17,20.0.0)` (not declared on Modrinth).
8. **Remnants Minimap is client-only** (`displayTest = IGNORE_ALL_VERSION`, deps `side = CLIENT`), although Modrinth marks it required on both sides.
   - **Smart Villagers AI** registers no network payloads and works installed only on the server. Clients are optional.
9. **Genetically Modified Monsters' 7 spawn eggs have no item model** in the jar, so they will show the missing-texture icon. Don't use them as quest icons.
10. **Remnants: Roguelite Dungeons is All-Rights-Reserved.** Reference it from Modrinth or CurseForge in the pack manifest; never re-host the jar in overrides. Every other mod here is Apache-2.0 (No More 63 AE2 is LGPL-3.0).
11. **Remnants | Ballistics** is CurseForge-only, a **beta** (`0.4.0`, file `9296773`) and needs NeoForge 21.1.264+. CurseForge publishes no hash, so the sha1 above was computed locally from the CDN download.
12. **Default keybinds collide heavily** across the Remnants mods. See §4.
13. **Two mods level mobs.** Runeborn levels mobs and spawns affixed champions (server option `mobLevelsEnabled`, `eliteChance`), and so does RPG Mobs. With both on, the same mob is scaled twice.
    - Set Runeborn `mobLevelsEnabled: false` and let RPG Mobs own mob scaling.
    - Keep Runeborn `eliteChance > 0`: its champions are the only source of `runeborn:sovereign_fragment`. Verify in game that champions still roll with levels off.
14. **Mob LootBags' boss rule misses the Realm bosses.** It covers `#c:bosses` + vanilla bosses, and The Eclipsed Realm does not tag its bosses `#c:bosses`. Add `remnants:hollow_sovereign`, `remnants:gravebound_warden`, `remnants:forgotten_watcher` and `remnants:ossukage` to `#mob_loot_bags:bosses` (or `#c:bosses`) if you want boss bags from them.
    - RPG Mobs already lists all five Realm bosses, including `burial_guardian`, in `#remnant_mobs:bosses`.

---

## 2. Per-mod audit

### 2.1 Jauml (library): include

- **Modrinth** (NeoForge 1.21.1, newest release): `3.0.0+neoforge-1.21.1` · version id `ckXjNUBa` · `jauml-neoforge-1.21.1-3.0.0.jar` · 96,107 bytes · published 2026-10-23
  - url: https://cdn.modrinth.com/data/ihvBalM2/versions/ckXjNUBa/jauml-neoforge-1.21.1-3.0.0.jar
  - sha1 `386c13eda9a471f456d1ef0d6bf4bd46993d2659`
  - sha512 `b56c166f00ffdf5fc1e1a639834e696e7295d429feffd0d180b66a2bf94df8e5bc84b8b2982bc4239fc76351aebad64ab8a12b2af88a5f485137eb10c1154da4`
- **CurseForge:** project `1281310` (slug `jauml`) · newest 1.21.1 NeoForge file `9298019` `jauml-neoforge-1.21.1-3.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1,). Licence Apache-2.0. Side: **both**.

**What it does:** NightBeam's shared library for typed, commented JSON configs (`JaumlConfig.bind`), server/player events, a tick scheduler, cooldowns, version-range helpers and a platform API. It adds no blocks, items or GUIs, and its jar has no assets or data.

**Fit:** mandatory. RAS (`*`), The Eclipsed Realm (`[1.2.0,)`), The Witch Hut and The Gingerbread House (`[1.1.0,)`) declare it. Runeborn, Better Farming++, Fisherman's Coast, Chronofall, GMM and Sprout & Soil needed it in older builds but **not** in the current 1.21.1 jars.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `jauml`
- Items (0): _none_
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Config files: `none of its own (each dependent mod writes config/<mod>/...)`

### 2.2 Remnants | RPG Stats, Skills & Progression (RPG Attribute System, "RAS"): include

- **Modrinth** (NeoForge 1.21.1, newest release): `5.0.1+neoforge-1.21.1` · version id `TERvkZUV` · `rpg_attribute_system-neoforge-1.21.1-5.0.1.jar` · 3,677,526 bytes · published 2026-10-27
  - url: https://cdn.modrinth.com/data/d85UTOuq/versions/TERvkZUV/rpg_attribute_system-neoforge-1.21.1-5.0.1.jar
  - sha1 `3373049fd9822da8b5244738d5c45ad7f46498ab`
  - sha512 `14b15fc5f0d46daaa8bca1728e38649fbb8387d130aa2c76b77946881991fa9e2f35d83aeb62b9957e14e27e45636badda8647295530d7047a9053f2f7a446c2`
- **CurseForge:** project `1079687` (slug `remnants-rpg-stats-skills-progression`) · newest 1.21.1 NeoForge file `9343361` `rpg_attribute_system-neoforge-1.21.1-5.0.1.jar` (release)
- **Dependencies:** required `jauml`; optional _none_. Modrinth lists: jauml (required). `neoforge.mods.toml` declares: jauml required *. NeoForge [21.1.229,). Licence Apache-2.0. Side: **both**.

**What it does (5.0 "The Ascendant Update"):** soulslike player leveling.

- Kills give **Valor Points (VP)**. VP is based on the mob's max health, with per-dimension multipliers, per-mob/tag rules and difficulty/armor weighting. VP fills an XP curve, and each level gives attribute points.
- Press **K** for the Level Up screen. Stage points with ←/→ (Shift = 5), preview **current → after** for every stat, then Enter to confirm. Confirmation is atomic and server-validated.
- The Status and Records pages switch with Tab. Level-ups show a gold banner, and a HUD shows level, XP and unspent points. All visuals are configurable in `config/ras/display/ui.json` (`font`, `hud_style`, `animations`).
- **Eight default attributes**, up to 15 supported. Each maps onto a vanilla attribute with a base value, per-point gain, cap, lock, icon and commands. The display names below were read from the jar's strings:

  | Attribute | Vanilla attribute | Per point |
  |---|---|---|
  | Vitality | max_health | +1.0 |
  | Attack Power | attack_damage | +0.20 |
  | Attack Speed | attack_speed | +0.02 |
  | Protection | armor | +0.25 |
  | Toughness | armor_toughness | +0.10 |
  | Agility | movement_speed | +0.0025 |
  | Fortitude | knockback_resistance | +0.01 |
  | Exploration | luck | +0.1 |

  The cap defaults to 500 points each.
- Other systems:
  - Respec via `/ras respec` or the **Scroll of Rebirth**, with optional costs and cooldowns.
  - Build templates: `/ras template apply warrior`.
  - Item and block locks by attribute or RPG level ("Requires RPG level %s").
  - Level-up rewards: items, effects or commands.
  - The **Tome of Ascension** grants levels.
  - Shared XP for nearby players, a public API, and a local web "configuration studio".
- Registered attributes `rpg_attribute_system:attribute_1` … `attribute_10` and `rpg_attribute_system:rpg_level` are the stored per-player values.

**Fit:** the spine of the Remnants family. The links are:
- RPG Mobs levels mobs to nearby RAS levels and pays bonus Valor.
- Runeborn shrine level-ups require RAS and grant RAS levels.
- Skills and Powers takes skill points from RAS levels.
- Fellowship caps ally level at your RAS level.
- Roguelite Dungeons pays Valor equal to ¼ of banked Renown.

**Overlaps:** Runeborn has its own 8-attribute system (see §3). Two RPG level sources exist: VP from kills, and Runeborn rune levels via `rpgLevelsPerRuneLevel`. Decide which one drives RAS levels (§5).

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `rpg_attribute_system`
- Items (2): `rpg_attribute_system:scroll_of_rebirth`, `rpg_attribute_system:tome_of_ascension`
- Blocks (0): _none_
- Entities (0): _none_
- Attributes: `rpg_attribute_system:attribute_1`, `rpg_attribute_system:attribute_10`, `rpg_attribute_system:attribute_2`, `rpg_attribute_system:attribute_3`, `rpg_attribute_system:attribute_4`, `rpg_attribute_system:attribute_5`, `rpg_attribute_system:attribute_6`, `rpg_attribute_system:attribute_7`, `rpg_attribute_system:attribute_8`, `rpg_attribute_system:attribute_9`, `rpg_attribute_system:rpg_level`
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Keybinds (default; b = read from bytecode, p = mod page): `key.rpg_attribute_system.open_stats_menu_keybind` Open Stats Menu = **K (b)**
- Config files: `config/ras/settings.json`, `config/ras/attributes/attribute_<N>.json`, `config/ras/display/ui.json`, `mob_xp.json, respec.json, templates.json (names from jar strings; same ras config tree)`
- Lang copy: `modpack/research/registry/rpg_attribute_system_en_us.json`

### 2.3 Runeborn | Soulslike RPG progression: include

- **Modrinth** (NeoForge 1.21.1, newest release): `3.0.0+neoforge-1.21.1` · version id `9IohPC6P` · `runeborn-neoforge-1.21.1-3.0.0.jar` · 715,691 bytes · published 2026-10-23
  - url: https://cdn.modrinth.com/data/ENwBoUVH/versions/9IohPC6P/runeborn-neoforge-1.21.1-3.0.0.jar
  - sha1 `48ee9fbfe05240343253e33f764c53ba70b30c9f`
  - sha512 `3739e40d20ff09ec7a1706224d804b5d73b37354dba413fb4836409b16f0f2ceb5db4d26c932bf06a58e95117f656df4c3ba3eaf78fd632a470ccf696962794c`
- **CurseForge:** project `1150827` (slug `runeborn-soulslike-rpg-progression`) · newest 1.21.1 NeoForge file `9296400` `runeborn-neoforge-1.21.1-3.0.0.jar` (release)
- **Dependencies:** required _none_; optional `remnants-rpg-stats-skills-progression`. Modrinth lists: remnants-rpg-stats-skills-progression (optional). `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.0,). Licence Apache-2.0. Side: **both**.

**What it does (3.0 "Rise of the Runeborn"; new mod id `runeborn`, Fine Tuned Weaponry 2.x worlds do not carry over):**

- **Runes:**
  - Kills pay runes, more for higher-level foes, champions and Sovereigns.
  - On death your runes stay where you fell, marked with a green glow. Recover them, or lose them if you die again (`dropRunesOnDeath`).
- **Ember Shrine** (`runeborn:ember_shrine`):
  - Crafted from a campfire, gold ingots, blaze powder and polished deepslate, then kindled.
  - Each shrine is named after the land around it.
  - Rest to restore HP/FP, refill flasks and set respawn (`shrineSetsRespawn`).
  - Shrine menu: Level Up, Reinforce, Infuse, divide **Flasks** between Ember (HP) and Azure (FP), **Travel** between kindled shrines (`shrineFastTravel`), a Merchant, exchanging **Relics** for legendary armaments, equipping a **Crown Shard**, and a Tear of Rebirth respec.
- **Origins** (10): Knight-Errant, Ashborn, Astromancer, Cutthroat, Duelist, Hexblade, Oracle, Penitent, Ronin, Warlord.
- **Attributes** (8): Vigor, Mind, Endurance, Strength, Dexterity, Intelligence, Faith, Arcane. Rune level is the sum of all eight.
- **Shrine level-ups require RAS** (`levelUpRequiresRpgAttributeSystem`, default true). Every rune level also grants `rpgLevelsPerRuneLevel` RAS levels.
- **Armaments:**
  - 74 weapons in 19 classes (dagger … sacred seal), with S–E scaling grades, attribute requirements, and physical, magic, fire, lightning and holy damage.
  - Status build-up: Hemorrhage (bleed), Frostbite, Poison, Blight.
  - **23 weapon arts** on **R**, paid in FP. **12 spells** cast from staves (Intelligence) or sacred seals (Faith).
  - Vanilla and modded swords, axes and tridents also scale with attributes (`vanillaWeaponsScale`).
- **Upgrades:**
  - Tempering Stones I–VIII take standard weapons to +25.
  - Lustrous Stones I–IX take legendary weapons to +10.
  - Sovereign Tempering and Lustrous stones also exist.
  - **13 affinities** come from Whetstones: Heavy, Keen, Quality, Magic, Fire, Flame Art, Lightning, Sacred, Cold, Blood, Poison, Occult, and Standard.
- **Combat layer:**
  - Stamina for attacks and dodges, plus a **dodge roll** with i-frames on **Left Alt**.
  - Its own HP/FP/stamina HUD; it hides vanilla hearts and armor (`hideVanillaHearts`).
  - Target level and build-up display, Sovereign boss bars, and cinematic banners ("Rise, Runeborn", "YOU DIED", "Sovereign Felled", "Shrine Kindled", "Runes Recovered", "Crown Shard Claimed").
- **Mob levels and champions:**
  - Mob levels grow with distance and are higher in the Nether and End.
  - About 1 in 25 hostiles spawns as a gold-titled **champion** with affixes (Blazing, Bloodthirsty, Colossal, Frenzied, Frostborne, Ironclad, Phasing, Stormtouched, Venomous, Warded) and carries **Sovereign Fragments**.
- **Sovereigns:** craft a **Sigil** from 6 Sovereign Fragments plus a token item, then use it to summon:

  | Sovereign | Title | Level | Token |
  |---|---|---|---|
  | The Dusk Rider | "Who Rides When Light Fails" | 15 | clock |
  | Varghast the Grafted | Sovereign of the Hollow Vale | 20 | iron block |
  | Sylvara, Frost Matron | Sovereign of the Rime Veil | 25 | blue ice |
  | Kaelthar the Stormcaller | Sovereign of the Drowned Sky | 30 | lightning rod |
  | Ysolde, the Crimson Bloom | Sovereign of the Scarlet Garden | 35 | redstone block |
  | Morgrath, Ash Sovereign | Sovereign of the Burning Crown | 50 | netherite scrap |
  | Vaelorn, the Wyrm-Ravager | Sovereign of the Last Shore | 70 | dragon's breath |

  The Dusk Rider also rides at night (`duskRiderSpawns`).
  - Each drops a **Relic** (exchanged for its legendary weapon) and a **Crown Shard** (a passive bonus).
  - The Ender Dragon, Wither, Warden and Elder Guardian drop relics too. The dragon also drops a crown shard.
- **Codex** (status screen on **I**): chapters plus crafting grids. The **Feats** advancement tab has 22 entries.

**Quest notes:** detect Sovereign kills with `runeborn:feats/fell_*` (Dusk Rider, Varghast, Sylvara, Kaelthar, Ysolde, Morgrath, Vaelorn), not by entity type. Use `runeborn:feats/kindle` for the first shrine and `runeborn:feats/level_20|50|100` for rune levels.

**Server config keys** (from the jar):
- Runes and costs: `runeGainMultiplier`, `levelCostMultiplier`, `smithingCostMultiplier`, `merchantPriceMultiplier`, `dropRunesOnDeath`, `requireClassSelection`
- RAS link: `levelUpRequiresRpgAttributeSystem`, `rpgLevelsPerRuneLevel`
- Stamina and combat: `staminaEnabled`, `attacksCostStamina`, `exhaustedDamageMultiplier`, `dodgeStaminaCost`, `dodgeInvulnerabilityTicks`, `pvpDamageMultiplier`, `focusRegenPerSecond`, `staminaRegenPerSecond`, `vanillaWeaponsScale`
- Mob levels: `mobLevelsEnabled`, `blocksPerLevel`, `overworldMaxLevel`, `netherBaseLevel`, `netherMaxLevel`, `endBaseLevel`, `endMaxLevel`, `otherDimensionMaxLevel`, `healthPerLevel`, `damagePerLevel`, `eliteChance`
- Bosses and shrines: `duskRiderSpawns`, `duskRiderNightlyChance`, `bossesBreakBlocks`, `shrineFastTravel`, `shrineSetsRespawn`, `shrineTravelCooldownSeconds`

**Client config keys:** `hudEnabled`, `hideVanillaHearts`, `showBarNumbers`, `showBanners`, `showTargetBar`, `showBossBars`, `showEquipment`, `hudOffsetX`, `hudOffsetY`, `hudScale`.

**Fit and overlaps:** the best soulslike fit of the set.
- It overlaps **RPG Mobs** on mob levels and champions. Disable Runeborn mob levels; RPG Mobs may still rank a Sovereign, since they are vanilla mob types.
- It overlaps **RAS** on attributes, by design.
- It overlaps **Skills and Powers** on active abilities and a mana bar.
- Its shrines resemble the **Eclipsed Realm's** Grace Embers. Keep shrines for the Overworld and graces for the Realm.
- Keys R and I clash (§4). Its target bar duplicates RPG Mobs' nameplates (`showTargetBar: false`).
- It ships no Better Combat `weapon_attributes` data.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `runeborn`
- Items (143): `runeborn:abyssal_scepter`, `runeborn:ashborn_club`, `runeborn:ashen_greatsword`, `runeborn:astral_staff`, `runeborn:azure_flask`, `runeborn:banneret_greatsword`, `runeborn:beast_claws`, `runeborn:blank_whetstone`, `runeborn:blood_whetstone`, `runeborn:bloodbloom_sigil`, `runeborn:bloomwarden_mace`, `runeborn:cold_whetstone`, `runeborn:crimsonfall`, `runeborn:crown_shard_ender_dragon`, `runeborn:crown_shard_kaelthar`, `runeborn:crown_shard_morgrath`, `runeborn:crown_shard_sylvara`, `runeborn:crown_shard_vaelorn`, `runeborn:crown_shard_varghast`, `runeborn:crown_shard_ysolde`, `runeborn:crownsplitter`, `runeborn:crystal_spire_staff`, `runeborn:cutthroat_kris`, `runeborn:desert_shamshir`, `runeborn:dragonsoul_seal`, `runeborn:duelist_scimitar`, `runeborn:duskrider_glaive`, `runeborn:eclipse_twinblade`, `runeborn:ember_flask`, `runeborn:ember_shrine`, `runeborn:emberbrand`, `runeborn:errant_longsword`, `runeborn:executioner_greataxe`, `runeborn:faded_rune`, `runeborn:fangtooth_cleaver`, `runeborn:fire_whetstone`, `runeborn:flame_art_whetstone`, `runeborn:flame_prayer_seal`, `runeborn:frostbound_staff`, `runeborn:golden_rite_seal`, `runeborn:graft_axe`, `runeborn:grave_scythe`, `runeborn:gravebound_staff`, `runeborn:gravewarden_scythe`, `runeborn:hallowed_lance`, `runeborn:hallowed_tear`, `runeborn:heavy_whetstone`, `runeborn:hellbrand`, `runeborn:heros_rune`, `runeborn:hexblade_estoc`, `runeborn:highland_claymore`, `runeborn:hollow_monk_staff`, `runeborn:iron_warhammer`, `runeborn:ironbound_knuckles`, `runeborn:jawbone_axe`, `runeborn:keen_whetstone`, `runeborn:lightning_whetstone`, `runeborn:longfang_nodachi`, `runeborn:lunar_bloomfang`, `runeborn:lustrous_rune`, `runeborn:lustrous_stone_1`, `runeborn:lustrous_stone_2`, `runeborn:lustrous_stone_3`, `runeborn:lustrous_stone_4`, `runeborn:lustrous_stone_5`, `runeborn:lustrous_stone_6`, `runeborn:lustrous_stone_7`, `runeborn:lustrous_stone_8`, `runeborn:lustrous_stone_9`, `runeborn:magic_whetstone`, `runeborn:magma_falchion`, `runeborn:militia_spear`, `runeborn:mistveil_katana`, `runeborn:morning_star`, `runeborn:noble_rapier`, `runeborn:oathsworn_blade`, `runeborn:occult_whetstone`, `runeborn:ossuary_blade`, `runeborn:penitent_mace`, `runeborn:pilgrim_seal`, `runeborn:poison_whetstone`, `runeborn:quality_whetstone`, `runeborn:radiant_rune`, `runeborn:ravager_greataxe`, `runeborn:rebirth_tear`, `runeborn:relic_dusk_rider`, `runeborn:relic_elder_guardian`, `runeborn:relic_ender_dragon`, `runeborn:relic_kaelthar`, `runeborn:relic_morgrath`, `runeborn:relic_sylvara`, `runeborn:relic_vaelorn`, `runeborn:relic_varghast`, `runeborn:relic_warden`, `runeborn:relic_wither`, `runeborn:relic_ysolde`, `runeborn:rimebite_axe`, `runeborn:rimeguard_sword`, `runeborn:rimeveil`, `runeborn:ronin_uchigatana`, `runeborn:ruinbreaker`, `runeborn:rusted_dagger`, `runeborn:sacred_whetstone`, `runeborn:sentinel_halberd`, `runeborn:shadowfang`, `runeborn:sigil_dusk_rider`, `runeborn:sigil_kaelthar`, `runeborn:sigil_morgrath`, `runeborn:sigil_sylvara`, `runeborn:sigil_vaelorn`, `runeborn:sigil_varghast`, `runeborn:sigil_ysolde`, `runeborn:sovereign_fragment`, `runeborn:sovereign_lustrous_stone`, `runeborn:sovereign_rune`, `runeborn:sovereign_tempering_stone`, `runeborn:starfall_slab`, `runeborn:starshard_kris`, `runeborn:stoneheart_maul`, `runeborn:storm_totem`, `runeborn:stormcaller_pike`, `runeborn:stormfang`, `runeborn:stormglass_rod`, `runeborn:sunlit_sword`, `runeborn:sunseed`, `runeborn:tempering_stone_1`, `runeborn:tempering_stone_2`, `runeborn:tempering_stone_3`, `runeborn:tempering_stone_4`, `runeborn:tempering_stone_5`, `runeborn:tempering_stone_6`, `runeborn:tempering_stone_7`, `runeborn:tempering_stone_8`, `runeborn:thornlash`, `runeborn:thornspur_rapier`, `runeborn:titans_gavel`, `runeborn:twinfang_glaive`, `runeborn:venomfang_stiletto`, `runeborn:voidstar_hammer`, `runeborn:warlord_battleaxe`, `runeborn:wavecut_flamberge`, `runeborn:winters_hook`, `runeborn:wyrmfang_halberd`
- Blocks (1): `runeborn:ember_shrine`
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements (22): `runeborn:feats/champion` (Champion's Bane), `runeborn:feats/crown` (The Crown Remade), `runeborn:feats/died` (You Died), `runeborn:feats/fell_dusk_rider` (Fell the Dusk Rider), `runeborn:feats/fell_kaelthar` (Fell Kaelthar the Stormcaller), `runeborn:feats/fell_morgrath` (Fell Morgrath, Ash Sovereign), `runeborn:feats/fell_sylvara` (Fell Sylvara, Frost Matron), `runeborn:feats/fell_vaelorn` (Fell Vaelorn, the Wyrm-Ravager), `runeborn:feats/fell_varghast` (Fell Varghast the Grafted), `runeborn:feats/fell_ysolde` (Fell Ysolde, the Crimson Bloom), `runeborn:feats/infused` (A Keener Edge), `runeborn:feats/kindle` (Ember in the Dark), `runeborn:feats/level_100` (Ascendant), `runeborn:feats/level_20` (Rune-Touched), `runeborn:feats/level_50` (Runebearer), `runeborn:feats/masterwork` (Masterwork), `runeborn:feats/rebirth` (Born Anew), `runeborn:feats/reclaimed` (Not This Time), `runeborn:feats/root` (Runeborn), `runeborn:feats/summon` (The Summoning), `runeborn:feats/tempered` (Tempered Steel), `runeborn:feats/travel` (Paths of Ember)
- Sounds: 0 · Loot tables: 1 · Recipes: 24
- Keybinds (default; b = read from bytecode, p = mod page): `key.runeborn.art` Weapon Art = **R (p)**; `key.runeborn.character` Status Screen / Codex = **I (p)**; `key.runeborn.dodge` Dodge Roll = **Left Alt (p)**
- Config files: `config/runeborn-server.json`, `config/runeborn-client.json`
- Lang copy: `modpack/research/registry/runeborn_en_us.json`

### 2.4 Remnants | RPG Mobs: include

- **Modrinth** (NeoForge 1.21.1, newest release): `3.0.0` · version id `9GU0cPjU` · `remnant_mobs-neoforge-1.21.1-3.0.0.jar` · 400,663 bytes · published 2026-10-24
  - url: https://cdn.modrinth.com/data/4eSfhd3M/versions/9GU0cPjU/remnant_mobs-neoforge-1.21.1-3.0.0.jar
  - sha1 `d6724cc1ddefa0c85fe9ec46cfc3b3dad78b9843`
  - sha512 `a8173ea4581722ad078ead6e582765662c14bb2f76e216f413600ada1475d9f5bcb9f5e0024a93c163a31eab22f18fb732ed13c6d8b118b1f5b8bd8ab65413bf`
- **CurseForge:** project `1088344` (slug `remnants-rpg-mobs`) · newest 1.21.1 NeoForge file `9308810` `remnant_mobs-neoforge-1.21.1-3.0.0.jar` (release)
- **Dependencies:** required _none_; optional `remnants-rpg-stats-skills-progression`. Modrinth lists: none listed. `neoforge.mods.toml` declares: rpg_attribute_system optional [4.0,); rpgmoblevelingsystem incompatible [0,). NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does (3.0 "Blood and Valor"; mod id `remnant_mobs`; replaces RPG Mob Leveling System, whose id `rpgmoblevelingsystem` is declared *incompatible*; 2.x configs migrate):**

- **Threat level.** A mob's level comes from where it spawns:
  - distance: +1 per 128 Overworld-equivalent blocks
  - days: +1 per 4 days, up to 15
  - depth: +1 per 12 blocks below Y 32, up to 8
  - structure minimums: ancient city 40, end city 50, bastion/mansion 30, stronghold/monument 25, fortress/trial chambers 20, outpost 12
  - nearby RAS players pull levels ⅓ of the way toward their own level

  Dimension bands:

  | Dimension | Levels |
  |---|---|
  | Overworld | 1–60 |
  | Nether | 15–80 |
  | End | 35–100 |
  | **Eclipsed Realm** | 30–100 |
  | Other dimensions | 1–60 |

  Per level: +6% health, +3% damage, +0.15 armor, +0.3% speed. Bosses show a level but are not scaled.
- **Ranks**, rolled at spawn: Common, Veteran (6%), Elite (1.5%), Champion (0.3%), **Remnant** (0.03%, from level 30). A Remnant has:
  - a generated name and title, e.g. "Vorgrim the Hollow"
  - no despawning
  - a horn heard within 48 blocks
  - a boss bar
  - a server-wide death message

  Spawner mobs roll ranks at ¼ the rate.
- **16 traits:** Vampiric, Frostbite, Infernal, Venomous, Withering, Berserk, Crushing, Juggernaut, Thornskin, Warded, Regenerating, Deflecting, Swift, Blinking, Packleader, Volatile.
- **Soulslike nameplates.** They show the rank crest, a level coloured against yours, **a health bar with a drain trail**, and traits. This makes Neat, ToroHealth or Jade health bars redundant.
- **Rewards:**
  - XP ×2/×3/×5/×10 by rank, plus extra loot rolls.
  - **Remnant Shards** from every ranked mob. Absorbing one gives **15 Valor** with RAS, or 8 XP without.
  - **Bonus Valor** with RAS: Veteran 10, Elite 25, Champion 60, Remnant 150, plus level. Kills above your level pay ×1.5; kills far below pay ×0.25.
- **Hunter's Moon.** 35% of full moons: a toll and title, mobs +5 levels, ranks ×2, shards ×2 until dawn. A HUD icon shows it, and `/remnants moon` reports it.
- **Items:**
  - Hunter's Lens: threat readout, and a stat sheet when scoped.
  - Brand of Challenge: a mob gains +1 rank and +5 levels, and its rewards are doubled.
- **Datapack hooks:**
  - Scoreboard tags such as `remnant_mobs.remnant` and `remnant_mobs.trait.vampiric`.
  - Entity tags `#remnant_mobs:bosses`, `#remnant_mobs:never_leveled`, `#remnant_mobs:never_ranked`.

**Answers to the brief:** it **does** have health bars, a **Hunter's Moon** event and **Valor rewards** (via RAS). The 2.x Calendar item and the Neat/Jade hooks were removed.

**Fit:** core difficulty layer. It is already aware of the Eclipsed Realm (level band, and its bosses are in `#remnant_mobs:bosses`) and of Roguelite Dungeons (Archive creatures are `never_leveled`).

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `remnant_mobs`
- Items (3): `remnant_mobs:brand_of_challenge`, `remnant_mobs:hunters_lens`, `remnant_mobs:remnant_shard`
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements (10): `remnant_mobs:accept_the_challenge` (Accept the Challenge), `remnant_mobs:champions_bane` (Champion's Bane), `remnant_mobs:know_thy_enemy` (Know Thy Enemy), `remnant_mobs:nothing_left_to_hide` (Nothing Left to Hide), `remnant_mobs:proven_hunter` (Proven Hunter), `remnant_mobs:punching_up` (Punching Up), `remnant_mobs:remnants_end` (A Remnant's End), `remnant_mobs:root` (Remnants), `remnant_mobs:taste_of_valor` (Taste of Valor), `remnant_mobs:under_the_hunters_moon` (Under the Hunter's Moon)
- Own tags: entity_type: `#remnant_mobs:bosses`, `#remnant_mobs:never_leveled`, `#remnant_mobs:never_ranked`
- Sounds: 11 · Loot tables: 0 · Recipes: 2
- Config files: `config/remnant_mobs/levels.json`, `config/remnant_mobs/ranks.json`, `config/remnant_mobs/traits.json`, `config/remnant_mobs/rewards.json`, `config/remnant_mobs/client.json`
- Lang copy: `modpack/research/registry/remnant_mobs_en_us.json`

### 2.5 Remnants | The Eclipsed Realm (mod id `remnant_bosses`): include

- **Modrinth** (NeoForge 1.21.1, newest release): `3.1.0+neoforge-1.21.1` · version id `HSEZGrga` · `remnant_bosses-neoforge-1.21.1-3.1.0.jar` · 3,988,508 bytes · published 2026-10-20
  - url: https://cdn.modrinth.com/data/coZxDAGe/versions/HSEZGrga/remnant_bosses-neoforge-1.21.1-3.1.0.jar
  - sha1 `4746e41123d356f55e5f6f92955b5b480afd7b05`
  - sha512 `9c6741c6e44259c448195cfc283982957d3d0f294678f2f00d9703197afc4df52be9025631e9ef21ba6bd5cdd24644156953971579e639bfdaf3700c8959263e`
- **CurseForge:** project `1225026` (slug `remnants-eclipsed-realm`) · newest 1.21.1 NeoForge file `9265581` `remnant_bosses-neoforge-1.21.1-3.1.0.jar` (release)
- **Dependencies:** required `geckolib`, `jauml`; optional _none_. Modrinth lists: geckolib (required); jauml (required). `neoforge.mods.toml` declares: geckolib required [4.8.4,); jauml required [1.2.0,). NeoForge [21.1.219,). Licence Apache-2.0. Side: **both**.

**What it does (3.1 "The Realm Endures"):** a boss dimension under a black eclipse sun, with the burning **Gracetree** on the horizon.

**How to reach it:**
1. Craft an **Eclipse Shard** (`remnant_bosses:eclipse_shard`): amethyst shard + ender pearl + gold ingot.
2. Craft a **Waygate** (`remnant_bosses:eclipse_waygate`): 6 polished deepslate, a shard at top centre and a gold ingot at bottom centre.
3. Place it. It raises a 3-wide, 4-tall arch.
4. Use a second Eclipse Shard on the arch. It kindles for 6 s.
5. Walk through. You arrive at an Arrival Shrine with a return Waygate and a Grace Ember.

The dimension is `remnant_bosses:eclipsed_realm`.

**The Realm:**
- Seven biomes: Tarnished Fields, The Gracewood, Gravefield Barrows, Ashen Wastes, The Lantern Heights, The Stilled Sea, and the Ossuary Depths below them.
- **Build protection:** survival players cannot break, place or empty buckets there (`build_protection`). Explosions don't break terrain.
- **Grace Embers** (`remnant_bosses:grace_ember`, found in `remnant_bosses:grace_shrine` structures):
  - Resting heals you, clears effects and sets respawn.
  - Golden motes lead toward the nearest arena.
  - The grace menu fast-travels to discovered graces or **Departs** the Realm.
  - A Name Tag renames a grace.

**Arenas**, each sealed by a **fog gate** that players can pass and mobs cannot:

| Arena | Structure | Boss |
|---|---|---|
| Hollow Citadel | `remnant_bosses:hollow_citadel` | Hollow Sovereign |
| Gravebound Catacombs | `remnant_bosses:gravebound_catacombs` | Gravebound Warden |
| Forgotten Observatory | `remnant_bosses:forgotten_observatory` | Forgotten Watcher |

Each arena has an Ancient Altar already loaded with its offerings.

**Summoning:**
- Craft an **Ancient Altar** and 4 **Ancient Pedestals**. Place the pedestals 3 blocks E/W/S/N of the altar, put the offerings on the pedestals, and use the summon item on the altar.
- The three Realm bosses answer only inside the Realm (`rituals_realm_only`).

| Boss (entity id) | Summon item | Offerings E/W/S/N |
|---|---|---|
| Hollow Sovereign `remnants:hollow_sovereign` | Sovereign's Seal `remnant_bosses:sovereigns_seal` (4 Tarnished Regalia + 4 gold + echo shard) | gold block, gold block, soul lantern, soul lantern |
| Gravebound Warden `remnants:gravebound_warden` | Crypt Key `remnant_bosses:crypt_key` (6 Grave Iron around an iron block; Burial Guardian drop) | bone block, soul soil, chain, iron bars |
| Forgotten Watcher `remnants:forgotten_watcher` | Lens of Memory `remnant_bosses:memory_lens` (4 Memory Shards + 4 amethyst + spyglass) | amethyst block, calcite, chiseled sandstone, lectern |
| **Ossukage** `remnants:ossukage` (works in any dimension) | Nether Star | 4 skeleton skulls |

**Boss mechanics and drops:**
- **Hollow Sovereign:**
  - Phase 1: three-hit combos, a throne slam and a guard (an axe breaks it).
  - Phase 2 (66%): his flying pauldrons, then spectral royal guards.
  - Phase 3 (33%): spectral crescents and a soul lunge.
  - At 10%: "**The Last Command**", a rain of spectral blades.
  - Drops: Sovereign's Ruin, Sovereign's Sigil, Hollow Crown, Royal Soul Fragments.
- **Gravebound Warden:**
  - Executioner sweeps, chain grabs and grave eruptions.
  - Phase 2 (50%): chain walls; break the 4 anchors to stagger him.
  - Drops: Warden's Grasp, Gravebound Executioner, Crypt Sigil, Grave Iron, one Warden armour piece.
- **Forgotten Watcher:**
  - Memory-bolt rings, a beam, and teleports between 4 lens platforms.
  - Phase 2: illusions and a rotating crystal aegis.
  - Drops: Memory Staff, Watcher's Eye, Ancient Knowledge Fragments, Memory Shards.
- **Ossukage**, "the original Remnant":
  - Invulnerable during its rise; sword chain and kunai.
  - Phase 2: transforms, raises soldiers and dashes.
  - Drops the **Ossukage Blade** (`remnant_bosses:ossukage_sword`).

**Gear:**
- Armour sets:
  - **Regalia**: Hollow Crown, Cuirass, Greaves, Sabatons.
  - **Warden**: Helm, Hauberk, Tassets, Boots.
  - **Archivist**: Hood, Robe, Leggings, Boots.
- Off-hand relics: Sovereign's Sigil, Crypt Sigil, Watcher's Eye.
- Weapons: Sovereign's Ruin, Warden's Grasp, Gravebound Executioner, Memory Staff, Ossukage Blade.

**Creature families** (each has an entity-type tag):

| Family (tag) | Creatures |
|---|---|
| `#remnants:hollow_legion` | Hollow Sentinel, Hollow Arbalist, Fallen Standard Bearer, Soulbound Knight, Spectral Royal Guard |
| `#remnants:cryptborn` | Catacomb Rat, Crypt Lurker, Gravebound Soldier, Burial Guardian (miniboss) |
| `#remnants:forgotten_souls` | Lost Pilgrim, Memory Wraith, Soul Collector, Soul Wisp |
| `#remnants:ashbound` | Ashbound Crawler, Ember Servitor, Rusted Guardian |
| `#remnants:corrupted_relics` | Shardling, Ancient Vessel, Relic Stalker |

They spawn only in the Realm. Ashen Cog and Relic Shard are their materials.

**Other UI and systems:**
- The **Boss Hunts Journal** (`remnant_bosses:boss_journal`) tracks each boss as Undiscovered → Encountered → Defeated, per player.
- Fair multiplayer credit: everyone who dealt damage in the last 60 s within 64 blocks.
- Custom pixel boss bars, "**REMNANT FELLED**" splash, area titles, fight theme, camera shake (all toggleable in `config/remnant/client/presentation.json`).
- No keybinds. The lang file has a leftover "Throw Shuriken" key, but no key mapping is registered.

**Quest notes:**
- Kill tasks: use `remnants:*` entity ids, or the family tags above.
- Dimension task: `remnant_bosses:eclipsed_realm`.
- Advancements: `remnant_bosses:realm/root` (first Eclipse Shard), `realm/kindle_waygate`, `realm/enter_realm`, `realm/remnant_felled` (Hollow Sovereign only) and `realm/waking_world` (return).
- Spawn eggs: `remnant_bosses:<mob>_spawn_egg`. **Ossukage's egg is `remnant_bosses:remnant_ossukage_spawn_egg`.**

**Fit and overlaps:**
- Grace Embers vs Runeborn Ember Shrines: both rest, respawn and fast-travel, but in different dimensions, so the overlap is fine.
- "Sovereign" naming collides with Runeborn's seven Sovereigns. This is a lore opportunity (§7).
- The fog gate likely stops Fellowship allies entering boss rooms (inferred from "bosses and creatures cannot"). Verify.
- Its custom boss bars may clash with mods that replace the whole boss overlay.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `remnant_bosses`
- Items (70): `remnant_bosses:ancient_altar`, `remnant_bosses:ancient_pedestal`, `remnant_bosses:ancient_vessel_spawn_egg`, `remnant_bosses:archivist_boots`, `remnant_bosses:archivist_hood`, `remnant_bosses:archivist_leggings`, `remnant_bosses:archivist_robe`, `remnant_bosses:ashbound_crawler_spawn_egg`, `remnant_bosses:ashen_cog`, `remnant_bosses:boss_journal`, `remnant_bosses:burial_guardian_spawn_egg`, `remnant_bosses:catacomb_rat_spawn_egg`, `remnant_bosses:chiseled_eclipse_stone_bricks`, `remnant_bosses:cobbled_eclipse_stone`, `remnant_bosses:cracked_eclipse_stone_bricks`, `remnant_bosses:crypt_key`, `remnant_bosses:crypt_lurker_spawn_egg`, `remnant_bosses:crypt_sigil`, `remnant_bosses:eclipse_shard`, `remnant_bosses:eclipse_stone`, `remnant_bosses:eclipse_stone_brick_slab`, `remnant_bosses:eclipse_stone_brick_stairs`, `remnant_bosses:eclipse_stone_brick_wall`, `remnant_bosses:eclipse_stone_bricks`, `remnant_bosses:eclipse_waygate`, `remnant_bosses:ember_servitor_spawn_egg`, `remnant_bosses:fallen_standard_bearer_spawn_egg`, `remnant_bosses:fog_gate`, `remnant_bosses:forgotten_watcher_spawn_egg`, `remnant_bosses:gilded_leaves`, `remnant_bosses:grace_ember`, `remnant_bosses:graceroot_log`, `remnant_bosses:graceroot_planks`, `remnant_bosses:grave_iron`, `remnant_bosses:gravebound_executioner`, `remnant_bosses:gravebound_soldier_spawn_egg`, `remnant_bosses:gravebound_warden_spawn_egg`, `remnant_bosses:hollow_arbalist_spawn_egg`, `remnant_bosses:hollow_crown`, `remnant_bosses:hollow_sentinel_spawn_egg`, `remnant_bosses:hollow_sovereign_spawn_egg`, `remnant_bosses:knowledge_fragment`, `remnant_bosses:lost_pilgrim_spawn_egg`, `remnant_bosses:memory_lens`, `remnant_bosses:memory_shard`, `remnant_bosses:memory_staff`, `remnant_bosses:memory_wraith_spawn_egg`, `remnant_bosses:ossukage_sword`, `remnant_bosses:regalia_cuirass`, `remnant_bosses:regalia_greaves`, `remnant_bosses:regalia_sabatons`, `remnant_bosses:relic_shard`, `remnant_bosses:relic_stalker_spawn_egg`, `remnant_bosses:remnant_ossukage_spawn_egg`, `remnant_bosses:royal_soul_fragment`, `remnant_bosses:rusted_guardian_spawn_egg`, `remnant_bosses:shardling_spawn_egg`, `remnant_bosses:soul_collector_spawn_egg`, `remnant_bosses:soulbound_knight_spawn_egg`, `remnant_bosses:sovereigns_ruin`, `remnant_bosses:sovereigns_seal`, `remnant_bosses:sovereigns_sigil`, `remnant_bosses:tarnished_regalia`, `remnant_bosses:warden_boots`, `remnant_bosses:warden_hauberk`, `remnant_bosses:warden_helm`, `remnant_bosses:warden_tassets`, `remnant_bosses:wardens_grasp`, `remnant_bosses:watchers_eye`, `remnant_bosses:weathered_gravestone`
- Blocks (19): `remnant_bosses:ancient_altar`, `remnant_bosses:ancient_pedestal`, `remnant_bosses:chiseled_eclipse_stone_bricks`, `remnant_bosses:cobbled_eclipse_stone`, `remnant_bosses:cracked_eclipse_stone_bricks`, `remnant_bosses:eclipse_stone`, `remnant_bosses:eclipse_stone_brick_slab`, `remnant_bosses:eclipse_stone_brick_stairs`, `remnant_bosses:eclipse_stone_brick_wall`, `remnant_bosses:eclipse_stone_bricks`, `remnant_bosses:eclipse_waygate`, `remnant_bosses:fog_gate`, `remnant_bosses:gilded_leaves`, `remnant_bosses:grace_ember`, `remnant_bosses:graceroot_log`, `remnant_bosses:graceroot_planks`, `remnant_bosses:waygate_frame`, `remnant_bosses:waygate_veil`, `remnant_bosses:weathered_gravestone`
- Entities (34): `remnants:ancient_vessel`, `remnants:ashbound_crawler`, `remnants:burial_guardian`, `remnants:catacomb_rat`, `remnants:chain_anchor`, `remnants:crypt_lurker`, `remnants:crystal_bolt`, `remnants:ember_bolt`, `remnants:ember_servitor`, `remnants:fallen_standard_bearer`, `remnants:forgotten_watcher`, `remnants:gravebound_soldier`, `remnants:gravebound_warden`, `remnants:hollow_arbalist`, `remnants:hollow_sentinel`, `remnants:hollow_sovereign`, `remnants:kunai`, `remnants:lost_pilgrim`, `remnants:memory_bolt`, `remnants:memory_wraith`, `remnants:ossukage`, `remnants:ossukage_rune_effect`, `remnants:relic_stalker`, `remnants:royal_blade_mark`, `remnants:rusted_guardian`, `remnants:shardling`, `remnants:soul_collector`, `remnants:soul_wisp`, `remnants:soulbound_knight`, `remnants:sovereign_pauldron`, `remnants:spectral_crescent`, `remnants:spectral_royal_guard`, `remnants:warden_chain`, `remnants:watcher_illusion`
- Dimensions: `remnant_bosses:eclipsed_realm`
- Biomes: `remnant_bosses:ashen_wastes`, `remnant_bosses:gracewood`, `remnant_bosses:gravefield_barrows`, `remnant_bosses:lantern_heights`, `remnant_bosses:ossuary_depths`, `remnant_bosses:stilled_sea`, `remnant_bosses:tarnished_fields`
- Structures (worldgen, usable with `/locate structure`): `remnant_bosses:forgotten_observatory`, `remnant_bosses:grace_shrine`, `remnant_bosses:gravebound_catacombs`, `remnant_bosses:hollow_citadel`
- Advancements (5): `remnant_bosses:realm/enter_realm` (Beneath the Eclipse), `remnant_bosses:realm/kindle_waygate` (The Way Remembered), `remnant_bosses:realm/remnant_felled` (The Last Command Ends), `remnant_bosses:realm/root` (Splinter of the Black Sun), `remnant_bosses:realm/waking_world` (The Waking World)
- Own tags: entity_type: `#remnants:ashbound`, `#remnants:corrupted_relics`, `#remnants:cryptborn`, `#remnants:forgotten_souls`, `#remnants:hollow_legion`; item: `#remnant_bosses:ossukage_sword_repair_items`, `#remnant_bosses:realm_usable`; worldgen/biome: `#remnant_bosses:has_structure/forgotten_observatory`, `#remnant_bosses:has_structure/grace_shrine`, `#remnant_bosses:has_structure/gravebound_catacombs`, `#remnant_bosses:has_structure/hollow_citadel`, `#remnant_bosses:in_eclipsed_realm`, `#remnant_bosses:is_eclipsed_realm`; worldgen/structure: `#remnant_bosses:remnant_arenas`
- Sounds: 16 · Loot tables: 45 · Recipes: 33
- Config files: `config/remnant/bosses/<boss>.json`, `config/remnant/bosses/_summon.json`, `config/remnant/monsters/<creature>.json`, `config/remnant/realm/realm.json`, `config/remnant/client/presentation.json`, `config/remnant/items/ossukage_sword.json`
- Lang copy: `modpack/research/registry/remnant_bosses_en_us.json`

### 2.6 Remnants: Roguelite Dungeons (mod id `tbos`, formerly *The Birth of Steve*): include

- **Modrinth** (NeoForge 1.21.1, newest release): `1.0.0+mc1.21.1+neoforge` · version id `2apQ9m7S` · `tbos-neoforge-1.21.1-1.0.0.jar` · 12,606,407 bytes · published 2026-10-29
  - url: https://cdn.modrinth.com/data/gKOBlOap/versions/2apQ9m7S/tbos-neoforge-1.21.1-1.0.0.jar
  - sha1 `a47479230f479e9af52c56d0e41ed3b58c72197c`
  - sha512 `a0fe388606f8612477b18a00cae0e7f2b5b023c45a893dba3ebdccda8ca42f2d4ea1d1ebd78b29f09ed95aab258354a55f3e13d88e370f457b308f38ae73ce7e`
- **CurseForge:** project `1621994` (slug `remnants-roguelite-dungeons`) · newest 1.21.1 NeoForge file `9359791` `tbos-neoforge-1.21.1-1.0.0.jar` (release)
- **Dependencies:** required _none_; optional `remnants-rpg-stats-skills-progression`, `remnants-rpg-mobs`. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence LicenseRef-All-Rights-Reserved. Side: **both**.

**What it does (1.0 "Remember or Forget", published 2026-10-29):**

- **Prologue** (the old *Birth of Steve* campaign):
  - Fracture Shrines generate in every Overworld. They are code-placed, not `/locate`-able.
  - The **Yesterglass Lens** (cracked, then repaired).
  - The **Meridian Archive**'s four puzzle sites: Hall of Alignment, Choir of Hours, Broken Meridian, and memory-scene reconstruction with the 6 **Memory Plates**.
  - **The Last Curator** (`tbos:phoenix_guardian`), with phases Catalogue, Revision and Erasure. Defeating him turns the Archive Core into the **Curator Gateway**.
- **Expeditions:**
  - Craft a **Memory Key** (`tbos:memory_key`: 4 amethyst, 4 gold, 1 ender pearl).
  - Use it on a **Waystone** (`tbos:waystone`), the Curator Gateway, **or inside any structure** for a "Recollection of <structure>". Each structure works once per player; exclude structures with `#tbos:unrecollectable`.
  - The Attunement screen picks **Distortions**: Fortified, Tyrannical, Bolstering, Volatile, Haunted, Frailty, Hourglass, Amnesia. Each adds Heat. Fracture = tier + Heat.
  - Party members within 24 blocks join the run.
  - Keys go up to tier 20 (×2.9 health / ×1.95 damage).
- **The Fractured Archive** (`tbos:fractured_archive`):
  - Procedural floors from 8 themes: The Parallax Wake, The Starless Gallery, Meridian Descent, Choir of Dust, The Glassbound Vault, The Hollow Catalogue, The Cantor's Labyrinth, The Unwritten Hour.
  - Room types: Threshold, Fracture, Catalogue, Puzzle, Ancient Trap, Lesser Warden, Sanctuary, Exchange, Buried Recollection, Reward Chamber, Last Recollection, …
  - A floor boss sits behind a gate.
- **Remember or Forget:** at each floor's end, **Remember** (bank Renown × Momentum, get a better key) or vote **Forget** (go deeper, Momentum +0.25). A wipe loses everything unbanked.
- **Living Memories**, an in-run build from drafts:
  - Abilities: Echo Lance, Memory Well, Parallax Step, Recall, Reconstruct, Resonant Guard.
  - Artifacts: Delayed Ink, Ember Script, Mason's Remnant, Memory Wick, Piercing Index, Resonant Nail, Returning Thread, Seeking Glass, Shatter Seal, Split Prism, Storm Filament, Ward Fragment.
- **Archive Codex** (**N**): levels 1–30 from banked Renown. The 16 Insights are Steady Hand, Deep Recall, Keen Eye, Archivist's Grace, Bulwark Memory, Echo Strike, Vampiric Recall, Hourglass Mastery, Swift Recollection, Waystone Ward, Second Draft, Lucid Start, Keymaker, Hoarder, Party Bond, Last Stand.
  - Also: the Bestiary (23 creatures), Records, the server **Hall of Records**, and the **Weekly Recollection**.
- **Relics**, generated vanilla weapons and armour:
  - Rarities: Common, Uncommon, Rare, Epic, Legendary, **Remnant**.
  - Affixes: Keen, Quick, Thirsting, Smoldering, Echoing, Archive-Breaking, Reaping / Stalwart, Plated, Tempered, Fleet, Rooted, Mirrored, Warded, Storied.
  - Remnant signatures: Last Hour, Fracture Step, Choir's Echo, Yesterglass.
- **Parties:** `/party …`, up to 4 players, shared revives, party frames.
- **Creatures** (23 entities, all `tbos:`):

  | Group | Creatures |
  |---|---|
  | Bosses and wardens | the Last Curator, Minotaur, Meridian Sentinel, Parallax Wraith |
  | Others | Armillary Scout, Ash Chorister, Blank Chronist, Dust Cantorile, Gallery Moth, Gnomon Knight, Hour Cantor, Hour-Hand Wraith, Index Wight, Labyrinth Usher, Lensward, Memory Leech, Metronome Hound, Null Portrait, Prism Stalker, Shard Drifter, Shardling Swarm, Shelf Crawler, Wake Cutter |

  "Lesser wardens" are re-skinned vanilla types with names: Tribunal Archivist (evoker), Crownless Warden (vindicator), Index Devourer (ravager), and Bronze Reviser (meridian sentinel).
- **Integrations:**
  - With RAS, Remembering grants Valor equal to ¼ of the banked Renown.
  - With RPG Mobs, all 23 Archive creatures are in `#remnant_mobs:never_leveled`.

**Quest notes:**
- `tbos:story/*` advancements trace the prologue in order:
  - `root` (Every Ruin Has a Before)
  - `enter_archive`, `obtain_cracked_lens`, `repair_lens`, `reconstruct_first_room`, `obtain_memory_lantern`
  - `solve_hall_of_alignment`, `complete_choir_of_hours`, `cross_broken_meridian`, `collect_all_memory_plates`, `display_complete_memory_scene`
  - `defeat_last_curator`, then `enter_fractured_archive`
- `tbos:expedition/*` covers the roguelite loop.

**Fit and overlaps:**
- Its "memory/forgetting" theme matches the Eclipsed Realm's Forgotten Watcher, Memory Shards and Archivist set.
- Name collisions:
  - Waystone vs the Waystones mod's `waystones:waystone` (no id clash)
  - Shardling Swarm vs `remnants:shardling`
  - its party system vs Fellowship's warband (different things)
  - party frames on the left vs Fellowship frames
- Key clashes on R, G, V, K and N (§4).

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `tbos`
- Items (126): `tbos:alignment_dial`, `tbos:archive_barrel`, `tbos:archive_barrel_stack`, `tbos:archive_bricks`, `tbos:archive_cache`, `tbos:archive_core`, `tbos:archive_crate`, `tbos:archive_crate_stack`, `tbos:archive_large_crate`, `tbos:archive_large_crate_stack`, `tbos:archive_mixed_stack_1`, `tbos:archive_mixed_stack_2`, `tbos:archive_mixed_stack_3`, `tbos:archive_seal`, `tbos:archive_stone`, `tbos:archive_survey_map`, `tbos:archivists_journal`, `tbos:brittle_ash`, `tbos:broken_wooden_grave_cross`, `tbos:cantor_floor`, `tbos:cantor_gate`, `tbos:cantor_rune`, `tbos:cantor_sigil`, `tbos:cantor_wall`, `tbos:catalogue_floor`, `tbos:catalogue_roof`, `tbos:catalogue_trim`, `tbos:catalogue_wall`, `tbos:chiseled_archive_stone`, `tbos:choir_floor`, `tbos:choir_roof`, `tbos:choir_trim`, `tbos:choir_wall`, `tbos:chronicle_bronze`, `tbos:chronicle_shard`, `tbos:chronicle_tile`, `tbos:collapsing_meridian`, `tbos:cracked_archive_stone`, `tbos:cracked_yesterglass_lens`, `tbos:curator_core`, `tbos:damaged_wooden_grave_cross`, `tbos:dead_grave_flower_vase`, `tbos:dead_grave_flowers`, `tbos:descent_floor`, `tbos:descent_roof`, `tbos:descent_trim`, `tbos:descent_wall`, `tbos:engraved_meridian_tile`, `tbos:false_shelf`, `tbos:fracture_coffer`, `tbos:gallery_floor`, `tbos:gallery_roof`, `tbos:gallery_trim`, `tbos:gallery_wall`, `tbos:grave_flower_vase`, `tbos:grave_flowers`, `tbos:gravestone_type_1`, `tbos:gravestone_type_10`, `tbos:gravestone_type_11`, `tbos:gravestone_type_12`, `tbos:gravestone_type_13`, `tbos:gravestone_type_14`, `tbos:gravestone_type_15`, `tbos:gravestone_type_16`, `tbos:gravestone_type_2`, `tbos:gravestone_type_3`, `tbos:gravestone_type_4`, `tbos:gravestone_type_5`, `tbos:gravestone_type_6`, `tbos:gravestone_type_7`, `tbos:gravestone_type_8`, `tbos:gravestone_type_9`, `tbos:ink_pool`, `tbos:iron_cemetery_gate_arch`, `tbos:iron_fence_1`, `tbos:iron_fence_2`, `tbos:labyrinth_floor`, `tbos:labyrinth_roof`, `tbos:labyrinth_trim`, `tbos:labyrinth_wall`, `tbos:lenswork_crystal`, `tbos:light_dust`, `tbos:lying_skeleton`, `tbos:memory_anchor`, `tbos:memory_key`, `tbos:memory_lantern`, `tbos:memory_plate`, `tbos:meridian_relay`, `tbos:meridian_tile`, `tbos:mossy_archive_stone`, `tbos:parallax_panel`, `tbos:phase_platform`, `tbos:recalled_hour`, `tbos:resonance_lamp`, `tbos:resonant_bell`, `tbos:resonant_plate`, `tbos:rift_threshold`, `tbos:shatter_pane`, `tbos:sitting_skeleton`, `tbos:skeleton_arm`, `tbos:skeleton_leg`, `tbos:skeleton_skull`, `tbos:skeleton_torso`, `tbos:unwritten_floor`, `tbos:unwritten_roof`, `tbos:unwritten_trim`, `tbos:unwritten_wall`, `tbos:vault_floor`, `tbos:vault_roof`, `tbos:vault_trim`, `tbos:vault_wall`, `tbos:wake_floor`, `tbos:wake_roof`, `tbos:wake_trim`, `tbos:wake_wall`, `tbos:waystone`, `tbos:weathered_archive_bricks`, `tbos:wilted_grave_flower_vase`, `tbos:wilted_grave_flowers`, `tbos:wooden_coffin`, `tbos:wooden_coffin_lid`, `tbos:wooden_coffin_skeleton`, `tbos:wooden_grave_cross`, `tbos:wooden_open_coffin`, `tbos:yesterglass`, `tbos:yesterglass_lens`
- Blocks (118): `tbos:alignment_dial`, `tbos:archive_barrel`, `tbos:archive_barrel_stack`, `tbos:archive_bricks`, `tbos:archive_cache`, `tbos:archive_core`, `tbos:archive_crate`, `tbos:archive_crate_stack`, `tbos:archive_large_crate`, `tbos:archive_large_crate_stack`, `tbos:archive_mixed_stack_1`, `tbos:archive_mixed_stack_2`, `tbos:archive_mixed_stack_3`, `tbos:archive_seal`, `tbos:archive_stairs`, `tbos:archive_stone`, `tbos:brittle_ash`, `tbos:broken_wooden_grave_cross`, `tbos:cantor_floor`, `tbos:cantor_gate`, `tbos:cantor_rune`, `tbos:cantor_wall`, `tbos:catalogue_floor`, `tbos:catalogue_roof`, `tbos:catalogue_trim`, `tbos:catalogue_wall`, `tbos:chiseled_archive_stone`, `tbos:choir_floor`, `tbos:choir_roof`, `tbos:choir_trim`, `tbos:choir_wall`, `tbos:chronicle_bronze`, `tbos:chronicle_tile`, `tbos:collapsing_meridian`, `tbos:cracked_archive_stone`, `tbos:damaged_wooden_grave_cross`, `tbos:dead_grave_flower_vase`, `tbos:dead_grave_flowers`, `tbos:descent_floor`, `tbos:descent_roof`, `tbos:descent_trim`, `tbos:descent_wall`, `tbos:engraved_meridian_tile`, `tbos:false_shelf`, `tbos:fracture_coffer`, `tbos:gallery_floor`, `tbos:gallery_roof`, `tbos:gallery_trim`, `tbos:gallery_wall`, `tbos:grave_flower_vase`, `tbos:grave_flowers`, `tbos:gravestone_type_1`, `tbos:gravestone_type_10`, `tbos:gravestone_type_11`, `tbos:gravestone_type_12`, `tbos:gravestone_type_13`, `tbos:gravestone_type_14`, `tbos:gravestone_type_15`, `tbos:gravestone_type_16`, `tbos:gravestone_type_2`, `tbos:gravestone_type_3`, `tbos:gravestone_type_4`, `tbos:gravestone_type_5`, `tbos:gravestone_type_6`, `tbos:gravestone_type_7`, `tbos:gravestone_type_8`, `tbos:gravestone_type_9`, `tbos:ink_pool`, `tbos:iron_cemetery_gate_arch`, `tbos:iron_fence_1`, `tbos:iron_fence_2`, `tbos:labyrinth_floor`, `tbos:labyrinth_roof`, `tbos:labyrinth_trim`, `tbos:labyrinth_wall`, `tbos:lenswork_crystal`, `tbos:light_dust`, `tbos:lying_skeleton`, `tbos:memory_anchor`, `tbos:memory_imprint`, `tbos:memory_lantern`, `tbos:meridian_relay`, `tbos:meridian_tile`, `tbos:mossy_archive_stone`, `tbos:parallax_panel`, `tbos:phase_platform`, `tbos:resonance_lamp`, `tbos:resonant_bell`, `tbos:resonant_plate`, `tbos:rift_threshold`, `tbos:shatter_pane`, `tbos:sitting_skeleton`, `tbos:skeleton_arm`, `tbos:skeleton_leg`, `tbos:skeleton_skull`, `tbos:skeleton_torso`, `tbos:unwritten_floor`, `tbos:unwritten_roof`, `tbos:unwritten_trim`, `tbos:unwritten_wall`, `tbos:vault_floor`, `tbos:vault_roof`, `tbos:vault_trim`, `tbos:vault_wall`, `tbos:wake_floor`, `tbos:wake_roof`, `tbos:wake_trim`, `tbos:wake_wall`, `tbos:waystone`, `tbos:weathered_archive_bricks`, `tbos:wilted_grave_flower_vase`, `tbos:wilted_grave_flowers`, `tbos:wooden_coffin`, `tbos:wooden_coffin_lid`, `tbos:wooden_coffin_skeleton`, `tbos:wooden_grave_cross`, `tbos:wooden_open_coffin`, `tbos:yesterglass`
- Entities (23): `tbos:armillary_scout`, `tbos:ash_chorister`, `tbos:blank_chronist`, `tbos:dust_cantorile`, `tbos:gallery_moth`, `tbos:gnomon_knight`, `tbos:hour_cantor`, `tbos:hour_hand_wraith`, `tbos:index_wight`, `tbos:labyrinth_usher`, `tbos:lensward`, `tbos:memory_leech`, `tbos:meridian_sentinel`, `tbos:metronome_hound`, `tbos:minotaur`, `tbos:null_portrait`, `tbos:parallax_wraith`, `tbos:phoenix_guardian`, `tbos:prism_stalker`, `tbos:shard_drifter`, `tbos:shardling_swarm`, `tbos:shelf_crawler`, `tbos:wake_cutter`
- Dimensions: `tbos:fractured_archive`
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements (28): `tbos:expedition/archivist_eternal` (Archivist Eternal), `tbos:expedition/fellowship` (Fellowship of the Archive), `tbos:expedition/forget` (Forget), `tbos:expedition/fractured` (Fractured), `tbos:expedition/hourglass` (Against the Sand), `tbos:expedition/know_the_archive` (Know the Archive), `tbos:expedition/last_key` (The Last Key), `tbos:expedition/momentum` (No Turning Back), `tbos:expedition/recollection` (Echo of a Place), `tbos:expedition/remember` (Remember), `tbos:expedition/remnant_relic` (Remnant), `tbos:expedition/root` (Remnants: Roguelite Dungeons), `tbos:expedition/storied` (Storied), `tbos:expedition/weekly` (This Week's Memory), `tbos:story/collect_all_memory_plates` (Six Ways to Remember), `tbos:story/complete_choir_of_hours` (The Hours Answer), `tbos:story/cross_broken_meridian` (Causality Has Weight), `tbos:story/defeat_last_curator` (Nothing Escapes the Archive), `tbos:story/display_complete_memory_scene` (The Past, Kept Kindly), `tbos:story/enter_archive` (The Meridian Archive), `tbos:story/enter_fractured_archive` (Beyond the Curator's Gate), `tbos:story/living_memories` ((no display; granted by code)), `tbos:story/obtain_cracked_lens` (A Fractured Memory), `tbos:story/obtain_memory_lantern` (A Memory Made Small), `tbos:story/reconstruct_first_room` (Recall the First Room), `tbos:story/repair_lens` (Through Yesterglass), `tbos:story/root` (Every Ruin Has a Before), `tbos:story/solve_hall_of_alignment` (Lines Across Time)
- Own tags: block: `#tbos:archive_run_palette`, `#tbos:lens_interaction_passthrough`; entity_type: `#remnant_mobs:never_leveled`; worldgen/structure: `#tbos:unrecollectable`
- Sounds: 44 · Loot tables: 119 · Recipes: 4
- Keybinds (default; b = read from bytecode, p = mod page): `key.tbos.codex` Open Archive Codex = **N (b)**; `key.tbos.memory_1` Memory ability 1 = **R (b)**; `key.tbos.memory_2` Memory ability 2 = **G (b)**; `key.tbos.memory_3` Memory ability 3 = **V (b)**; `key.tbos.memory_loadout` Living Memories loadout = **K (b)**; `key.tbos.toggle_objectives` Hide/Show Archive Objectives = **J (b)**
- Config files: `config/tbos-expeditions.json`, `config/tbos-common.json`, `config/tbos-client.json`
- Lang copy: `modpack/research/registry/tbos_en_us.json`

### 2.7 Remnants | Skills and Powers (mod id `elementals`): optional

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.1+neoforge-1.21.1` · version id `QochbfYu` · `remnants-skills-and-powers-neoforge-1.21.1-2.0.1.jar` · 616,255 bytes · published 2026-10-27
  - url: https://cdn.modrinth.com/data/RFO8VXZx/versions/QochbfYu/remnants-skills-and-powers-neoforge-1.21.1-2.0.1.jar
  - sha1 `910cfad445e1f621c68ee8089c7578b5df62f5b9`
  - sha512 `977b98cefed215b172ad9ee3657623ad9a153a80073afad1bcd0554e353fe920de7e2b91346350f9710afd7ef5a03c8451f9750a6528d121e66d0364e364da48`
- **CurseForge:** project `1228643` (slug `remnants-skills-and-powers`) · newest 1.21.1 NeoForge file `9342741` `remnants-skills-and-powers-neoforge-1.21.1-2.0.1.jar` (release)
- **Dependencies:** required _none_; optional `remnants-rpg-stats-skills-progression`. Modrinth lists: remnants-rpg-stats-skills-progression (optional). `neoforge.mods.toml` declares: rpg_attribute_system optional *. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does (2.0 "The Remnant Constellation", a rework of *Elementals*):**
- A **522-node passive tree** (open with **I**): 54 notables, 30 abilities and 12 keystones. Hybrid notables include Plasma Arc, Ionized Flame, Black Ice, Permafrost and Overgrowth.
- **Six schools**, each with five abilities; the last is a 2-point ultimate:

  | School | Abilities |
  |---|---|
  | Pyromancy | Ember Bolt, Explosive Orb, Ember Shield, Inferno Wave, **Meteor** |
  | Stormcalling | Chain Lightning, Static Field, Thunderclap, Gale Step, **Tempest** |
  | Umbral Arts | Shadow Bolt, Soul Harvest, Void Rift, Shadow Step, **Eclipse** |
  | Tidecalling | Frost Lance, Tidebinder, Glacial Prison, Tidal Surge, **Maelstrom** |
  | Earthshaping | Stone Spear, Stone Skin, Tremor, Fissure, **Mountain's Wrath** |
  | Verdance | Mending Light, Thorn Burst, Sanctuary, Radiant Nova, **Verdant Rebirth** |

- **Keystones:** Pyre Heart, Glass Cannon, Conduit, Windborne, Blood Pact, Soul Eater, Eternal Tide, Glacial Bulwark, Unyielding, Bedrock Will, Undying Grove, Verdant Bloom.
- **Casting:** 4 cast slots on **R / Z / B / H**, paid in **Essence**. Abilities use vanilla particles only, never break blocks, and don't hit allies or pets.
- **Build codes** (`RSP1-…`) and `/powers build`.
- **Points:**
  - Power XP from kills and casting, up to Power level 100.
  - **With RAS:** 1 point per RAS level, plus 0.5% ability damage per level (`rpg_player_skills.mode`: auto/replace/add/off).
  - The **Remnant Tome** gives +1 point, up to 20. **Tome of Unbinding** resets the tree.
- **Fire Golems** spawn in the Nether wastes, crimson forests and basalt deltas, and drop Fire Runes.
- The tree can be custom-built in `skill_tree.json`.

**Fit and overlaps:** a strong build layer, but it overlaps **Runeborn**:
- 23 weapon arts and 12 FP spells vs 30 Essence abilities.
- Two magic resource bars.
- Key clashes: **I** (both open their main screen) and **R**.
- It also takes **B** (Minimap marker) and **Z** (Wands undo).
- Compared with Iron's Spells, it is another full caster system.

Choose one primary magic layer. Runeborn spells are sufficient for a souls-like; add Skills and Powers only for a "Remnant Constellation" class fantasy, and rebind its keys.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `elementals`
- Items (10): `elementals:ember_fire_shield_spell_book`, `elementals:explosive_orb_spell_book`, `elementals:fire_element_food`, `elementals:fire_golem_spawn_egg`, `elementals:fire_rune`, `elementals:inferno_wave_spell_book`, `elementals:remnant_tome`, `elementals:tome_of_unbinding`, `elementals:water_element_food`, `elementals:water_rune`
- Blocks (0): _none_
- Entities (3): `elementals:explosive_fire_orb`, `elementals:fire_golem`, `elementals:fire_signature`
- Effects: `elementals:tidebinder_effect`
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 1 · Recipes: 4
- Keybinds (default; b = read from bytecode, p = mod page): `key.elementals.open_tree` Open Skill Tree = **I (b)**; `key.elementals.cast_1` Cast Ability Slot 1 = **R (b)**; `key.elementals.cast_2` Cast Ability Slot 2 = **Z (b)**; `key.elementals.cast_3` Cast Ability Slot 3 = **B (b)**; `key.elementals.cast_4` Cast Ability Slot 4 = **H (b)**
- Config files: `abilities.json`, `skill_tree.json`, `skill_tree.default.json`, `general.json (config folder name not visible in the jar)`, `player data: <world>/remnants_powers/`
- Lang copy: `modpack/research/registry/elementals_en_us.json`

### 2.8 Remnants | Fellowship (mod id `better_with_gold`): include

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `CH1NxWq9` · `better_with_gold-neoforge-1.21.1-2.0.0.jar` · 686,757 bytes · published 2026-10-28
  - url: https://cdn.modrinth.com/data/B3cmf35A/versions/CH1NxWq9/better_with_gold-neoforge-1.21.1-2.0.0.jar
  - sha1 `2c9d5b3925b15cd6ab30889da8e3ba2303824840`
  - sha512 `5ccf23849925a465a28b761df4974177ea021d14bc03fb7e92a926116e5745ce2bfd207dd9de66941671aff73cefe4f01e1361b6d3e86e665c8153d19c12654c`
- **CurseForge:** project `1305455` (slug `remnants-fellowship`) · newest 1.21.1 NeoForge file `9349123` `better_with_gold-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional `remnants-rpg-stats-skills-progression`. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does (2.0, a rework of *Better With Gold*):**
- **Hiring:**
  - Sellswords (`better_with_gold:ally`, shown as "Sellsword") appear near village bells.
  - Hire one by using it while holding **gold ingots**: 7–12 gold at level 1, plus 2–3 per level.
  - Up to 6 per leader (`partySize`, max 24).
- **Allies:**
  - Each rolls 1–2 of 11 traits: Steadfast, Swift, Brutal, Keen-eyed, Stalwart, Devoted, Lucky, Greedy, Hardy, Fearless, Merciful. The trait gives the epithet ("Brenna the Steadfast", "Corwin Bonebreaker").
  - Level 20 cap, with titles Veteran, Champion, Hero and Legend.
  - Morale rises and falls with the fight.
  - Real gear can be handed over.
- **Classes:** Bulwark (Challenge taunt), Skirmisher (Whirl), Ranger (Volley), Mender (Mend + revive), Arcanist (Arc Storm). Classes are JSON-editable.
- **Command wheel** (hold **G**): Follow, Charge, Focus, Hold, Fall back, Guard banner, Formation, Recall.
- **Formations:** Line, Wedge, Shield Wall, Circle, around you or the planted **Warbanner**.
- **Aggro:** an aggro system with labels.
- **Downed, not dead:** a 30 s bleed-out; crouch-revive takes 3 s. A bled-out ally returns to camp after 5 min, or is lost for good with `permadeath` and joins the **Remembrance**.
- **Roster** (**U**): 3D portraits and a **Chronicle** written from what each ally actually did.
- Allies follow through logouts and dimension changes, and **Recall** reloads lost ones.
- The 17 legacy gold items remain in the "Gilded Regalia" tab. Reinforced Golden Armour buffs nearby allies, and the **Golden Fish** heals an ally and adds +30 morale.

**Answer to the brief:** it uses **no custom currency**. Sellswords are paid in vanilla gold ingots; the "hiring currency" is configurable in `fellowship.json`.

**Fit:** a strong narrative device (named companions with chronicles). Lower `partySize` for souls difficulty. Allies are vanilla owned entities, so RPG Mobs, Skills and Powers and Loot Bags all credit them to the owner.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `better_with_gold`
- Items (18): `better_with_gold:golden_fish`, `better_with_gold:golden_scythe`, `better_with_gold:greater_golden_axe`, `better_with_gold:greater_golden_hammer`, `better_with_gold:reinforced_golden_armor_boots`, `better_with_gold:reinforced_golden_armor_chestplate`, `better_with_gold:reinforced_golden_armor_helmet`, `better_with_gold:reinforced_golden_armor_leggings`, `better_with_gold:reinforced_golden_axe`, `better_with_gold:reinforced_golden_hoe`, `better_with_gold:reinforced_golden_pick_axe`, `better_with_gold:reinforced_golden_scythe`, `better_with_gold:reinforced_golden_shovel`, `better_with_gold:reinforced_golden_sword`, `better_with_gold:reinforced_greater_golden_axe`, `better_with_gold:reinforced_greater_golden_hammer`, `better_with_gold:upgrade_template`, `better_with_gold:warbanner`
- Blocks (0): _none_
- Entities (2): `better_with_gold:aggro_label`, `better_with_gold:ally`
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 18
- Keybinds (default; b = read from bytecode, p = mod page): `key.better_with_gold.command_wheel` Command wheel (hold) = **G (b)**; `key.better_with_gold.roster` Warband roster = **U (b)**
- Config files: `config/better_with_gold/fellowship.json`, `config/better_with_gold/classes/<class>.json`
- Lang copy: `modpack/research/registry/better_with_gold_en_us.json`

### 2.9 Mob LootBags (mod id `mob_loot_bags`): optional

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `sGjV41xA` · `mob_loot_bags-neoforge-1.21.1-2.0.0.jar` · 553,234 bytes · published 2026-10-24
  - url: https://cdn.modrinth.com/data/uEntVAnd/versions/sGjV41xA/mob_loot_bags-neoforge-1.21.1-2.0.0.jar
  - sha1 `3b17da9e83e806dc945b51fa246d3df8599b30cf`
  - sha512 `98f56d188ce9e5ac8f59a5f71d72a2268855bc45d56499ff2942a2c0c412b65d8a94ed5849bd25a6e88095dc058d84761174f0e7f4ad85c4829c4e8bbc2f85aa`
- **CurseForge:** project `1093276` (slug `mob-loot-bags`) · newest 1.21.1 NeoForge file `9307650` `mob_loot_bags-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does (2.0):**
- **Drops:**
  - Hostile kills drop bags 18% of the time (×0.5–×2.5 by toughness).
  - Six tiers: Common, Uncommon, Rare, Epic, Legendary, **Mythic**. Combine 4 bags into the next tier (Mythic also needs a nether star), or split one back.
  - **Bag Luck** from Looting, Luck, mob health, dimension and difficulty.
  - Some zombies, skeletons, piglins and illagers spawn **carrying** a bag. Nether and End kills also roll themed loot.
  - Bosses (vanilla + `#c:bosses`) always drop 3 Epic+ bags.
  - Bad-luck protection.
- **Special bags:** Cursed (gamble/summons), Hourglass (ripens in 5–10 min), Locked (needs a **Diamond Key**), Summoning (spawn eggs). The **Fortune Talisman** improves drops.
- **Opening:** hold-to-open with toasts; Shift shows odds sampled from the real loot tables.
- **Machines:** the **Bag Opener** (9 in / 18 out, redstone modes) and the **Loot Recycler** (junk → salvage → bags).
- **Tuning:** `#mob_loot_bags:bonus/<tier>` tags add modded loot. Farm protection: spawner mobs drop ¼ as often, and a player kill is required.

**Fit:** compatible with RPG Mobs, but a third reward layer (rank loot + shards + bags). The default Mythic tables (nether stars, beacons, maxed netherite) clash with curated soulslike gear. Include only with rewritten tables, and add the Realm bosses to `#mob_loot_bags:bosses`.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `mob_loot_bags`
- Items (14): `mob_loot_bags:commonlootbag`, `mob_loot_bags:cursed_lootbag`, `mob_loot_bags:diamond_key`, `mob_loot_bags:epiclootbag`, `mob_loot_bags:fortune_talisman`, `mob_loot_bags:legendarylootbag`, `mob_loot_bags:locked_lootbags`, `mob_loot_bags:loot_bag_opener_block`, `mob_loot_bags:loot_bag_recycle_block`, `mob_loot_bags:mythiclootbag`, `mob_loot_bags:rarelootbag`, `mob_loot_bags:summoning_lootbags`, `mob_loot_bags:timed_loot_bag`, `mob_loot_bags:uncommonlootbag`
- Blocks (2): `mob_loot_bags:loot_bag_opener_block`, `mob_loot_bags:loot_bag_recycle_block`
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements (13): `mob_loot_bags:bag_opener` (Industrial Looting), `mob_loot_bags:fortune_talisman` (Feeling Lucky), `mob_loot_bags:loot_recycler` (One Mob's Trash), `mob_loot_bags:open_bag` (Loot Goblin), `mob_loot_bags:open_cursed` (Tempting Fate), `mob_loot_bags:open_epic` (Epic Haul), `mob_loot_bags:open_hourglass` (Worth the Wait), `mob_loot_bags:open_legendary` (Jackpot!), `mob_loot_bags:open_locked` (Safecracker), `mob_loot_bags:open_mythic` (Myth Made Real), `mob_loot_bags:open_rare` (Shiny Things), `mob_loot_bags:open_summoning` (Pocket Bestiary), `mob_loot_bags:root` (Mob Loot Bags)
- Own tags: entity_type: `#mob_loot_bags:bag_carriers`, `#mob_loot_bags:bosses`, `#mob_loot_bags:no_bags`; item: `#mob_loot_bags:bonus/common`, `#mob_loot_bags:bonus/epic`, `#mob_loot_bags:bonus/legendary`, `#mob_loot_bags:bonus/mythic`, `#mob_loot_bags:bonus/rare`, `#mob_loot_bags:bonus/uncommon`, `#mob_loot_bags:loot_bags`, `#mob_loot_bags:recycler_junk`
- Sounds: 15 · Loot tables: 23 · Recipes: 14
- Config files: `config/mob_loot_bags/drops.json`, `config/mob_loot_bags/bags.json`, `config/mob_loot_bags/machines.json`, `config/mob_loot_bags/client.json`
- Lang copy: `modpack/research/registry/mob_loot_bags_en_us.json`

### 2.10 Much More Dungeons (mod id `muchmoredungeons`): include

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `iywfJnLP` · `muchmoredungeons-neoforge-1.21.1-2.0.0.jar` · 581,293 bytes · published 2026-10-25
  - url: https://cdn.modrinth.com/data/ydBxwDBa/versions/iywfJnLP/muchmoredungeons-neoforge-1.21.1-2.0.0.jar
  - sha1 `0b7324f83c5e54f6f7ba26f33fe576c03005c64f`
  - sha512 `5ea36c86b370fc7342c9c7c95054e025f78ba93b5d13f6bd3579d69a8e6a08e4bb4c2ed3873b3bc64fbebcde88cef3318ff1d6e1cbe9062bd39e1b0284d8deda`
- **CurseForge:** project `1499714` (slug `much-more-dungeons`) · newest 1.21.1 NeoForge file `9317378` `muchmoredungeons-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does (2.0):** 4 handcrafted dungeons plus 6 jigsaw labyrinths.
- Every chest has a tiered loot table plus a guarded vault table.
- Each structure spawns a **named guardian** once: a vanilla mob that never despawns and always drops its weapon.
- Vaults hold a **treasure map to the next tier** ("Dungeon Map: Tier II/III/IV").
- The mod adds no blocks, items or entities, uses vanilla blocks only, and keeps 4 chunks from villages.

| Structure id | Name | Tier | Biomes | Guardian (vanilla mob) |
|---|---|---|---|---|
| `muchmoredungeons:outdoor_villa` | Smuggler's Villa | I | plains, meadows, flower forests, savannas | Smuggler Chief (vindicator) |
| `muchmoredungeons:tower_dungeon` | Arcane Spire | II | forests, taigas | Spire Illusionist (illusioner) |
| `muchmoredungeons:dungeon_t2` | **Cursed Keep** | **III** | deserts, badlands, jungles, swamps, savannas | Keep Warlord (zombie) |
| `muchmoredungeons:soulfire_crypt` | Soulfire Crypt | IV | snowy plains/slopes, groves, ice spikes, taigas | Cinder Warden (wither skeleton) |
| `muchmoredungeons:catacombs` | Forgotten Catacombs | II | under plains/meadows/forests | Bone Warden (skeleton) |
| `muchmoredungeons:sandstone_tomb` | Sunscorched Tomb | II | under deserts/badlands | Tomb King (husk) |
| `muchmoredungeons:overgrown_warrens` | Verdant Warrens | II | under jungles/swamps/lush caves | Broodmother (spider) |
| `muchmoredungeons:frost_vaults` | Rimefrost Vaults | III | under snowy biomes | Frost Lich (stray) |
| `muchmoredungeons:deepslate_halls` | Abyssal Halls | IV | deep under any Overworld biome | Abyssal Knight (wither skeleton) |
| `muchmoredungeons:nether_bastille` | Infernal Bastille | IV | the Nether (y≈40) | Brute Overseer (piglin brute) |

Locate them with `#muchmoredungeons:dungeons` or `#muchmoredungeons:labyrinths`. Use the advancements `discover_*`, `slay_*_guardian`, `all_dungeons` (Dungeon Delver) and `all_labyrinths` (Into Every Maze).

**Fit:** excellent quest scaffolding (the "dungeon trail"), removable without breaking worlds.
- Overlaps YUNG's Better Dungeons and When Dungeons Arise only in theme.
- RPG Mobs does not list these structures in its structure-minimum table; add them in `levels.json` if you want minimum levels there.
- Roguelite Memory Keys can "recollect" any of them.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `muchmoredungeons`
- Items (0): _none_
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): `muchmoredungeons:catacombs`, `muchmoredungeons:deepslate_halls`, `muchmoredungeons:dungeon_t2`, `muchmoredungeons:frost_vaults`, `muchmoredungeons:nether_bastille`, `muchmoredungeons:outdoor_villa`, `muchmoredungeons:overgrown_warrens`, `muchmoredungeons:sandstone_tomb`, `muchmoredungeons:soulfire_crypt`, `muchmoredungeons:tower_dungeon`
- Advancements (23): `muchmoredungeons:all_dungeons` (Dungeon Delver), `muchmoredungeons:all_labyrinths` (Into Every Maze), `muchmoredungeons:discover_catacombs` (Rest in Pieces), `muchmoredungeons:discover_deepslate_halls` (Bottom of the World), `muchmoredungeons:discover_dungeon_t2` (Cursed Ground), `muchmoredungeons:discover_frost_vaults` (Cold Storage), `muchmoredungeons:discover_nether_bastille` (Hot Property), `muchmoredungeons:discover_outdoor_villa` (Contraband), `muchmoredungeons:discover_overgrown_warrens` (Into the Green), `muchmoredungeons:discover_sandstone_tomb` (Sealed Away), `muchmoredungeons:discover_soulfire_crypt` (Cold Fire), `muchmoredungeons:discover_tower_dungeon` (Spellbound Heights), `muchmoredungeons:root` (Much More Dungeons), `muchmoredungeons:slay_catacombs_guardian` (Bone Dry), `muchmoredungeons:slay_deepslate_halls_guardian` (Knight Fall), `muchmoredungeons:slay_dungeon_t2_guardian` (Warlord Fallen), `muchmoredungeons:slay_frost_vaults_guardian` (Thaw), `muchmoredungeons:slay_nether_bastille_guardian` (Overseen), `muchmoredungeons:slay_outdoor_villa_guardian` (Chief Out), `muchmoredungeons:slay_overgrown_warrens_guardian` (Exterminator), `muchmoredungeons:slay_sandstone_tomb_guardian` (Dethroned), `muchmoredungeons:slay_soulfire_crypt_guardian` (Ashes to Ashes), `muchmoredungeons:slay_tower_dungeon_guardian` (Illusions Shattered)
- Own tags: worldgen/biome: `#muchmoredungeons:has_structure/catacombs`, `#muchmoredungeons:has_structure/deepslate_halls`, `#muchmoredungeons:has_structure/dungeon_t2`, `#muchmoredungeons:has_structure/frost_vaults`, `#muchmoredungeons:has_structure/nether_bastille`, `#muchmoredungeons:has_structure/outdoor_villa`, `#muchmoredungeons:has_structure/overgrown_warrens`, `#muchmoredungeons:has_structure/sandstone_tomb`, `#muchmoredungeons:has_structure/soulfire_crypt`, `#muchmoredungeons:has_structure/tower_dungeon`; worldgen/structure: `#muchmoredungeons:dungeons`, `#muchmoredungeons:labyrinths`, `#muchmoredungeons:on_tier2_maps`, `#muchmoredungeons:on_tier3_maps`, `#muchmoredungeons:on_tier4_maps`
- Sounds: 0 · Loot tables: 20 · Recipes: 0
- Config files: `config/muchmoredungeons.json`
- Lang copy: `modpack/research/registry/muchmoredungeons_en_us.json`

### 2.11 Fisherman's Coast (mod id `fisherman_house`): include

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `Evb6ajjS` · `fisherman_house-neoforge-1.21.1-2.0.0.jar` · 513,335 bytes · published 2026-10-26
  - url: https://cdn.modrinth.com/data/Dku9hJfB/versions/Evb6ajjS/fisherman_house-neoforge-1.21.1-2.0.0.jar
  - sha1 `042937b528e54903e7bd5e1d1953f8bcb9d7bc6d`
  - sha512 `4b0937bad43e2f4e3efa693caf44cceecb34da0f4c7cbc2d13678125f80b6bc34a2f703715ed2f0c499ae3d84971a32e3cd3ae61f0ebe0db565e51d74de442e7`
- **CurseForge:** project `1388089` (slug `fisherman-coast`) · newest 1.21.1 NeoForge file `9330850` `fisherman_house-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.219,). Licence Apache-2.0. Side: **both**.

**What it does (2.0 "The Living Coast"):** seven shore-aware structures. Each samples the terrain and rotation before placing, so docks point into water at least 3 deep, nothing floats, and the wreck sits under at least 12 water.

| Structure | Where | Resident |
|---|---|---|
| Fisherman's Cottage (`fisherman_house:fisherman_house`) | sandy and snowy beaches | Saylor |
| Harbour Pier | sandy beaches | Harbourmaster Wren |
| Lighthouse | stony shores | Keeper Morrow |
| Stilt Shack | swamps | Old Bayou Tam |
| Ice Fishing Camp | frozen ocean/river | Frost-Beard Ole |
| River Boathouse | river banks | Ferryman Hale |
| Sunken Trawler | ocean floor | two drowned deckhands; captain's chest may hold a Heart of the Sea |

- Residents are vanilla journeyman fishermen with exclusive trades.
- **Crab Pots:** 5 biome catch tables, 2× in rain, hopper/comparator support, baits (Fish Bait, Chum, Glow Bait).
- **Fishing Nets:** climbable and waterlogged.
- **Messages in a Bottle:** 1.5% of rod catches plus pots, chests and trades. Each reads one of 12 sea notes and gives a treasure or a "Bottled Map to a Wreck" (a filled map, not a separate item id).

**Fit:** cheap exploration content with lore hooks (the notes, the named keepers). No overlaps.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `fisherman_house`
- Items (6): `fisherman_house:chum`, `fisherman_house:crab_pot`, `fisherman_house:fish_bait`, `fisherman_house:fishing_net`, `fisherman_house:glow_bait`, `fisherman_house:message_in_a_bottle`
- Blocks (2): `fisherman_house:crab_pot`, `fisherman_house:fishing_net`
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): `fisherman_house:fisherman_house`, `fisherman_house:harbour_pier`, `fisherman_house:ice_fishing_camp`, `fisherman_house:lighthouse`, `fisherman_house:river_boathouse`, `fisherman_house:stilt_shack`, `fisherman_house:sunken_trawler`
- Advancements (12): `fisherman_house:all_structures` (Coastal Wanderer), `fisherman_house:buy_crab_pot` (Tools of the Trade), `fisherman_house:discover_fisherman_house` (Home of Saylor), `fisherman_house:discover_harbour_pier` (Land Ahoy), `fisherman_house:discover_ice_fishing_camp` (Cold Feet), `fisherman_house:discover_lighthouse` (Keeper of the Light), `fisherman_house:discover_river_boathouse` (Up the River), `fisherman_house:discover_stilt_shack` (Bayou Living), `fisherman_house:discover_sunken_trawler` (X Marks the Wreck), `fisherman_house:get_crab_pot` (Pot Luck), `fisherman_house:open_bottle` (Message Received), `fisherman_house:root` (Fisherman's Coast)
- Own tags: item: `#fisherman_house:raw_fish`; worldgen/biome: `#fisherman_house:crab_pot/frozen`, `#fisherman_house:crab_pot/ocean`, `#fisherman_house:crab_pot/river`, `#fisherman_house:crab_pot/swamp`, `#fisherman_house:has_structure/fisherman_house`, `#fisherman_house:has_structure/harbour_pier`, `#fisherman_house:has_structure/ice_fishing_camp`, `#fisherman_house:has_structure/lighthouse`, `#fisherman_house:has_structure/river_boathouse`, `#fisherman_house:has_structure/stilt_shack`, `#fisherman_house:has_structure/sunken_trawler`; worldgen/structure: `#fisherman_house:coastal`, `#fisherman_house:on_bottle_maps`
- Sounds: 0 · Loot tables: 21 · Recipes: 5
- Config files: `config/fisherman_house.json`
- Lang copy: `modpack/research/registry/fisherman_house_en_us.json`

### 2.12 Remnants | Advanced Minimap & Waypoints (mod id `remnantminimaps`): include (client)

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `QCxt1U64` · `remnantminimaps-neoforge-1.21.1-2.0.0.jar` · 922,006 bytes · published 2026-10-22
  - url: https://cdn.modrinth.com/data/lLviL6Oq/versions/QCxt1U64/remnantminimaps-neoforge-1.21.1-2.0.0.jar
  - sha1 `3f7d897c19858aab1d5540541df0fc47717d5b51`
  - sha512 `ada331af90ddc3d9cbc9014b210b8051809280c405ac4f84dd9230c9f1033671fc0a200162d80cd528800af683342689897e53acc8e4a4527ee532643cc44812`
- **CurseForge:** project `1564458` (slug `remnants-minimap`) · newest 1.21.1 NeoForge file `9286028` `remnantminimaps-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.229,). Licence Apache-2.0. Side: **client**.

**What it does (2.0, a full rebuild of Odyssey Map; old waypoints don't carry over):** an Elden-Ring-style parchment minimap and world map.
- **Look:** relief and contour lines, engraved seas, ink outlines, and **fog over unexplored land**. Round gold-ring or square frame; rotating or north-up.
- **HUD readouts:** time of day ("Dawn, Early Day, Noon, Dusk…"), coordinates, biome, optional radar.
- **World map:** **M**.
- **Markers:**
  - 30 emblems, including Site of Grace, Waygate, Boss and Catacombs.
  - Ten hues, plus labels and pillars of light visible up to 2 048–16 384 m.
  - A **Bloodstain** is automatically placed where you die (last 3 kept), and a **Resting Place** at your last bed.
  - The Grace list (G in the map screen) has search and 9 filters.
- Settings use a soulslike options screen. Data is kept per world/server in `remnantminimaps/`.

**Fit:** perfect visual fit and client-only. It replaces Xaero's Minimap/World Map or JourneyMap; don't ship both. It has no integration with the Eclipsed Realm graces or Runeborn shrines (markers are manual), but bloodstains pair naturally with Runeborn's rune recovery. Rebind N and B (§4).

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `remnantminimaps`
- Items (0): _none_
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Keybinds (default; b = read from bytecode, p = mod page): `key.remnantminimaps.open_map` Open World Map = **M (p)**; `key.remnantminimaps.toggle_minimap` Show / Hide Minimap = **N (p)**; `key.remnantminimaps.zoom_in` Minimap Zoom In = **= (p)**; `key.remnantminimaps.zoom_out` Minimap Zoom Out = **- (p)**; `key.remnantminimaps.add_marker` Place Marker Here = **B (p)**; `key.remnantminimaps.toggle_rotation` Toggle Minimap Rotation = **unbound (p)**; `key.remnantminimaps.settings` Minimap Settings = **unbound (p)**
- Config files: `config/remnantminimaps.json`, `remnantminimaps/worlds/<world>/ (map tiles .rmr + markers.json)`
- Lang copy: `modpack/research/registry/remnantminimaps_en_us.json`

### 2.13 Smart Villagers AI (mod id `smartvillagers`): optional

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `bGNaqTaL` · `smartvillagers-neoforge-1.21.1-2.0.0.jar` · 285,498 bytes · published 2026-10-25
  - url: https://cdn.modrinth.com/data/l9oZCCPS/versions/bGNaqTaL/smartvillagers-neoforge-1.21.1-2.0.0.jar
  - sha1 `f9a901f1f3e93d2ec68233d5637d3039bacbbcf7`
  - sha512 `196e5da485353e84d1f316bac60be9aded75eef3483d9d16e40daf9db4e4611ef6a08ac2bfc502b60e3874e3531cd90506dd14325ccd0c1309e526902af0710d`
- **CurseForge:** project `1567718` (slug `smart-villagers-ai`) · newest 1.21.1 NeoForge file `9319343` `smartvillagers-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional `simple-voice-chat`. Modrinth lists: simple-voice-chat (optional). `neoforge.mods.toml` declares: voicechat optional [0,). NeoForge [21.1.80,). Licence Apache-2.0. Side: **server**.

**What it does (2.0 "The Village Square Update"):**
- Villagers answer chat in speech bubbles, written by an OpenAI-compatible LLM (DeepSeek, OpenAI, OpenRouter, NanoGPT, Ollama, LM Studio, custom) or by built-in dialogue when no provider is set.
- **Village requests:** fetch tasks by profession, or slay tasks against zombies, skeletons, spiders, creepers and pillagers. Rewards are emeralds and XP, plus vanilla positive gossip toward a better reputation.
- Standing levels: stranger, friend, hero, wary, hostile. Gossip spreads within 48 blocks.
- Per-player AI consent (`/villagerai consent accept`). Optional Simple Voice Chat speech.
- Advancements: `smartvillagers:root`, `first_request` (A Favor for a Friend), `village_hero` (Hero of the Village Square).

**Fit:** good filler side-quests. The risk is that AI-improvised lore contradicts the authored story, and it needs API keys and privacy consent. If included, run it with no provider (built-in dialogue) or with locked personas. It runs server-side only.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `smartvillagers`
- Items (0): _none_
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements (3): `smartvillagers:first_request` (A Favor for a Friend), `smartvillagers:root` (Smart Villagers), `smartvillagers:village_hero` (Hero of the Village Square)
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Config files: `config/smartvillagers/config.toml`, `secrets.toml, consent.json, ledger.json (names from jar strings)`
- Lang copy: `modpack/research/registry/smartvillagers_en_us.json`

### 2.14 RE:Constructed Wands (mod id `reconstructedwands`): optional

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `DySmVFHw` · `reconstructedwands-neoforge-1.21.1-2.0.0.jar` · 251,893 bytes · published 2026-10-24
  - url: https://cdn.modrinth.com/data/zj6ZBpmY/versions/DySmVFHw/reconstructedwands-neoforge-1.21.1-2.0.0.jar
  - sha1 `f83e8df69ec96dc7b47a4048a5ab651642b11105`
  - sha512 `a5014e4a4f720e0851cb63a6177091ded2315a8bef3983fe45826c36fda5dfb6bc0db49576b7cc23f855b66910b2d603f4810fe8cc9bb9455673a914ad1a45b7`
- **CurseForge:** project `1425382` (slug `re-constructed-wands`) · newest 1.21.1 NeoForge file `9311333` `reconstructedwands-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does (2.0):**
- **Wands:** Stone, Iron, Diamond, Netherite and Infinity.
- **Base mode:** extends a clicked face.
- **Cores**, installed by crafting:
  - **Angel**: mid-air placement.
  - **Destruction**: surface removal with offhand-tool drops.
  - **Exchange**: swaps a surface.
  - **Architect**: line, wall, floor, box, cube, circle and ring between two clicks.
- **Controls:** a live preview, undo/redo (Ctrl+Z / Ctrl+Y), Ctrl+scroll for size, Sneak+scroll to lock direction.
- **Block sources:** shulkers, bundles, Ender Chest and a bound chest.
- **Safety:** claims are respected; deny tags `#reconstructedwands:denied` and `#reconstructedwands:no_dismantle`.

**Fit:** off-theme QoL, harmless if the pack values building. Default R (wheel), G (screen) and Z/Y collide with Runeborn, Fellowship, Roguelite and Skills and Powers; rebind.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `reconstructedwands`
- Items (9): `reconstructedwands:core_angel`, `reconstructedwands:core_architect`, `reconstructedwands:core_destruction`, `reconstructedwands:core_exchange`, `reconstructedwands:diamond_wand`, `reconstructedwands:infinity_wand`, `reconstructedwands:iron_wand`, `reconstructedwands:netherite_wand`, `reconstructedwands:stone_wand`
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Own tags: block: `#reconstructedwands:denied`, `#reconstructedwands:no_dismantle`
- Sounds: 0 · Loot tables: 0 · Recipes: 10
- Keybinds (default; b = read from bytecode, p = mod page): `key.reconstructedwands.wheel` Mode wheel (hold) = **R (b)**; `key.reconstructedwands.screen` Wand settings = **G (b)**; `key.reconstructedwands.undo` Undo (with Ctrl) = **Z (b)**; `key.reconstructedwands.redo` Redo (with Ctrl) = **Y (b)**
- Config files: `config/reconstructedwands/server.json`, `config/reconstructedwands/client.json`
- Lang copy: `modpack/research/registry/reconstructedwands_en_us.json`

### 2.15 Better Farming ++ (mod id `better_farming_plus`): optional

- **Modrinth** (NeoForge 1.21.1, newest release): `1.0.0+neoforge-1.21.1` · version id `Tnsm7vVi` · `better_farming_plus-neoforge-1.21.1-1.0.0.jar` · 352,705 bytes · published 2026-10-25
  - url: https://cdn.modrinth.com/data/cYvmbMbJ/versions/Tnsm7vVi/better_farming_plus-neoforge-1.21.1-1.0.0.jar
  - sha1 `7d6df4fad37bd49b5184d5d7d45f537c5a08746e`
  - sha512 `1ed907d0d81fd0955cf9b202fe2862e2831f5e87440bab3db376a71c11c6d9a0742f53cb7a33622e6c0d549e6bfae6b4478a6910c2f8d68b194ab7ee566cf560`
- **CurseForge:** project `1255531` (slug `better-farming`) · newest 1.21.1 NeoForge file `9319765` `better_farming_plus-neoforge-1.21.1-1.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.219,). Licence Apache-2.0. Side: **both**.

**What it does (1.0; JaUML no longer needed):**
- Right-click harvest and replant (the replant costs a seed from the drops).
- **Hoe sweeps:** iron or gold 3×3, diamond 5×5, netherite 7×7.
- **Sprinkler:** hydrates 9×9 and gives about 3× growth ticks; needs water within 4 blocks below or adjacent.
- **Farming Crate:** harvests, replants and stores a 9×9 area; never voids items.
- No trampling, and a built-in "Harvest Indicators" resource pack.
- Block tags `#better_farming_plus:harvestable`, `not_harvestable`, `sprinkler_boosted`.

**Answer to the brief:** it does **not** overlap Sprout & Soil functionally (automation vs crops). Sprout & Soil's crops are plain blocks, so Better Farming would not even harvest them unless they were tagged.

**Overlaps:** Farmer's Delight only in right-click harvesting of vanilla-type crops. Tag any FD crop that misbehaves `not_harvestable`.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `better_farming_plus`
- Items (2): `better_farming_plus:farming_crate`, `better_farming_plus:sprinkler`
- Blocks (2): `better_farming_plus:farming_crate`, `better_farming_plus:sprinkler`
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Own tags: block: `#better_farming_plus:harvestable`, `#better_farming_plus:not_harvestable`, `#better_farming_plus:sprinkler_boosted`
- Sounds: 0 · Loot tables: 2 · Recipes: 2
- Config files: `config/better_farming_plus.json (migrates config/betterfarming/global.json)`
- Lang copy: `modpack/research/registry/better_farming_plus_en_us.json`

### 2.16 Sprout & Soil (mod id `sprout_and_soil`): exclude

- **Modrinth** (NeoForge 1.21.1, newest release): `0.3.0+neoforge-1.21.1` · version id `Wqyz45b4` · `sprout_and_soil-neoforge-1.21.1-0.3.0.jar` · 67,689 bytes · published 2026-09-14
  - url: https://cdn.modrinth.com/data/nZVwZSoj/versions/Wqyz45b4/sprout_and_soil-neoforge-1.21.1-0.3.0.jar
  - sha1 `8f0e8920a00ad87f0a5f9f517d06219626b1d0ea`
  - sha512 `7152a8384cd727b41fb7f66c5308df28640d7f301dbe22736b60aaa22169dae71159acfdb03f3cdf6fb7da1343304f577471dba76fe44d309cdfc4d60b299d24`
- **CurseForge:** project `1386319` (slug `sprout-and-soil`) · newest 1.21.1 NeoForge file `8879085` `sprout_and_soil-neoforge-1.21.1-0.3.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does:** adds tomato (8 stages), garlic and "letuce" (sic, 4 stages each), plus tomato seeds. The page's "foods & recipes" do not exist in the jar.

**Why exclude:**
- On 1.21.1 its loot tables (`data/sprout_and_soil/loot_tables/blocks/*`) and its only recipe (`data/sprout_and_soil/recipes/seed_recipe.json`) are in pre-1.21 folders and **do not load**, so crops drop nothing.
- No garlic or lettuce seed exists.
- Its tags live in a stray `crops:` namespace.
- Its Modrinth page still says "1.20.1, requires JAUML".
- Farmer's Delight already covers tomatoes.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `sprout_and_soil`
- Items (20): `sprout_and_soil:garlic`, `sprout_and_soil:garlic_plant_stage_0`, `sprout_and_soil:garlic_plant_stage_1`, `sprout_and_soil:garlic_plant_stage_2`, `sprout_and_soil:garlic_plant_stage_3`, `sprout_and_soil:letuce`, `sprout_and_soil:letuce_plant_stage_0`, `sprout_and_soil:letuce_plant_stage_1`, `sprout_and_soil:letuce_plant_stage_2`, `sprout_and_soil:letuce_plant_stage_3`, `sprout_and_soil:tomato`, `sprout_and_soil:tomato_plant_stage_0`, `sprout_and_soil:tomato_plant_stage_1`, `sprout_and_soil:tomato_plant_stage_2`, `sprout_and_soil:tomato_plant_stage_3`, `sprout_and_soil:tomato_plant_stage_4`, `sprout_and_soil:tomato_plant_stage_5`, `sprout_and_soil:tomato_plant_stage_6`, `sprout_and_soil:tomato_plant_stage_7`, `sprout_and_soil:tomato_seeds`
- Blocks (16): `sprout_and_soil:garlic_plant_stage_0`, `sprout_and_soil:garlic_plant_stage_1`, `sprout_and_soil:garlic_plant_stage_2`, `sprout_and_soil:garlic_plant_stage_3`, `sprout_and_soil:letuce_plant_stage_0`, `sprout_and_soil:letuce_plant_stage_1`, `sprout_and_soil:letuce_plant_stage_2`, `sprout_and_soil:letuce_plant_stage_3`, `sprout_and_soil:tomato_plant_stage_0`, `sprout_and_soil:tomato_plant_stage_1`, `sprout_and_soil:tomato_plant_stage_2`, `sprout_and_soil:tomato_plant_stage_3`, `sprout_and_soil:tomato_plant_stage_4`, `sprout_and_soil:tomato_plant_stage_5`, `sprout_and_soil:tomato_plant_stage_6`, `sprout_and_soil:tomato_plant_stage_7`
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Own tags: block: `#crops:farmland`; item: `#crops:fertilizer`
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Lang copy: `modpack/research/registry/sprout_and_soil_en_us.json`

### 2.17 The Witch Hut (mod id `better_witch_huts`): optional (low priority)

- **Modrinth** (NeoForge 1.21.1, newest release): `1.0.0` · version id `3dxLP8EC` · `better_witch_huts-1.0.0-neoforge-1.21.1.jar` · 17,809 bytes · published 2025-12-01
  - url: https://cdn.modrinth.com/data/xcgCWpcP/versions/3dxLP8EC/better_witch_huts-1.0.0-neoforge-1.21.1.jar
  - sha1 `f5baec869ceb8c889b647b3ff3d9a9a0f4dab4c1`
  - sha512 `119821dbe59a3f777ae47d1be12ccbfe51071956cb06fcd1b341ca3d79f9eda149445b9060ca555cf715ab1f1bf1176a016dc64f89c33cc7fc4df6485fa5f9a3`
- **CurseForge:** project `1393188` (slug `the-witch-hut`) · newest 1.21.1 NeoForge file `7279422` `better_witch_huts-1.0.0-neoforge-1.21.1.jar` (release)
- **Dependencies:** required `jauml`; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: jauml required [1.1.0,); jauml required [1.1.0,); jauml required [1.1.0,); jauml required [1.1.0,). NeoForge [21.1.176,). Licence Apache-2.0. Side: **both**.

**What it does:** adds **one new jigsaw structure**, `better_witch_huts:witch_hut` (24×14×23), in swamp, dark forest and **plains**. Spacing is 150 and separation 100.
- It contains a `minecraft:witch` spawner, cauldrons, 5 barrels and a chest. The only filled container holds 11 iron nuggets, 9 iron ingots and 2 emeralds; there are no loot tables.
- It does **not** replace or modify the vanilla `minecraft:swamp_hut`.
- The "hostile, neutral and trader witches", "random magical loot" and "secret compartments" on the mod page are **not in the jar**. Its lang file is empty.
- Requires jauml.

**Fit:** a small atmospheric set piece at best. YUNG's Better Witch Huts (which *replaces* the vanilla hut) is richer; both can coexist, but you'd get two kinds of witch hut.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `better_witch_huts`
- Items (0): _none_
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): `better_witch_huts:witch_hut`
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Lang copy: `modpack/research/registry/better_witch_huts_en_us.json`

### 2.18 The Gingerbread House (mod id `christmas_ginger_house`): exclude

- **Modrinth** (NeoForge 1.21.1, newest release): `1.0.0` · version id `aEQ294YN` · `christmas_ginger_house-1.0.0-neoforge-1.21.1.jar` · 21,811 bytes · published 2026-01-07
  - url: https://cdn.modrinth.com/data/Ddgd2w2n/versions/aEQ294YN/christmas_ginger_house-1.0.0-neoforge-1.21.1.jar
  - sha1 `c62d3549a9e2ab7093e5a8a996dec4220c601cdc`
  - sha512 `39cdcd1e23127451ac72ff9a2994f803eccb3f2922ba57e79a7e007d9da8c5964984d93ab563c3f66c917fd58f076cea9c015be4cf6e5d443392434dda6b9ea8`
- **CurseForge:** project `1409805` (slug `the-gingerbread-house`) · newest 1.21.1 NeoForge file `7374514` `christmas_ginger_house-1.0.0-neoforge-1.21.1.jar` (release)
- **Dependencies:** required `jauml`; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: jauml required [1.1.0,); jauml required [1.1.0,); jauml required [1.1.0,); jauml required [1.1.0,); jauml required [1.1.0,); jauml required [1.1.0,). NeoForge [21.1.176,). Licence Apache-2.0. Side: **both**.

**What it does:** one 42×16×40 candy-house structure, `christmas_ginger_house:christmas_ginger_house`, in snowy slopes, plains, snowy plains and snowy taiga.
- Its 10 barrels hold fixed vanilla items (bread, snowballs, potatoes, beetroot seeds, coal…).
- No loot tables, entities or custom items. The candy canes and cookies on the page are not in the jar.
- Requires jauml.

**Why exclude:** tone-breaking festive content in a dark-fantasy pack.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `christmas_ginger_house`
- Items (0): _none_
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): `christmas_ginger_house:christmas_ginger_house`
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Lang copy: `modpack/research/registry/christmas_ginger_house_en_us.json`

### 2.19 Genetically Modified Monsters (mod id `gmm`): exclude

- **Modrinth** (NeoForge 1.21.1, newest release): `1.0.0+neoforge-1.21.1` · version id `B2tTlGwb` · `gmm-neoforge-1.21.1-1.0.0.jar` · 56,255 bytes · published 2026-09-14
  - url: https://cdn.modrinth.com/data/56wxSt5P/versions/B2tTlGwb/gmm-neoforge-1.21.1-1.0.0.jar
  - sha1 `6325d3d46b15a2636b452650cda12d3910fb6c18`
  - sha512 `b908e8ded4dbc094f5f42e45a169f6080aee74d7ccb2ee0f8a27f4d8cbe690a8d9286768068bb4ecaeda8cb71a1f341d11ee29a5b03e6bd752d2ae08e94436d0`
- **CurseForge:** project `1390363` (slug `genetically-modified-monsters`) · newest 1.21.1 NeoForge file `8879894` `gmm-neoforge-1.21.1-1.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does:** 7 red mutant creepers added by biome modifier: Leap, Climb, Hunter (target lock), Adaptive (dodges), Silent, Swift, and Overcharge (up to 2× a charged-creeper blast). There are no loot tables and no items besides spawn eggs, which have no item models.

**Why exclude:**
- The "lab-engineered" sci-fi flavour doesn't fit.
- Extra terrain-griefing explosions.
- RPG Mobs traits (Volatile, Swift, Blinking…) already add creeper variety.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `gmm`
- Items (7): `gmm:adaptive_creeper_spawn_egg`, `gmm:climb_creeper_spawn_egg`, `gmm:hunter_creeper_spawn_egg`, `gmm:leap_creeper_spawn_egg`, `gmm:overcharge_creeper_spawn_egg`, `gmm:silent_creeper_spawn_egg`, `gmm:swift_creeper_spawn_egg`
- Blocks (0): _none_
- Entities (7): `gmm:adaptive_creeper`, `gmm:climb_creeper`, `gmm:hunter_creeper`, `gmm:leap_creeper`, `gmm:overcharge_creeper`, `gmm:silent_creeper`, `gmm:swift_creeper`
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Lang copy: `modpack/research/registry/gmm_en_us.json`

### 2.20 Chronofall (mod id `chronofall`, formerly Robotica / The Year 3001): exclude

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+neoforge-1.21.1` · version id `zcl3NWYX` · `chronofall-neoforge-1.21.1-2.0.0.jar` · 1,002,159 bytes · published 2026-10-26
  - url: https://cdn.modrinth.com/data/kVfzGwSI/versions/zcl3NWYX/chronofall-neoforge-1.21.1-2.0.0.jar
  - sha1 `21cb2522c3eb085a9db071f74832bcd5a222cc27`
  - sha512 `c182425af3a8dae80c8ffac406cdae91708260c415b7cd9e3b81385941da5d15c3748a635bd3b99498aa8399aa08e20ca967d7685a48a5543f863f0aca72023c`
- **CurseForge:** project `1353400` (slug `chronofall`) · newest 1.21.1 NeoForge file `9330767` `chronofall-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.219,). Licence Apache-2.0. Side: **both**.

**What it does (2.0):**
- **Chrono Rifts** at night (4% per player-minute): a Chrono Pod crashes, guarded by laser **Sentinels**, around a **Rift Cache** of salvage.
- A **Fabricator** with holograms, cable-free **Flux** and a Flux Charger.
- Gear: **Jetpack**, **Hover Skiff**, **Drone** (Collector/Guard/Lamp chips), rideable **Mech** with upgrade cards, Plasma Cutter, Pulse Rifle.
- **Rift Gates**, linked with a Rift Tuner, teleport across dimensions.
- Ores and tiers: titanium, cobalt, orichalcum and scrap.

**Why exclude:** year-3001 sci-fi breaks the tone. Flight and cross-dimension gates trivialise exploration and the Realm's Waygate/grace travel.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `chronofall`
- Items (82): `chronofall:blank_card`, `chronofall:blank_printed_circuit_board`, `chronofall:bulk_upgrade_card`, `chronofall:central_processing_unit`, `chronofall:cobalt_armor_boots`, `chronofall:cobalt_armor_chestplate`, `chronofall:cobalt_armor_helmet`, `chronofall:cobalt_armor_leggings`, `chronofall:cobalt_axe`, `chronofall:cobalt_block`, `chronofall:cobalt_hoe`, `chronofall:cobalt_ingot`, `chronofall:cobalt_ore`, `chronofall:cobalt_pickaxe`, `chronofall:cobalt_shovel`, `chronofall:cobalt_sword`, `chronofall:collector_chip`, `chronofall:damage_upgrade_card`, `chronofall:defense_upgrade_card`, `chronofall:drone`, `chronofall:electrical_conductors`, `chronofall:fabricator`, `chronofall:flux_cell`, `chronofall:flux_charger`, `chronofall:guard_chip`, `chronofall:jetpack`, `chronofall:lamp_chip`, `chronofall:mech`, `chronofall:orichalcum_armor_boots`, `chronofall:orichalcum_armor_chestplate`, `chronofall:orichalcum_armor_helmet`, `chronofall:orichalcum_armor_leggings`, `chronofall:orichalcum_axe`, `chronofall:orichalcum_block`, `chronofall:orichalcum_hoe`, `chronofall:orichalcum_ingot`, `chronofall:orichalcum_ore`, `chronofall:orichalcum_pickaxe`, `chronofall:orichalcum_shovel`, `chronofall:orichalcum_sword`, `chronofall:plasma_cutter`, `chronofall:printed_circuit_board`, `chronofall:pulse_rifle`, `chronofall:raw_cobalt`, `chronofall:raw_orichalcum`, `chronofall:raw_titanium`, `chronofall:repair_card`, `chronofall:rift_beacon`, `chronofall:rift_cache`, `chronofall:rift_gate`, `chronofall:rift_glass`, `chronofall:rift_shard`, `chronofall:rift_tuner`, `chronofall:scrap`, `chronofall:scrap_armor_boots`, `chronofall:scrap_armor_chestplate`, `chronofall:scrap_armor_helmet`, `chronofall:scrap_armor_leggings`, `chronofall:scrap_axe`, `chronofall:scrap_block`, `chronofall:scrap_debris`, `chronofall:scrap_hoe`, `chronofall:scrap_pickaxe`, `chronofall:scrap_shovel`, `chronofall:scrap_slab`, `chronofall:scrap_stairs_block`, `chronofall:scrap_sword`, `chronofall:sentinel_spawn_egg`, `chronofall:skiff`, `chronofall:speed_upgrade_card`, `chronofall:titanium_armor_boots`, `chronofall:titanium_armor_chestplate`, `chronofall:titanium_armor_helmet`, `chronofall:titanium_armor_leggings`, `chronofall:titanium_axe`, `chronofall:titanium_block`, `chronofall:titanium_hoe`, `chronofall:titanium_ingot`, `chronofall:titanium_ore`, `chronofall:titanium_pickaxe`, `chronofall:titanium_shovel`, `chronofall:titanium_sword`
- Blocks (16): `chronofall:cobalt_block`, `chronofall:cobalt_ore`, `chronofall:fabricator`, `chronofall:flux_charger`, `chronofall:orichalcum_block`, `chronofall:orichalcum_ore`, `chronofall:rift_beacon`, `chronofall:rift_cache`, `chronofall:rift_gate`, `chronofall:rift_glass`, `chronofall:scrap_block`, `chronofall:scrap_debris`, `chronofall:scrap_slab`, `chronofall:scrap_stairs_block`, `chronofall:titanium_block`, `chronofall:titanium_ore`
- Entities (6): `chronofall:chrono_pod`, `chronofall:drone`, `chronofall:laser_bolt`, `chronofall:mech`, `chronofall:sentinel`, `chronofall:skiff`
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Own tags: item: `#chronofall:repairs_cobalt_armor`, `#chronofall:repairs_jetpack`, `#chronofall:repairs_orichalcum_armor`, `#chronofall:repairs_scrap_armor`, `#chronofall:repairs_titanium_armor`
- Sounds: 21 · Loot tables: 16 · Recipes: 66
- Config files: `config/chronofall.json`
- Lang copy: `modpack/research/registry/chronofall_en_us.json`

### 2.21 Remnants | Ballistics (mod id `remnants_ballistics`, CurseForge only): exclude

- **Modrinth:** not published there.
- **CurseForge:** project `1759493` (slug `remnants-ballistics`) · newest 1.21.1 NeoForge file `9296773` `remnants_ballistics-neoforge-1.21.1-0.4.0.jar` (beta) · 3,716,878 bytes · sha1 (computed locally) `952a63de4e5a533484d0e0dead837af510f5a6d1`
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.264,). Licence Apache-2.0 (per CurseForge description). Side: **both**.

**What it does (0.4.0 beta; page text describes 0.3.0 "First Shots"):**
- **16 firearms:**
  - pistols: R-9 Sidearm, Ironfang .50, Warden .357
  - SMGs: Viper-9, Spectre PDW
  - rifles: ARX-16, Raven AK, Mantis BR
  - shotguns: Breacher-12, Thunderpump
  - snipers: Ghostline M24, Longshot .50
  - LMGs: Titan-56, Bulwark-762
  - experimental: Voidcaster, Eclipse Railgun
- 9 ammo types, plus a Gunsmith Workbench (6 attachment slots) and an Ammunition Press.
- Blueprints (Advanced, Prototype); top tiers need Remnant Alloy and Void Cores.
- Server-authoritative hitscan with lag compensation, penetration and ricochet.
- Loot injected into 25 vanilla tables; pillagers, vindicators and brutes drop ammo.

**Why exclude:** modern guns are tone-breaking for a soulslike. It is a beta, CurseForge-only (no Modrinth hash for `.mrpack`), needs NeoForge 21.1.264+, and binds R/V/I.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `remnants_ballistics`
- Items (62): `remnants_ballistics:ammo_12g`, `remnants_ballistics:ammo_308`, `remnants_ballistics:ammo_50bmg`, `remnants_ballistics:ammo_556`, `remnants_ballistics:ammo_57`, `remnants_ballistics:ammo_762`, `remnants_ballistics:ammo_9mm`, `remnants_ballistics:ammo_magnum`, `remnants_ballistics:ammo_press`, `remnants_ballistics:angled_grip`, `remnants_ballistics:arx_16`, `remnants_ballistics:blueprint_advanced`, `remnants_ballistics:blueprint_prototype`, `remnants_ballistics:brass_ingot`, `remnants_ballistics:breacher_12`, `remnants_ballistics:bulwark_762`, `remnants_ballistics:casing`, `remnants_ballistics:compensator`, `remnants_ballistics:drum_mag`, `remnants_ballistics:eclipse_railgun`, `remnants_ballistics:energy_cell`, `remnants_ballistics:extended_mag`, `remnants_ballistics:flash_hider`, `remnants_ballistics:ghostline_m24`, `remnants_ballistics:gun_parts`, `remnants_ballistics:gunsmith_workbench`, `remnants_ballistics:heavy_stock`, `remnants_ballistics:holo_reflex`, `remnants_ballistics:ironfang_50`, `remnants_ballistics:light_stock`, `remnants_ballistics:longeye_scope`, `remnants_ballistics:longshot_50`, `remnants_ballistics:mantis_br`, `remnants_ballistics:muzzle_brake`, `remnants_ballistics:polymer_sheet`, `remnants_ballistics:precision_parts`, `remnants_ballistics:quick_mag`, `remnants_ballistics:r9_sidearm`, `remnants_ballistics:ranger_scope`, `remnants_ballistics:raven_ak`, `remnants_ballistics:remnant_alloy`, `remnants_ballistics:repair_kit`, `remnants_ballistics:shotgun_choke`, `remnants_ballistics:shotgun_hull`, `remnants_ballistics:skin_arctic`, `remnants_ballistics:skin_crimson`, `remnants_ballistics:skin_desert`, `remnants_ballistics:skin_gilded`, `remnants_ballistics:skin_void`, `remnants_ballistics:spectre_pdw`, `remnants_ballistics:steel_ingot`, `remnants_ballistics:stubby_grip`, `remnants_ballistics:suppressor`, `remnants_ballistics:tactical_stock`, `remnants_ballistics:thunderpump`, `remnants_ballistics:titan_56`, `remnants_ballistics:tripoint_holo`, `remnants_ballistics:vertical_grip`, `remnants_ballistics:viper_9`, `remnants_ballistics:void_core`, `remnants_ballistics:voidcaster`, `remnants_ballistics:warden_357`
- Blocks (2): `remnants_ballistics:ammo_press`, `remnants_ballistics:gunsmith_workbench`
- Entities (1): `remnants_ballistics:void_orb`
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements (12): `remnants_ballistics:ammo_press` (Rolling Your Own), `remnants_ballistics:attachment` (Tactical Upgrade), `remnants_ballistics:blueprint` (Classified Schematics), `remnants_ballistics:first_blood` (First Blood), `remnants_ballistics:first_weapon` (Locked and Loaded), `remnants_ballistics:gunsmith` (Bench Rest), `remnants_ballistics:headshot` (Between the Eyes), `remnants_ballistics:legendary` (Legendary Arsenal), `remnants_ballistics:long_shot` (Ghost in the Line), `remnants_ballistics:prototype` (Prototype Program), `remnants_ballistics:root` (Remnants: Ballistics), `remnants_ballistics:void` (Stare Into the Void)
- Own tags: block: `#remnants_ballistics:bullet_breakable`, `#remnants_ballistics:bullet_penetrable`, `#remnants_ballistics:impact/glass`, `#remnants_ballistics:impact/metal`, `#remnants_ballistics:impact/soft`, `#remnants_ballistics:impact/wood`; damage_type: `#remnants_ballistics:bullets`, `#remnants_ballistics:headshot`; entity_type: `#remnants_ballistics:humanoid_hit_zones`; item: `#remnants_ballistics:ammo`, `#remnants_ballistics:attachments`, `#remnants_ballistics:legendary_weapons`, `#remnants_ballistics:weapons`
- Damage types: `remnants_ballistics:bullet`, `remnants_ballistics:bullet_headshot`, `remnants_ballistics:energy`
- Sounds: 59 · Loot tables: 15 · Recipes: 63
- Keybinds (default; b = read from bytecode, p = mod page): `key.remnants_ballistics.reload` Reload = **R (b)**; `key.remnants_ballistics.fire_mode` Switch Fire Mode = **V (b)**; `key.remnants_ballistics.inspect` Inspect Weapon = **I (b)**
- Config files: `NeoForge config specs (client/common/server); exact file names not visible in the jar`
- Lang copy: `modpack/research/registry/remnants_ballistics_en_us.json`

### 2.22 Core Utilities (mod id `core_utilities`): exclude

- **Modrinth** (NeoForge 1.21.1, newest release): `2.0.0+1.21.1-neoforge` · version id `GGsdWgaL` · `core_utilities-neoforge-1.21.1-2.0.0.jar` · 1,055,694 bytes · published 2026-10-27
  - url: https://cdn.modrinth.com/data/uy92hxqE/versions/GGsdWgaL/core_utilities-neoforge-1.21.1-2.0.0.jar
  - sha1 `7e0551bccced09bd8a67c98a3f00ad8e371a0b9c`
  - sha512 `be7b4836424d16fa4845d495a2bd1f86362b1dcb42729e0677b5910b5fe041f3179bbe405f0b7e8da9f81bfb1448eb79eeec9a0336a497afff8f272eae99b883`
- **CurseForge:** project `1379111` (slug `core-utilities`) · newest 1.21.1 NeoForge file `9343421` `core_utilities-neoforge-1.21.1-2.0.0.jar` (release)
- **Dependencies:** required _none_; optional `jei`, `jade`. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does (2.0 "The Technology Update"):**
- **Power:** FE generators (solar T1–T4, combustion, geothermal), energy cells and 3 cable tiers.
- **Processing:** Crusher, Alloy Smelter (Steel, Energized, Ender Alloy), Compressor, Electric Furnace.
- **Machines:** Quarry, Crop Harvester, Mob Grinder, Block Breaker/Placer, item pipes, upgrades, wrench, multimeter.
- **Legacy content:** vector/effect plates, entity filters, backpacks, Mob Net, Floating Block, and the in-game manual.
- Its lang file still has legacy `block.fe_system.*` keys, and the registry still contains 1.x cable shapes (`cable_e`, `cable_x` …) kept for world conversion.

**Why exclude:** off-theme tech. The Quarry and Mob Grinder undercut exploration and the kill-reward loop of RPG Mobs, Runeborn and Loot Bags.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `core_utilities`
- Items (109): `core_utilities:advanced_circuit`, `core_utilities:advanced_machine_frame`, `core_utilities:alloy_smelter`, `core_utilities:basic_circuit`, `core_utilities:basic_machine_frame`, `core_utilities:big_backpack`, `core_utilities:blank_plate`, `core_utilities:block_breaker`, `core_utilities:block_placer`, `core_utilities:cable`, `core_utilities:cable_advanced`, `core_utilities:cable_e`, `core_utilities:cable_elite`, `core_utilities:cable_f`, `core_utilities:cable_i`, `core_utilities:cable_l`, `core_utilities:cable_lc`, `core_utilities:cable_lcc`, `core_utilities:cable_lt`, `core_utilities:cable_ltc`, `core_utilities:cable_s`, `core_utilities:cable_t`, `core_utilities:cable_tc`, `core_utilities:cable_tx`, `core_utilities:cable_txc`, `core_utilities:cable_txcc`, `core_utilities:cable_x`, `core_utilities:cable_xc`, `core_utilities:coal_dust`, `core_utilities:combustion_generator`, `core_utilities:compressor`, `core_utilities:configuration_wrench`, `core_utilities:copper_dust`, `core_utilities:copper_plate`, `core_utilities:crop_harvester`, `core_utilities:crusher`, `core_utilities:deny_filter_animal`, `core_utilities:deny_filter_pet`, `core_utilities:deny_filter_skeleton`, `core_utilities:deny_filter_spider`, `core_utilities:deny_filter_villager`, `core_utilities:deny_filter_zombie`, `core_utilities:deny_mob_filter`, `core_utilities:deny_neutral_filter`, `core_utilities:deny_player_filter`, `core_utilities:deny_projectile_filter`, `core_utilities:electric_furnace`, `core_utilities:elite_circuit`, `core_utilities:ender_alloy_ingot`, `core_utilities:energized_ingot`, `core_utilities:energy_cell_advanced`, `core_utilities:energy_cell_basic`, `core_utilities:energy_cell_creative`, `core_utilities:energy_cell_elite`, `core_utilities:energy_upgrade`, `core_utilities:filter_animal`, `core_utilities:filter_pet`, `core_utilities:filter_skeleton`, `core_utilities:filter_spider`, `core_utilities:filter_villager`, `core_utilities:filter_zombie`, `core_utilities:fire_res_plate`, `core_utilities:floating_block`, `core_utilities:geothermal_generator`, `core_utilities:gold_dust`, `core_utilities:gold_plate`, `core_utilities:guide_book`, `core_utilities:healing_plate`, `core_utilities:iron_dust`, `core_utilities:iron_plate`, `core_utilities:item_pipe`, `core_utilities:medium_backpack`, `core_utilities:mob_filter`, `core_utilities:mob_grinder`, `core_utilities:mob_net`, `core_utilities:multimeter`, `core_utilities:neutral_filter`, `core_utilities:player_filter`, `core_utilities:poison_plate`, `core_utilities:projectile_filter`, `core_utilities:quarry`, `core_utilities:range_upgrade`, `core_utilities:rapid_item_pipe`, `core_utilities:slowness_plate`, `core_utilities:small_backpack`, `core_utilities:solar_panel`, `core_utilities:solar_panel_1`, `core_utilities:solar_panel_2`, `core_utilities:solar_panel_tier_21`, `core_utilities:solar_panel_tier_22`, `core_utilities:solar_panel_tier_23`, `core_utilities:solar_panel_tier_31`, `core_utilities:solar_panel_tier_32`, `core_utilities:solar_panel_tier_33`, `core_utilities:solar_panel_tier_41`, `core_utilities:solar_panel_tier_42`, `core_utilities:solar_panel_tier_43`, `core_utilities:speed_plate`, `core_utilities:speed_upgrade`, `core_utilities:steel_block`, `core_utilities:steel_ingot`, `core_utilities:steel_plate`, `core_utilities:strength_plate`, `core_utilities:vector_plate_tier_1`, `core_utilities:vector_plate_tier_2`, `core_utilities:vector_plate_tier_3`, `core_utilities:vector_plate_tier_4`, `core_utilities:weakness_plate`, `core_utilities:wither_plate`
- Blocks (84): `core_utilities:advanced_machine_frame`, `core_utilities:alloy_smelter`, `core_utilities:basic_machine_frame`, `core_utilities:block_breaker`, `core_utilities:block_placer`, `core_utilities:cable`, `core_utilities:cable_advanced`, `core_utilities:cable_e`, `core_utilities:cable_elite`, `core_utilities:cable_f`, `core_utilities:cable_i`, `core_utilities:cable_l`, `core_utilities:cable_lc`, `core_utilities:cable_lcc`, `core_utilities:cable_lt`, `core_utilities:cable_ltc`, `core_utilities:cable_s`, `core_utilities:cable_t`, `core_utilities:cable_tc`, `core_utilities:cable_tx`, `core_utilities:cable_txc`, `core_utilities:cable_txcc`, `core_utilities:cable_x`, `core_utilities:cable_xc`, `core_utilities:combustion_generator`, `core_utilities:compressor`, `core_utilities:crop_harvester`, `core_utilities:crusher`, `core_utilities:deny_filter_animal`, `core_utilities:deny_filter_pet`, `core_utilities:deny_filter_skeleton`, `core_utilities:deny_filter_spider`, `core_utilities:deny_filter_villager`, `core_utilities:deny_filter_zombie`, `core_utilities:deny_mob_filter`, `core_utilities:deny_neutral_filter`, `core_utilities:deny_player_filter`, `core_utilities:deny_projectile_filter`, `core_utilities:electric_furnace`, `core_utilities:energy_cell_advanced`, `core_utilities:energy_cell_basic`, `core_utilities:energy_cell_creative`, `core_utilities:energy_cell_elite`, `core_utilities:filter_animal`, `core_utilities:filter_pet`, `core_utilities:filter_skeleton`, `core_utilities:filter_spider`, `core_utilities:filter_villager`, `core_utilities:filter_zombie`, `core_utilities:fire_res_plate`, `core_utilities:floating_block`, `core_utilities:geothermal_generator`, `core_utilities:healing_plate`, `core_utilities:item_pipe`, `core_utilities:mob_filter`, `core_utilities:mob_grinder`, `core_utilities:neutral_filter`, `core_utilities:player_filter`, `core_utilities:poison_plate`, `core_utilities:projectile_filter`, `core_utilities:quarry`, `core_utilities:rapid_item_pipe`, `core_utilities:slowness_plate`, `core_utilities:solar_panel`, `core_utilities:solar_panel_1`, `core_utilities:solar_panel_2`, `core_utilities:solar_panel_tier_21`, `core_utilities:solar_panel_tier_22`, `core_utilities:solar_panel_tier_23`, `core_utilities:solar_panel_tier_31`, `core_utilities:solar_panel_tier_32`, `core_utilities:solar_panel_tier_33`, `core_utilities:solar_panel_tier_41`, `core_utilities:solar_panel_tier_42`, `core_utilities:solar_panel_tier_43`, `core_utilities:speed_plate`, `core_utilities:steel_block`, `core_utilities:strength_plate`, `core_utilities:vector_plate_tier_1`, `core_utilities:vector_plate_tier_2`, `core_utilities:vector_plate_tier_3`, `core_utilities:vector_plate_tier_4`, `core_utilities:weakness_plate`, `core_utilities:wither_plate`
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Own tags: block: `#core_utilities:drill_machine`, `#core_utilities:drill_machine/non_breakable`; item: `#core_utilities:ingots/copper`, `#core_utilities:ingots/gold`, `#core_utilities:ingots/iron`, `#core_utilities:ores/coal`, `#core_utilities:ores/copper`, `#core_utilities:ores/diamond`, `#core_utilities:ores/emerald`, `#core_utilities:ores/gold`, `#core_utilities:ores/iron`, `#core_utilities:ores/lapis`, `#core_utilities:ores/quartz`, `#core_utilities:ores/redstone`, `#core_utilities:raw_materials/copper`, `#core_utilities:raw_materials/gold`, `#core_utilities:raw_materials/iron`, `#core_utilities:upgrades`
- Sounds: 0 · Loot tables: 84 · Recipes: 70
- Config files: `config/core_utilities.properties`
- Lang copy: `modpack/research/registry/core_utilities_en_us.json`

### 2.23 Simple Terminals (mod id `simple_terminals`): optional

- **Modrinth** (NeoForge 1.21.1, newest release): `1.1.1+neoforge-1.21.1` · version id `DpRrldoJ` · `simple-terminals-1.21.1-neoforge-1.1.1.jar` · 54,087 bytes · published 2026-10-06
  - url: https://cdn.modrinth.com/data/Ss3e4qjk/versions/DpRrldoJ/simple-terminals-1.21.1-neoforge-1.1.1.jar
  - sha1 `3fb21b00b6a5cb026f16a2714844a010695dd6ea`
  - sha512 `56fe737256577b9d97c56281762f28c6a2c7cbfcfee7518afa155718f1b4845aff26c3a0f46bd19042ae85596d4068e68b1fb5386c88bdb5f4f8161cd252a5a1`
- **CurseForge:** project `1528758` (slug `simple-terminals`) · newest 1.21.1 NeoForge file `9076436` `simple-terminals-1.21.1-neoforge-1.1.1.jar` (release)
- **Dependencies:** required _none_; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: none besides NeoForge/Minecraft. NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does:** one **Crafting Terminal** (`simple_terminals:crafting_terminal`; recipe: crafting table, redstone torch, chest, diamond). Attached to a chest, modded inventory or Sophisticated Storage controller, it gives a scrollable view with a built-in crafting grid.

**Fit:** neutral storage QoL. Keep only one terminal solution (skip it if AE2, RS or Sophisticated Storage terminals are in the pack).

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `simple_terminals`
- Items (1): `simple_terminals:crafting_terminal`
- Blocks (1): `simple_terminals:crafting_terminal`
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 1 · Recipes: 1
- Lang copy: `modpack/research/registry/simple_terminals_en_us.json`

### 2.24 No More 63 AE2 (mod id `no_more_63_ae2`): exclude (unless AE2 is in the pack)

- **Modrinth** (NeoForge 1.21.1, newest release): `0.1.3+neoforge-1.21.1` · version id `vyxgZAoW` · `no-more-63-ae2-1.21.1-neoforge-0.1.3.jar` · 11,559 bytes · published 2026-08-16
  - url: https://cdn.modrinth.com/data/ywtf09FK/versions/vyxgZAoW/no-more-63-ae2-1.21.1-neoforge-0.1.3.jar
  - sha1 `26ea0f96d43bca53410778a066a4cf4278089d4f`
  - sha512 `4e3ef0cec125e73407c6a58ac10e1dc311d65f43c9e359ab13ee157981a479173e523321f1eb10c4f1deacdce0810e9d25b96b7eb75805b933ec25a025ce24dd`
- **CurseForge:** project `1585209` (slug `no-more-63-ae2`) · newest 1.21.1 NeoForge file `8662349` `no-more-63-ae2-1.21.1-neoforge-0.1.3.jar` (release)
- **Dependencies:** required `ae2`; optional _none_. Modrinth lists: none listed. `neoforge.mods.toml` declares: ae2 required [19.2.17,20.0.0). NeoForge [21.1.80,). Licence Apache-2.0. Side: **both**.

**What it does:** mixins raise AE2's 63-unique-types-per-item-cell cap to a configurable `maxItemTypesPerCell` (e.g. 4096) in `config/no_more_63_ae2.toml`. Bytes, channels and autocrafting are untouched. It has no assets and no data.

**Fit:** irrelevant without AE2; optional if the pack ships AE2 19.2.17–19.x.

**Registry IDs** (from the jar, 2026-10-29; full lists also in `nightbeam_mods.json`):

- Mod id(s): `no_more_63_ae2`
- Items (0): _none_
- Blocks (0): _none_
- Entities (0): _none_
- Structures (worldgen, usable with `/locate structure`): _none_
- Advancements: _none_
- Sounds: 0 · Loot tables: 0 · Recipes: 0
- Config files: `config/no_more_63_ae2.toml (maxItemTypesPerCell)`

---

## 3. Overlap and conflict matrix

### 3.1 NightBeam × NightBeam (included and optional set)

Legend:
- **=** built-in integration
- **x** functional overlap or conflict that needs config
- **k** default keybind clash
- **~** thematic or name overlap only
- **·** none

| | RAS | Runeborn | RPG Mobs | Eclipsed | Roguelite | Skills&Powers | Fellowship | LootBags | MMD | Minimap | Wands |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **RAS** | | =x | = | · | = | = | = | · | · | · | · |
| **Runeborn** | =x | | x | ~ | k | xk | · | ~ | ~ | ~ | k |
| **RPG Mobs** | = | x | | = | = | · | = | ~ | ~ | · | · |
| **Eclipsed** | · | ~ | = | | ~ | · | x? | x | · | ~ | · |
| **Roguelite** | = | k | = | ~ | | k | ~ | · | ~ | k | k |
| **Skills&Powers** | = | xk | · | · | k | | = | · | · | k | k |
| **Fellowship** | = | · | = | x? | ~ | = | | = | · | · | k |
| **LootBags** | · | ~ | ~ | x | · | · | = | | ~ | · | · |
| **MMD** | · | ~ | ~ | · | ~ | · | · | ~ | | · | · |
| **Minimap** | · | ~ | · | ~ | k | k | · | · | · | | · |

Details:
- **RAS × Runeborn (=x):** Runeborn shrine level-ups require RAS and grant `rpgLevelsPerRuneLevel` RAS levels each. RAS also levels from kill Valor, so players gain RAS levels from **two** currencies (runes and VP). Both systems raise HP and damage (RAS Vitality/Attack Power vs Runeborn Vigor/Strength scaling), so balance one against the other.
- **RAS × RPG Mobs / Roguelite / Skills and Powers / Fellowship (=):** mob levels follow RAS level, ranked kills pay bonus Valor and shards give 15 VP; Remembering pays Valor; RAS levels give skill points; ally level is capped at RAS level.
- **Runeborn × RPG Mobs (x):** both level mobs and roll elites (Runeborn champions with affixes vs RPG Mobs ranks with traits). Turn off Runeborn `mobLevelsEnabled`. RPG Mobs may still rank/trait Runeborn's Sovereigns and MMD guardians, because those are vanilla mob types; test boss difficulty.
- **Runeborn × Skills and Powers (xk):** two active-ability systems with separate mana (FP vs Essence). I and R clash.
- **Runeborn × Eclipsed (~):** Ember Shrines and Grace Embers are both rest, respawn and travel points. Split them by dimension. The "Sovereign" name appears in both mods.
- **RPG Mobs × Eclipsed (=):** the Realm gets a 30–100 level band, and the five Realm bosses are in `#remnant_mobs:bosses` (level shown, never scaled). The regular Realm creatures *are* leveled on top of their own stats.
- **RPG Mobs × Roguelite (=):** all 23 Archive creatures are `#remnant_mobs:never_leveled`.
- **Eclipsed × LootBags (x):** the Realm bosses aren't in `#c:bosses`, so no guaranteed boss bags without a tag edit.
- **Eclipsed × Fellowship (x?):** fog gates admit players only, so sellswords likely can't follow into boss rooms (inferred; verify). Realm build protection also applies.
- **Fellowship × LootBags (=):** pet and ally kills count as the owner's.
- **Roguelite × others (~):** "Remnant" relic rarity vs RPG Mobs' "Remnant" rank; `tbos:waystone` vs the Waystones mod name; `tbos:shardling_swarm` vs `remnants:shardling`. Memory Keys can recollect MMD dungeons and other mods' structures.
- **Minimap × Runeborn/Eclipsed (~):** manual "Site of Grace"/"Waygate" emblems; automatic bloodstains complement Runeborn's dropped runes.
- **Better Farming++ × Sprout & Soil:** no overlap (QoL vs crops); Sprout & Soil is broken anyway.
- **The Witch Hut × vanilla:** adds a separate structure and does **not** replace the swamp hut.

### 3.2 NightBeam × common pack mods

| Common mod | Overlap with NightBeam mods | Recommendation |
|---|---|---|
| **Better Combat** | Runeborn already provides stamina, dodge roll, weapon arts on R and attribute scaling, and ships **no** `weapon_attributes`, so its 74 armaments get no Better Combat movesets. Two combat-feel layers. | Choose one combat layer. If keeping Better Combat, author `weapon_attributes` for Runeborn weapons and test stamina interplay. |
| **Iron's Spells 'n Spellbooks** | A third caster system next to Runeborn (FP spells) and Skills and Powers (Essence). Three mana bars; likely key overlaps (check Iron's cast/wheel keys against R/Z/B/H/V). | Prefer Runeborn spells (+ optionally Skills and Powers); add Iron's only if magic is a pillar of the story. |
| **Farmer's Delight** | Sprout & Soil's tomato duplicates FD (moot, since S&S is excluded). Better Farming++ right-click/sweep harvest also acts on CropBlock-based FD crops. | Keep FD; exclude Sprout & Soil; tag odd FD crops `#better_farming_plus:not_harvestable`. |
| **Xaero's Minimap/World Map, JourneyMap** | Duplicate of Remnants Minimap (also client-side). | Ship Remnants Minimap only, for theme. |
| **AE2** | No More 63 AE2 is an AE2 addon; Simple Terminals and Core Utilities duplicate storage/tech roles. | No AE2 in a soulslike → exclude all three. |
| **YUNG's structures** | Much More Dungeons adds new structures alongside YUNG's Better Dungeons. YUNG's Better Witch Huts replaces the vanilla hut, while The Witch Hut adds a second hut type. YUNG's keeps vanilla structure ids, so RPG Mobs' structure minimums still apply. | Compatible; MMD and YUNG's can both stay; pick one witch-hut flavour. |
| **Neat / ToroHealth / Jade health bars** | RPG Mobs draws nameplates with health bars; Runeborn draws a target bar. | Don't add a health-bar mod; set Runeborn `showTargetBar: false` or keep one. |
| **Waystones (blay09)** | Name clash with `tbos:waystone`; extra fast travel on top of Runeborn shrines and Realm graces. | Avoid the Waystones mod for soulslike travel discipline. |

---

## 4. Keybind collisions (defaults)

**Bold** = read from bytecode; the rest are from the mod page.

| Key | Mods that bind it by default |
|---|---|
| **R** | Runeborn Weapon Art · Skills and Powers Cast 1 (**R**) · Roguelite Memory ability 1 (**R**) · Wands Mode wheel, hold (**R**) · Ballistics Reload (**R**) |
| **I** | Runeborn Status Screen/Codex · Skills and Powers Open Skill Tree (**I**) · Ballistics Inspect (**I**) |
| **K** | RAS Open Stats Menu (**K**) · Roguelite Living Memories loadout (**K**) |
| **G** | Fellowship Command wheel (**G**) · Wands settings (**G**) · Roguelite Memory ability 2 (**G**). Minimap uses G only inside its world-map screen. |
| **N** | Minimap Show/Hide · Roguelite Archive Codex (**N**) |
| **B** | Minimap Place Marker · Skills and Powers Cast 3 (**B**) |
| **Z** | Skills and Powers Cast 2 (**Z**) · Wands Undo, with Ctrl (**Z**) |
| **V** | Roguelite Memory ability 3 (**V**) · Ballistics Fire mode (**V**) |
| **H** | Skills and Powers Cast 4 (**H**). Minimap uses H only on the world map. |

These keys are unique: U Fellowship roster, M Minimap world map, J Roguelite objectives, Y Wands redo (with Ctrl), Left Alt Runeborn dodge, and = / - Minimap zoom.

**Suggested defaults for the "include" set**, to ship in `options.txt`:
- Keep RAS K, Runeborn R / I / Left Alt, Fellowship G / U, and Minimap M / N / B / = / -.
- Move Roguelite to: Codex **Y**, Memory 1/2/3 **Z / X / C** (they are only active inside the Archive), loadout **O**, objectives J.
- If Skills and Powers is added: tree **P**, casts on four free keys or mouse buttons (e.g. **V**, **H**, Mouse 4, Mouse 5), and move Minimap "Place Marker" off B if B is used.
- If Wands are added: wheel on a mouse button, settings unbound (Sneak + right-click air still opens it).

---

## 5. Recommendations

| Decision | Mods |
|---|---|
| **Include** | Jauml · RPG Stats (RAS) · Runeborn · RPG Mobs · The Eclipsed Realm (+ GeckoLib) · Roguelite Dungeons · Fellowship · Much More Dungeons · Fisherman's Coast · Remnants Minimap (client) |
| **Optional** | Skills and Powers (if you want a skill-tree class layer) · Mob LootBags (only with re-tuned tables) · Smart Villagers AI (built-in dialogue, no provider) · RE:Constructed Wands · Better Farming++ · Simple Terminals · The Witch Hut (low priority) |
| **Exclude** | Sprout & Soil (broken on 1.21.1) · The Gingerbread House · Genetically Modified Monsters · Chronofall · Remnants Ballistics · Core Utilities · No More 63 AE2 (unless AE2) |

**Config to ship with the include set:**
1. Runeborn `config/runeborn-server.json`:
   - `mobLevelsEnabled: false` (RPG Mobs owns mob scaling); keep `eliteChance` and verify that champions and Sovereign Fragments still appear.
   - Decide `rpgLevelsPerRuneLevel`, and lower RAS kill VP (`mob_xp.json`) if Runeborn should be the main leveling path. Otherwise lower Runeborn's `runeGainMultiplier`.
   - Consider `shrineFastTravel` on (Overworld) alongside Realm graces.
2. RPG Mobs `levels.json`: add Much More Dungeons structure minimum levels if wanted; keep the Hunter's Moon.
3. RAS: add a 1.21-format recipe for `rpg_attribute_system:scroll_of_rebirth` (or give it as a quest reward).
4. Eclipsed Realm: keep `rituals_realm_only` (story gating); `build_protection` on.
5. Fellowship `config/better_with_gold/fellowship.json`: `partySize` 2–3 for souls difficulty; consider `permadeath` for stakes.
6. Mob LootBags (if added): rewrite the `mob_loot_bags:bags/*` tables and add the Realm bosses to `#mob_loot_bags:bosses`.
7. Ship the keybind defaults from §4. Don't add Neat or Jade health bars.

---

## 6. Quest-writing reference (how to detect things)

| Story beat | Use this |
|---|---|
| First RPG level-up / Valor | RAS has no advancements. Use RPG Mobs `remnant_mobs:taste_of_valor` (absorb a Remnant Shard) or a KubeJS check. |
| Kindle first Ember Shrine | `runeborn:feats/kindle` (block `runeborn:ember_shrine`) |
| Slay a Runeborn Sovereign | `runeborn:feats/fell_dusk_rider`, `fell_varghast`, `fell_sylvara`, `fell_kaelthar`, `fell_ysolde`, `fell_morgrath`, `fell_vaelorn` (not entity ids: they are vanilla mobs) |
| Rank kills / Hunter's Moon | `remnant_mobs:proven_hunter` (Elite), `champions_bane`, `remnants_end` (Remnant), `under_the_hunters_moon`, `punching_up` |
| Enter the Eclipsed Realm | dimension `remnant_bosses:eclipsed_realm` or `remnant_bosses:realm/enter_realm` |
| Realm bosses | kill `remnants:hollow_sovereign`, `remnants:gravebound_warden`, `remnants:forgotten_watcher`, `remnants:ossukage`; miniboss `remnants:burial_guardian`; or `remnant_bosses:realm/remnant_felled` (Sovereign) |
| Boss trophies | items `remnant_bosses:sovereigns_ruin`, `sovereigns_sigil`, `hollow_crown`, `wardens_grasp`, `gravebound_executioner`, `crypt_sigil`, `memory_staff`, `watchers_eye`, `ossukage_sword` |
| Roguelite prologue | `tbos:story/*` chain (see §2.6); Last Curator `tbos:phoenix_guardian` / `tbos:story/defeat_last_curator` |
| First expedition / Remember | `tbos:expedition/recollection`, `tbos:expedition/remember`, dimension `tbos:fractured_archive` |
| Dungeon trail | `muchmoredungeons:discover_<id>`, `slay_<id>_guardian`, `all_dungeons`, `all_labyrinths` |
| Coast | `fisherman_house:discover_<id>`, `open_bottle`, `all_structures` |
| Hire a sellsword | no advancement; KubeJS or entity check for `better_with_gold:ally` |

Structure ids for `/locate` and structure tasks are listed per mod above. Roguelite's Fracture Shrines and the Meridian Archive are placed by code and are not `/locate`-able.

---

## 7. Lore hooks (every in-mod name a story can use)

**Brand words shared across mods:**
- **Remnant / Remnants:** RPG Mobs' Remnant rank and Remnant Shard; "Remnant : Ossukage, the original Remnant" and "REMNANT FELLED" in the Eclipsed Realm; the *Remnant* relic rarity in Roguelite; Remnant Tome in Skills and Powers; Remnant Alloy in Ballistics.
- **Sovereign:** Runeborn's 7 Sovereigns, Sovereign Fragments and Crown Shards vs the Eclipsed Realm's Hollow Sovereign ("the Last King") with Sovereign's Seal, Ruin and Sigil. Hook: the Hollow Sovereign as the eighth, fallen Sovereign.
- **Grace / Ember / Shrine:** Runeborn Ember Shrines and Ember/Azure Flasks; Eclipsed Grace Embers, the Gracetree and Arrival Shrine; Minimap "Site of Grace"; Roguelite Fracture Shrines.
- **Memory / Forgetting:** Eclipsed Forgotten Watcher, Memory Shard, Lens of Memory, Memory Staff, Ancient Knowledge Fragment and the Archivist set; Roguelite Memory Keys, the Fractured Archive, Archivist's Journal, Living Memories and Remember/Forget.
- **Hollow:** Eclipsed Hollow Legion, Hollow Citadel and Hollow Crown; Runeborn "Hollows" and "Sovereign of the Hollow Vale"; Roguelite "The Hollow Catalogue"; RPG Mobs' example name "Vorgrim the Hollow".
- **Warden:** Gravebound Warden and the Warden set, vanilla Warden, MMD Bone/Cinder Warden, Roguelite "Crownless Warden" and lesser wardens. Disambiguate in quest text.
- **Eclipse:** Eclipsed Realm, Eclipse Shard, Eclipse Stone; Skills and Powers ultimate "Eclipse"; Runeborn "Eclipse Twinblade"; Ballistics "Eclipse Railgun".

### The Eclipsed Realm
- **Places:** the Eclipsed Realm · black eclipse sun · the Gracetree · Tarnished Fields · The Gracewood · Gravefield Barrows · Ashen Wastes · The Lantern Heights · The Stilled Sea · Ossuary Depths · Hollow Citadel (throne hall) · Gravebound Catacombs (chain chapel, burial vault) · Forgotten Observatory (dome, memory vault, four lens platforms) · Arrival Shrine · grace shrines (ring of weathered standing stones).
- **Bosses:**
  - Hollow Sovereign ("the Last King"; "The Last Command"; Sovereign's Pauldron; Spectral Royal Guard; Royal Blade)
  - Gravebound Warden (Warden's Chain, Chain Anchor)
  - The Forgotten Watcher ("Memory of the Watcher", Memory Bolt, crystal aegis)
  - Remnant : Ossukage (Ossukage Rune, kunai)
  - Burial Guardian
  - Soul Collector
- **Families:**
  - Hollow Legion: Hollow Sentinel, Hollow Arbalist, Fallen Standard Bearer, Soulbound Knight
  - Cryptborn: Catacomb Rat, Crypt Lurker, Gravebound Soldier
  - Forgotten Souls: Lost Pilgrim, Memory Wraith, Soul Wisp
  - Ashbound Constructs: Ashbound Crawler, Ember Servitor, Rusted Guardian
  - Corrupted Relics: Shardling, Ancient Vessel, Relic Stalker
- **Objects:** Waygate · Eclipse Shard · fog gate · Ancient Altar · Ancient Pedestal · Grace Ember · Boss Hunts Journal · Tarnished Regalia · Royal Soul Fragment · Grave Iron · Crypt Key · Lens of Memory · Memory Shard · Ashen Cog · Relic Shard · Regalia, Warden and Archivist sets · Weathered Gravestone · Graceroot · Gilded Leaves · Eclipse Stone.
- **Phrases:** "The Realm will not change." · "GRACE DISCOVERED" · "Grace Restored" · "REMNANT FELLED" · "The Waking World".
- **Advancement titles:** Splinter of the Black Sun, The Way Remembered, Beneath the Eclipse, The Last Command Ends, The Waking World.

### Runeborn
- **Core terms:** runes · rune level · Ember Shrine · Ember Flask · Azure Flask · the Merchant · Relics · Crown Shards · Sovereign Fragments · Sigils · Tear of Rebirth · Hallowed Tear · Faded/Hero's/Lustrous/Radiant/Sovereign Rune · Tempering and Lustrous Stones · Sunseed.
- **Origins:** Knight-Errant ("sworn to no lord"), Ashborn ("risen from ash with nothing"), Astromancer, Cutthroat, Duelist, Hexblade, Oracle, Penitent ("a sinner of the old order"), Ronin, Warlord.
- **Attributes:** Vigor, Mind, Endurance, Strength, Dexterity, Intelligence, Faith, Arcane.
- **Statuses:** Hemorrhage, Frostbite, Poison, Blight.
- **Sovereigns:**
  - The Dusk Rider, "Who Rides When Light Fails"
  - Varghast the Grafted, Sovereign of the Hollow Vale
  - Sylvara, Frost Matron, of the Rime Veil
  - Kaelthar the Stormcaller, of the Drowned Sky
  - Ysolde, the Crimson Bloom, of the Scarlet Garden
  - Morgrath, Ash Sovereign, of the Burning Crown
  - Vaelorn, the Wyrm-Ravager, of the Last Shore
- **Champion affixes:** Blazing, Bloodthirsty, Colossal, Frenzied, Frostborne, Ironclad, Phasing, Stormtouched, Venomous, Warded.
- **Weapon arts:** Unsheathe, Crimson Flurry, Stormcall, Lunar Wave, Shadowstep, Voidstar Fall, Bloomward, Earthshaker, Ember Cleave, Frenzied Strikes, Grave Harvest, Gravity Well, Impaling Thrust, Leaping Cleave, Quickstep, Rimefrost Stomp, Ruinous Charge, Sacred Edge, Spinning Reap, Starblade Volley, Thunderstep, War Cry, Whirlwind.
- **Spells:** Abyssal Ray, Blessed Flame, Blood Sigil, Dragonfire, Frost Comet, Gravity Orb, Mending Light, Pillar of Flame, Starshard Barrage, Starshard Bolt, Storm Bolt, Storm Spear.
- **Banners:** "Rise, Runeborn", "YOU DIED", "Shrine Kindled", "Sovereign Felled", "Runes Recovered", "Crown Shard Claimed".
- **Notable weapons:** Varghast's Graft-Axe, Duskrider Glaive, Sylvara's Frostbound Staff, Kaelthar's Storm Totem, Stormcaller Pike, Bloodbloom Sigil, Voidstar Hammer, Ashen Greatsword, Wyrmfang Halberd, Dragonsoul Seal, Lunar Bloomfang, Abyssal Scepter, Gravewarden Scythe, Starfall Slab, Eclipse Twinblade, Bloomwarden Mace, Sunlit Sword (full list in the ID block).

### RPG Mobs and RAS
- **Ranks:** Common, Veteran, Elite, Champion, **Remnant** (named, e.g. "Vorgrim the Hollow"; "A Remnant stirs nearby").
- **Events and items:** Hunter's Moon ("Monsters grow stronger until dawn") · threat · Remnant Shard · Hunter's Lens · Brand of Challenge ("Challenge accepted").
- **Traits:** Vampiric, Frostbite, Infernal, Venomous, Withering, Berserk, Crushing, Juggernaut, Thornskin, Warded, Regenerating, Deflecting, Swift, Blinking, Packleader, Volatile.
- **Advancements:** Know Thy Enemy, Proven Hunter, Champion's Bane, Nothing Left to Hide, Punching Up, A Remnant's End, Taste of Valor, Accept the Challenge, Under the Hunter's Moon.
- **RAS:** Valor / Valor Points, RPG Level, Scroll of Rebirth, Tome of Ascension, "The Ascendant Update", "Memory Of The Past" (RAS's old name, still its keybind category), and the attributes Vitality, Attack Power, Attack Speed, Protection, Toughness, Agility, Fortitude, Exploration.

### Remnants: Roguelite Dungeons
- **Prologue:** The Birth of Steve · Fracture Shrines · Yesterglass (Cracked Yesterglass Lens) · the Meridian Archive · Hall of Alignment ("Astronomical Alignment") · Choir of Hours ("Choir of Recollection") · Broken Meridian · Memory Plates · Memory Lantern · the Orrery · Archive Core → Curator Gateway.
- **The Last Curator:** Ruined/Remembered forms; phases Catalogue, Revision, Erasure.
- **Shrine sites:** Curator Workshop, Evacuation Gate, Observatory.
- **Memory scenes:** The Evacuation · The Instant the Archive Fell · The Orrery at Work · A Family Beneath the Conjunction · The Curator Repaired · The Final Command.
- **Expedition terms:** Fractured Archive ("THE ARCHIVE REMEMBERS") · Memory Key · Waystone · Distortions · Heat · Fracture · Renown · Recollection · Momentum · Remember / Forget · Archive Codex · Insights · Living Memories · Archivist's Journal · Hall of Records · Weekly Recollection · Shade (Haunted) · Cantor Seal · Chronicle Shard · Recalled Hour.
- **Floors:** The Parallax Wake, The Starless Gallery, Meridian Descent, Choir of Dust, The Glassbound Vault, The Hollow Catalogue, The Cantor's Labyrinth, The Unwritten Hour.
- **Creatures:** Armillary Scout, Ash Chorister, Blank Chronist, Dust Cantorile, Gallery Moth, Gnomon Knight, Hour Cantor, Hour-Hand Wraith, Index Wight, Labyrinth Usher, Lensward, Memory Leech, Meridian Sentinel, Metronome Hound, Minotaur, Null Portrait, Parallax Wraith, Prism Stalker, Shard Drifter, Shardling Swarm, Shelf Crawler, Wake Cutter.
- **Lesser wardens:** Tribunal Archivist, Bronze Reviser, Index Devourer, Crownless Warden.
- **Relic signatures:** Last Hour, Fracture Step, Choir's Echo, Yesterglass.

### Skills and Powers
- **Theme and schools:** The Remnant Constellation · Pyromancy, Stormcalling, Umbral Arts, Tidecalling, Earthshaping, Verdance · Essence · Power XP.
- **Items and creatures:** Remnant Tome · Tome of Unbinding · Fire Golem · Fire/Water Rune · Fire/Water Seed · Tidebinder.
- **Keystones:** Pyre Heart, Glass Cannon, Conduit, Windborne, Blood Pact, Soul Eater, Eternal Tide, Glacial Bulwark, Unyielding, Bedrock Will, Undying Grove, Verdant Bloom.
- **Ultimates:** Meteor, Tempest, Eclipse, Maelstrom, Mountain's Wrath, Verdant Rebirth.

### Fellowship
- **Units and classes:** sellswords · warband · Bulwark (Challenge) · Skirmisher (Whirl) · Ranger (Volley) · Mender (Mend) · Arcanist (Arc Storm).
- **Traits and epithets:** Steadfast, Swift, Brutal, Keen-eyed, Stalwart, Devoted, Lucky, Greedy, Hardy, Fearless, Merciful.
- **Titles and story terms:** Veteran, Champion, Hero, Legend · Morale · Warbanner · the Chronicle · the Remembrance (fallen allies) · "swore the oath" · "the kill that blooded them".
- **Gear and commands:** Gilded Regalia · Golden Fish · formations Line, Wedge, Shield Wall, Circle.

### Much More Dungeons, Fisherman's Coast, Minimap, Loot Bags, Smart Villagers
- **MMD:**
  - Dungeons: Smuggler's Villa, Arcane Spire, Cursed Keep, Soulfire Crypt.
  - Labyrinths: Forgotten Catacombs, Sunscorched Tomb, Verdant Warrens, Rimefrost Vaults, Abyssal Halls, Infernal Bastille.
  - Guardians: Smuggler Chief, Spire Illusionist, Keep Warlord, Cinder Warden, Bone Warden, Tomb King, Broodmother, Frost Lich, Abyssal Knight, Brute Overseer.
  - Spawner flavour: cursed warriors, berserker, shadow mage, rage brute.
  - Terms: "the dungeon trail" · Dungeon Map: Tier II–IV · Dungeon Delver · Into Every Maze.
- **Fisherman's Coast:**
  - Residents: Saylor, Harbourmaster Wren, Keeper Morrow, Old Bayou Tam, Frost-Beard Ole, Ferryman Hale, the drowned deckhands.
  - Objects: Messages in a Bottle (12 "notes from the sea"), Bottled Map to a Wreck, Sunken Trawler.
  - Advancement: Coastal Wanderer.
- **Minimap:** Site of Grace, Bloodstain, Resting Place, beacon pillars of light; emblems Castle, Church, Ruins, Tower, Catacombs, Portal, Waygate, Boss, Great Tree, Summit, Lookout….
- **Loot Bags:** Cursed, Hourglass, Locked and Summoning bags; Diamond Key; Fortune Talisman; advancements Loot Goblin, Myth Made Real.
- **Smart Villagers:** Hero of the Village Square; stranger / friend / hero / wary / hostile.

---

## 8. Method notes and caveats

- **Registry IDs** are what the jar registers:
  - Items need an item model plus a lang entry or a registration string literal.
  - Blocks need a blockstate.
  - Entities need a lang entry plus a string literal in the registration class, in the mod's real registry namespace.
  - Structures, dimensions, biomes and advancements come from `data/` files.
  - Exceptions found and handled:
    - Retired Eclipsed Realm keys are excluded.
    - Ballistics `icon/*` models are not items.
    - "Map" names in Much More Dungeons and Fisherman's Coast are filled-map titles, not item ids.
    - `mob_loot_bags:cursed` and `tbos:lesser_boss` are name templates, not entities.
    - GMM spawn eggs are registered but have no model.
  - Tags in pre-1.21 plural folders (`tags/blocks`, `tags/items`, `tags/entity_types`) were dropped. Every one duplicated a singular-folder tag.
- **Keybind defaults:** marked **(b)** where read from the `KeyMapping` bytecode, **(p)** where taken from the mod page. Runeborn and Minimap build their mappings dynamically, so theirs are (p).
- **RAS attribute names** (Vitality … Exploration) are inferred from string constants in the jar. Change them in `config/ras/attributes/attribute_<N>.json`.
- **Not verified in-game** (no code was run):
  - Scroll of Rebirth recipe loading
  - Runeborn champions with `mobLevelsEnabled: false`
  - Fellowship allies and Realm fog gates
  - RPG Mobs ranking Runeborn Sovereigns
- Working files: jars in `scratchpad/jars/<slug>/`, scripts in `scratchpad/scripts/nightbeam/`.
