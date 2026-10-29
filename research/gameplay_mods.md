# Remnants | The Modpack - Season 1: community gameplay layer

Minecraft **1.21.1**, **NeoForge** only. Data pulled **2026-10-29**. Companion data file: `gameplay_mods.json` (same folder, one object per mod incl. every library). Language files for the included content mods are in `registry/<modid>_en_us.json`.

Scope: the community content around NightBeam's core (RPG Stats/RAS, RPG Mobs, Eclipsed Realm, Mob LootBags, Much More Dungeons / Roguelite Dungeons, Skills and Powers, Runeborn, Fellowship). Performance, QoL, storage, minimap and quest infrastructure belong to the other researchers and are not repeated here.

## 1. Totals

- **Include: 55 jars** = 41 content mods + 14 libraries. This is the default Season 1 gameplay layer and sits inside the 50-90 target.
- **Optional: 41 jars** = 26 content mods + 15 libraries that come only with them. They are off by default; each one has an 'only if' condition below.
- **Excluded: 37** candidates, each with its reason.
- Every candidate checked: 133. Each `required_deps` slug of an included or optional mod has its own entry in the JSON, and the build script checks this. No included mod depends on a non-included jar.

How the data was gathered:
- **Modrinth**: `/v2/project/{slug}/version?loaders=["neoforge"]&game_versions=["1.21.1"]`, newest *release* (a beta/alpha is used only when nothing else exists, and it is flagged). Version id, filename, url, sha1, sha512 and size are taken from that file. Dependencies are resolved from project ids to slugs.
- **CurseForge**: cfwidget by project id. Project ids were found through the ModpackIndex search API, because cfwidget 404s on many slugs. For some multi-loader YUNG's projects, cfwidget's file list is partial and shows no NeoForge 1.21.1 file. Those entries keep the CF project id with `file_id: null`; resolve the file id in the CurseForge app, or use the Modrinth file.
- **Jars**: 100 jars were downloaded: 99 from Modrinth (sha1-checked against the API) and Twilight Forest from the CurseForge CDN. Two of them are NightBeam jars (Runeborn, The Witch Hut), read only to check for clashes and read only as zip data (Python `zipfile`). They were never run. From each jar: `neoforge.mods.toml` dependencies (these are the real requirements; Modrinth metadata is sometimes incomplete), `c:bosses` tags, `worldgen/structure` ids, dimensions, advancements, lang keys and Better Combat `weapon_attributes`.
- **Side**: `both` means install on client and server. `server` means required on a dedicated server and optional or unneeded on the client. Single-player runs an integrated server, so **every jar ships in the client instance** whatever its side.

## 2. Decisions that protect NightBeam's systems

| NightBeam system | Community candidates that collide | Decision |
|---|---|---|
| **Runeborn**: stamina, dodge roll (Left Alt, i-frames), weapon arts (R), 74 armaments in 19 classes, tempering/affinities, 12 FP spells, Ember Shrine fast travel, 7 Sovereign bosses | Epic Fight, Combat Roll, Shield Expansion, Simply Swords, Spartan Weaponry, Marium's Soulslike Weaponry, Waystones | Epic Fight **out** (it replaces the whole combat model and is incompatible with Better Combat). Combat Roll **out** (a second dodge, and its default key R collides with the weapon art). Weapon catalogues are **optional/out**. Waystones is flagged for the QoL researcher because Ember Shrines already travel. **Better Combat stays**: it only animates swings. Runeborn ships *no* Better Combat data (checked in the jar), so the pack needs a small datapack that maps Runeborn armament classes to Better Combat presets. |
| **RPG Stats (RAS)** attributes + level screen | Apotheosis / Apothic Attributes, RPG Series Jewelry (spell_power attributes) | **out**: they would be two attribute UIs and parallel stat lines. |
| **RPG Mobs**: levels, 5 ranks, named Remnants, **Hunter's Moon** | Enhanced Celestials (Blood Moon), mob-difficulty mods, Apotheosis elite bosses, Mutant Monsters | Enhanced Celestials **out** (it would be a second lunar event system). Difficulty mods **out**. Mutant Monsters **optional**, because RPG Mobs ranks already make big versions of vanilla mobs. Modded bosses: Cataclysm, Mowzie's, Bosses'Rise, BOMD (and Twilight Forest/Iron's) tag their bosses `c:bosses`. Born in Chaos, Aquamirae, The Graveyard, Friends&Foes, Illager Invasion and Deeper and Darker do **not**. Add their bosses to `c:bosses` with a datapack, and confirm which tag RPG Mobs reads to 'show a level without scaling'. |
| **Skills and Powers** (6 schools, 30 abilities, Essence; optional in the NightBeam audit) and Runeborn FP spells | Iron's Spells, Ars Nouveau, RPG Series classes (Spell Engine), Goety | Iron's Spells **optional**, never together with Skills and Powers. All other magic systems **out**. Classes come from Runeborn origins + Skills and Powers + Fellowship roles. |
| **Eclipsed Realm** boss dimension | Twilight Forest, The Aether, Undergarden | Twilight Forest **optional** (Season 2 candidate). Aether and Undergarden **out**. Deeper and Darker's Otherside stays in as a compact Warden-tier chapter. |
| **Mob LootBags** / Runeborn relics | Apotheosis affixes/gems, Relics mod | **out**. Artifacts stays in because its trinkets come from chests and Mimics, not affixed stats. |
| **Much More Dungeons / Roguelite Dungeons** (labyrinths) | YUNG's Better Dungeons, IDAS (its own `idas:labyrinth`), Illager Invasion (`illagerinvasion:labyrinth`) | Different structure sets, so there is no clash. Use the namespaced ids in quests. |
| **The Witch Hut** (mod id `better_witch_huts`, display name 'Better Witch Huts') | YUNG's Better Witch Huts (`betterwitchhuts`, disables vanilla huts by mixin) | YUNG's **out**: two 'Better Witch Huts' in the same swamps. Terralith (`terralith:witch_hut`) and D&T (`nova_structures:witch_villa`, `mangrove_witch_hut`) also add witch buildings, so quests must name the exact structure id. |
| **Fellowship** sellswords (spawn near village bells) | Guard Villagers, Towns and Towers | Both **in**. Guards defend villages and are not party members. T&T adds more villages, which means more bells to hire at. |
| **Fisherman's Coast** | Aquaculture 2 | Aquaculture **optional**: its Neptunium gear tier competes with Runeborn armaments. |

## 3. Integration tasks before the first build

1. **Better Combat x Runeborn**: write `data/runeborn/weapon_attributes/<item>.json` with `parent` set to a Better Combat preset (`dagger`, `katana`, `claymore`, `twin_blade`, `scythe`, `spear`, `halberd`, `hammer`, `heavy_axe`, `fist`, `claw`, `staff`, `mace`, `rapier`...). Then play-test Runeborn's per-attack stamina cost with Better Combat combos.
2. **Boss tag datapack**: add `born_in_chaos_v1:lord_pumpkinhead`, `aquamirae:captain_cornelia`, `aquamirae:maze_mother`, `graveyard:lich`, `illagerinvasion:invoker`, `friendsandfoes:wildfire` and `deeperdarker:stalker` to `c:bosses`, if that is the tag RPG Mobs uses. Otherwise they get rank-rolled and level-scaled like normal mobs.
3. **Illusioner owner**: Friends&Foes and Illager Invasion both re-enable and restyle the vanilla Illusioner. Turn it off in Friends&Foes' config and keep Illager Invasion's Illusioner Tower.
4. **Structure density**: about 10 structure mods add roughly 300 structure ids (D&T 97, T&T 60, WDA 40, Terralith 28, Graveyard 22). Use Sparse Structures (`/dumpstructuresets`) to space out WDA and D&T first. Explorer's Compass blacklist: hide boss arenas if they should be found by exploring.
5. **Keybinds**: Runeborn uses R (weapon art), Left Alt (dodge) and I (status). Skills and Powers, if enabled, uses R/Z/B/H. None of the included community mods binds these by default. Excluded Combat Roll was the one that collided (R).
6. **The Graveyard 4.0.1 (2026-10-27)** newly requires Villager Trading Plus `[1.1.0,2)`. Modrinth has VTP 1.1.1, but CurseForge's newest 1.21.1 VTP file is `villager-trading-plus-1.1+1.21.jar` (2024-09). Test the CF pack resolution.
7. **World creation**: Terralith, Tectonic and Nullscape must be in the world from the start. Never add them to an existing save.
8. **Spawn pressure**: Born in Chaos (mini-bosses from night 10, Sir Pumpkinhead 25 Oct-5 Nov) + The Graveyard + Illager Invasion all stack on RPG Mobs' level scaling. Tune spawn weights during balancing, not by adding a difficulty mod.
9. **Licences**: Cataclysm and Friends&Foes are CC-BY-NC-ND. Bosses'Rise, Born in Chaos, D&T and WDA are All Rights Reserved. DMR is PolyForm-Noncommercial. Distribute the pack through CurseForge/Modrinth manifests (download by API), never by re-hosting jars.

## 4. Picks per category

### Combat feel

**Included**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Better Combat** (`better-combat` / `bettercombat`) | 2.4.0+1.21.1-neoforge | 639842 / 8430183 | both | LicenseRef-All-Rights-Reserved | 101.9M | The standard animated melee layer (combos, swing arcs, two-handed/dual wield). Ships presets for katana, claymore, twin_blade, scythe, halberd, spear, etc. Cataclysm, Born in Chaos, Aquamirae, Bosses'Rise and Simply Swords already ship weapon_attributes for it. |

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Shield Expansion** (`shield-expansion` / `shieldexp`) | 1.4.3 | 583318 / 8884525 | both | Apache-2.0 | 29.3M | Adds shield tiers, Off-Guard cooldown and timed parries, the one soulslike verb Runeborn lacks. Off by default so the pack ships one combat ruleset; enable only after testing against Runeborn's stamina/poise. |
| **Simply Swords** (`simply-swords` / `simplyswords`) | 1.70.2-1.21.1 | 659887 / 8746001 | both | LicenseRef-Custom | 65.5M | Popular unique/legendary weapons with BC animations (429 weapon_attributes). Runeborn already provides 74 armaments in 19 classes (katanas, twinblades, greatswords...) with tempering/affinities, so a second weapon catalogue is duplication; Runeborn would scale them via vanillaWeaponsScale if enabled. |

### Classes & magic

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Iron's Spells 'n Spellbooks** (`irons-spells-n-spellbooks` / `irons_spellbooks`) | 1.21.1-3.16.3 | 855414 / 8680204 | both | LicenseRef-All-Rights-Reserved | 77.3M | Best-in-class spellbook mage with strong content (Dead King, Tyros, Citadel, Catacombs), but it would be another casting system and mana bar next to Runeborn (12 spells on FP via staves/seals) and NightBeam's own Skills and Powers (optional in the NightBeam audit; 30 abilities on Essence in six schools that mirror Iron's). Optional 'Arcanist' module only, and never together with Skills and Powers. |

### Accessories & loot

**Included**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Artifacts** (`artifacts` / `artifacts`) | 13.2.5 | 312353 / 8791899 | both | MIT | 163.9M | 48 vanilla-style exploration trinkets found in chests and Mimics; gives dungeons the rare-loot moment the brief asks for without touching stats systems. |

### Bosses & mobs

**Included**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Aquamirae** (`aquamirae` / `aquamirae`) | 7.2.13 | 536254 / 9228645 | both | LicenseRef-Obscuria-Modding-License | 60.4M | Frozen-ocean horror: Ice Maze, pirate ships, Captain Cornelia and the Maze Mother; gives the ocean a dark-fantasy chapter. |
| **Born in Chaos** (`borninchaos` / `born_in_chaos_v1`) | 1.7.6 | 686437 / 8268280 | both | LicenseRef-All-Rights-Reserved | 33.1M | Dark-fantasy/horror bestiary (86 entities, dark towers, graves) with a real boss (Lord Pumpkinhead) and several mini-bosses that appear from night 10; strongest tonal fit in the mob layer. |
| **Bosses of Mass Destruction (Forge/NeoForge)** (`bosses-of-mass-destruction-forge` / `bosses_of_mass_destruction`) | 1.3.3 | 941573 / 8448640 | both | LGPL-3.0-only | 38.7M | Four structure-bound bosses (Night Lich, Obsidilith, Gauntlet, Void Blossom) that give natural exploration goals across Overworld/Nether/End; NeoForge port of the Fabric original. |
| **Bosses'Rise** (`bossesrise` / `block_factorys_bosses`) | 2.1.2 | 1314084 / 8123167 | both | LicenseRef-All-Rights-Reserved | 13.2M | 'Epic souls-like boss fights' by Block Factory: five arena bosses (Underworld Knight, Infernal Dragon, Yeti, Sandworm, Kraken) behind keys; fits a soulslike exactly. |
| **Deeper and Darker** (`deeperdarker` / `deeperdarker`) | 1.4.1-neoforge-1.21.1 | 659011 / 8201775 | both | AGPL-3.0-only | 112.0M | Endgame descent below the Ancient City into the Otherside dimension with Warden-tier gear; dark, compact, vanilla-styled. |
| **Friends&Foes (Forge/NeoForge)** (`friends-and-foes-forge` / `friendsandfoes`) | neoforge-5.0.4+mc1.21.1 | 602059 / 9331874 | both | CC-BY-NC-ND-4.0 | 47.9M | Vanilla-style mob-vote creatures (Copper/Tuff Golem, Glare, Iceologer, Illusioner, Mauler, Wildfire mini-boss) - the 'vanilla-first' backbone of the bestiary. |
| **Guard Villagers** (`guard-villagers` / `guardvillagers`) | 2.4.12 | 360203 / 8767509 | both | LicenseRef-Custom | 107.2M | Village guards defend settlements against levelled raids and night spawns; complements (does not replace) Fellowship's hired warband. |
| **Illager Invasion** (`illager-invasion` / `illagerinvasion`) | v21.1.6-1.21.1-NeoForge | 891324 / 6492670 | both | MIT | 42.1M | Port of Illager Expansion: 10 new illagers, an Invoker boss, Illager Fort and Illusioner Tower - deepens the raid/illager questline. |
| **L_Ender's Cataclysm** (`l_enders-cataclysm` / `cataclysm`) | 3.33 | 551586 / 8931182 | both | CC-BY-NC-ND-4.0 | 139.0M | The flagship boss mod: 8 tagged bosses with dedicated arenas and signature gear; perfect chapter bosses between Runeborn's Sovereigns and the Eclipsed Realm. |
| **Mowzie's Mobs** (`mowzies-mobs` / `mowziesmobs`) | 1.8.2 | 250498 / 7760267 | both | LicenseRef-Mowzies-Mobs-License | 124.8M | Hand-animated, telegraphed bosses (Ferrous Wroughtnaut, Frostmaw, Umvuthi, Sculptor) that suit soulslike pattern-learning, plus useful relic gear. |
| **Naturalist** (`naturalist` / `naturalist`) | 2.0.7+1.21.1-neoforge | 627986 / 9280587 | both | LicenseRef-Custom | 68.4M | Vanilla-style wildlife (bears, deer, boars, snakes, alligators...) that makes the overworld feel alive and gives hunting quests; low performance cost. |
| **The Graveyard (Fabric/NeoForge)** (`the-graveyard-fabric` / `graveyard`) | 4.0.1+mc1.21.1-neoforge | 514468 / 9346778 | both | GPL-3.0-only | 25.5M | Graveyards, crypts, haunted houses and overrun villages with ghouls, revenants, wraiths and the Lich boss - the most on-tone structure+mob pack for 'Remnants'. |

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Critters and Companions** (`critters-and-companions` / `crittersandcompanions`) | 2.7.0 | 574913 / 8646976 | both | LicenseRef-All-Rights-Reserved | 34.2M | Cute ambient critters (otters, red pandas, ferrets); good quality but off-tone for dark fantasy. |
| **It Takes a Pillage Continuation** (`it-takes-a-pillage-continuation` / `takesapillage`) | neoforge-1.0.13+mc1.21.1 | 1111063 / 9018153 | both | MIT | 7.4M | Illager bastilles/camps and new pillager troops; overlaps Illager Invasion + Dungeons and Taverns illager structures - only if the illager arc needs more. |
| **Mutant Monsters** (`mutant-monsters` / `mutantmonsters`) | v21.1.1-1.21.1-NeoForge | 852665 / 7232511 | both | AGPL-3.0-only | 55.5M | Mutant Zombie/Skeleton/Creeper/Enderman mini-bosses; overlaps RPG Mobs' Elite/Champion/Remnant rank tiers which already make 'big version of a vanilla mob' fights. |
| **The Twilight Forest** (`the-twilight-forest` / `twilightforest`) | twilightforest-1.21.1-4.8.3345-universal.jar (CF) | 227639 / 7797302 | both | LGPL-2.1 (per mods.toml) | 211.2M | The classic boss-progression dimension (9 bosses, progression locks) - excellent content, but it competes directly with NightBeam's Eclipsed Realm as the pack's boss dimension. Recommended as a Season 2 chapter or opt-in. |
| **THE UNDEAD REVAMPED** (`the-undead-revamped` / `undead_revamp2`) | 1.8f+1.21.1-neoforge | 479710 / 6778715 | both | LicenseRef-All-Rights-Reserved | 19.4M | 41 new undead types; on-tone but small project (205k MR) self-described as unfinished, and undead variety is already covered by Born in Chaos and The Graveyard. |

### Exploration & worldgen

**Included**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Dungeons and Taverns** (`dungeons-and-taverns` / `mr_dungeons_andtaverns`) | v4.4.4+mod | 853794 / 5768823 | server | LicenseRef-All-Rights-Reserved | 55.9M | Nova's vanilla-style structures: taverns, Illager manor, combat shrines (5 tiers), crypts, End castle and - fittingly - 'remnant_*' ruined settlements; ships advancements usable as quest tasks. |
| **Explorer's Compass** (`explorers-compass` / `explorerscompass`) | 1.21.1-3.4.0-neoforge | 491794 / 7892943 | both | CC-BY-NC-SA-4.0 | 115.2M | Lets players (and quest rewards) locate any structure by id - the bridge between quests and the ~300 structure ids above. |
| **Nature's Compass** (`natures-compass` / `naturescompass`) | 1.21.1-3.4.0-neoforge | 252848 / 7892954 | both | CC-BY-NC-SA-4.0 | 334.0M | Biome locator for biome-gated quests (Terralith adds 130 biomes). |
| **Nullscape** (`nullscape` / `nullscape`) | 1.2.14 | 570354 / 7078265 | server | LicenseRef-Stardust-Labs-License | 40.4M | Turns the End into alien terrain while keeping it desolate; makes the End chapter (Cataclysm Ender Guardian, BOMD Void Blossom/Obsidilith) worth travelling. |
| **Philip's Ruins** (`philips-ruins` / `philipsruins`) | 1.21.1-2.0 | 569737 / 6058135 | both | LicenseRef-All-Rights-Reserved | 53.2M | Ruins, crypts and the 'Lost Soul City' with loot - more 'remnants' scenery and early loot; light. |
| **Sparse Structures** (`sparsestructures` / `sparsestructures`) | 3.0 | 911437 / 6456912 | server | MIT | 29.1M | One config to space out every structure set (incl. modded) - essential with ~10 structure mods; /dumpstructuresets helps per-structure tuning. |
| **Structory** (`structory` / `structory`) | 1.3.17 | 636540 / 8396883 | server | LicenseRef-Stardust-Labs-License | 100.7M | Small atmospheric ruins, chapels, graveyards and outcast villagers - 'remnants of the old world' scenery that suits the pack name; datapack-style, cheap. |
| **Tectonic** (`tectonic` / `tectonic`) | 3.0.28-neoforge-21.1 | 686836 / 8855043 | server | MIT | 52.7M | Terrain shaping; the mod ships a dedicated Terralith-compatible variant, so the two are designed to be paired. |
| **Terralith** (`terralith` / `terralith`) | 2.6.2 | 513688 / 8222737 | server | LicenseRef-Stardust-Labs-License | 101.4M | Vanilla-block biome overhaul (130 biomes, 28 small structures) - the 'vanilla-first' choice; no new wood/block palette. |
| **Towns and Towers** (`towns-and-towers` / `t_and_t`) | 1.13.11 | 626761 / 8657120 | server | CC-BY-NC-SA-4.0 | 124.4M | Biome-specific villages and pillager outposts (60 variants) - vanilla-first settlement variety for villages, Guard Villagers and Fellowship hiring (sellswords spawn near village bells). |
| **When Dungeons Arise** (`when-dungeons-arise` / `dungeons_arise`) | 2.1.68 | 442508 / 7150870 | server | LicenseRef-All-Rights-Reserved | 126.1M | Large hand-built roguelike dungeons (Illager Fort, Plague Asylum, Thornborn Towers, Heavenly Conqueror, Keep Kayra) - the 2-8 player co-op set pieces the brief asks for. |
| **YUNG's Better Desert Temples** (`yungs-better-desert-temples` / `betterdeserttemples`) | 1.21.1-NeoForge-4.1.5 | 631016 / n/a | server | LGPL-3.0-only | 87.3M | Puzzle temple with traps and a Pharaoh's chamber; strong early-game quest target. |
| **YUNG's Better Dungeons** (`yungs-better-dungeons` / `betterdungeons`) | 1.21.1-NeoForge-5.1.4 | 510089 / n/a | server | LGPL-3.0-only | 149.9M | Replaces vanilla spawner rooms with skeleton/zombie/spider dungeons and small catacombs - early-game dungeons that complement NightBeam's Much More Dungeons labyrinths. |
| **YUNG's Better End Island** (`yungs-better-end-island` / `betterendisland`) | 1.21.1-NeoForge-3.1.2 | 901344 / n/a | server | LGPL-3.0-only | 93.9M | Reworked dragon fight arena; the Ender Dragon pays a Runeborn crown shard, so the fight deserves an upgrade. |
| **YUNG's Better Jungle Temples** (`yungs-better-jungle-temples` / `betterjungletemples`) | 1.21.1-NeoForge-3.1.2 | 897669 / n/a | server | LGPL-3.0-only | 84.1M | Expanded jungle temple with puzzles and traps. |
| **YUNG's Better Mineshafts** (`yungs-better-mineshafts` / `bettermineshafts`) | 1.21.1-NeoForge-5.1.1 | 389665 / n/a | server | LGPL-3.0-only | 191.4M | Biome-themed mineshafts; pure vanilla-plus. |
| **YUNG's Better Nether Fortresses** (`yungs-better-nether-fortresses` / `betterfortresses`) | 1.21.1-NeoForge-3.1.5 | 817651 / n/a | server | LGPL-3.0-only | 111.3M | Reworked fortress; the Nether chapter's main dungeon if Incendium stays off. |
| **YUNG's Better Ocean Monuments** (`yungs-better-ocean-monuments` / `betteroceanmonuments`) | 1.21.1-NeoForge-4.1.2 | 689238 / n/a | server | LGPL-3.0-only | 111.8M | Bigger monument; the Elder Guardian already pays a Runeborn relic. |
| **YUNG's Better Strongholds** (`yungs-better-strongholds` / `betterstrongholds`) | 1.21.1-NeoForge-5.1.3 | 465575 / n/a | server | LGPL-3.0-only | 130.1M | Turns the stronghold into a proper multi-hour dungeon before the End chapter. |
| **YUNG's Bridges** (`yungs-bridges` / `yungsbridges`) | 1.21.1-NeoForge-5.1.1 | 536660 / n/a | server | LGPL-3.0-only | 86.2M | Bridges over rivers; makes long overland travel (horses) smoother. |
| **YUNG's Extras** (`yungs-extras` / `yungsextras`) | 1.21.1-NeoForge-5.1.1 | 480006 / n/a | server | LGPL-3.0-only | 81.6M | Small vanilla-style decorations (wells, ruins); harmless flavour. |

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Explorify** (`explorify` / `explorify`) | v1.6.5 | 698309 / 8082824 | server | LicenseRef-All-Rights-Reserved | 81.4M | Vanilla-style small dungeons; good, but overlaps D&T/Structory/Philip's Ruins - add only if the world feels empty. |
| **Incendium Legacy** (`incendium` / `incendium`) | 5.4.4 [alpha] | 591388 / 5962249 | server | LicenseRef-Stardust-Labs-License | 47.4M | Nether biome/structure overhaul (Forbidden Castle, Sanctum). Stardust now titles it 'Incendium Legacy' and the only 1.21.x build is 5.4.4, marked ALPHA on Modrinth (2024-12), with the previous build named 'UNSUPPORTED_PORT'. Enable only after a stability test. |
| **Integrated Dungeons and Structures** (`idas` / `idas`) | 1.13.7+1.21.1-neoforge | 605375 / 8232359 | both | LicenseRef-All-Rights-Reserved | 31.7M | Integrated Dungeons and Structures: great dark-fantasy dungeons (Labyrinth, Necromancer's Spire, Haunted Manor), BUT its 1.21.1 mods.toml REQUIRES Create, Quark, Supplementaries and Integrated API - only viable if the pack adopts Create. |
| **MES - Moog's End Structures** (`mes-moogs-end-structures` / `mes`) | 2.1.1 | 892382 / 8902211 | server | LGPL-3.0-only | 72.0M | 25 End structures to fill Nullscape's emptiness; optional End content density. |
| **Repurposed Structures (NeoForge/Forge)** (`repurposed-structures-forge` / `repurposed_structures`) | 7.5.22+1.21.1-neoforge | 368293 / 8688394 | server | LGPL-3.0-only | 105.1M | Biome variants of vanilla structures (107 structure ids); large structure count, overlaps YUNG's and T&T - optional. |
| **Structory: Towers** (`structory-towers` / `structory_towers`) | 1.0.17 | 783522 / 8396885 | server | LicenseRef-Stardust-Labs-License | 60.3M | Adds 21 towers/outposts; nice but overlaps Towns and Towers and D&T firewatch towers. |
| **When Dungeons Arise: Seven Seas** (`when-dungeons-arise-seven-seas` / `dungeons_arise_seven_seas`) | 1.0.4 | 953637 / 7142896 | server | LicenseRef-All-Rights-Reserved | 34.4M | Ship/naval dungeons; nice with Aquamirae but adds ocean density - optional. |

### Food, farming & life skills

**Included**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Amendments** (`amendments` / `amendments`) | 1.21-2.2.4 | 896746 / 9357939 | both | LicenseRef-Supplementaries-Team-License-1.1 | 125.3M | Companion to Supplementaries that improves vanilla blocks (lanterns, cauldrons, skulls); no new progression. |
| **Brewin' And Chewin'** (`brewin-and-chewin` / `brewinandchewin`) | 4.5.0+1.21.1-neoforge | 637808 / 8309583 | both | LicenseRef-All-Rights-Reserved | 22.5M | Keg brewing (mead, ales) and cheeses - feeds the tavern fantasy that D&T/WDA taverns and Fellowship sellswords set up. |
| **Farmer's Delight** (`farmers-delight` / `farmersdelight`) | 1.21.1-1.3.4 | 398521 / 8765184 | both | MIT | 267.7M | The expected cooking layer: knives, cooking pot, meals with Comfort/Nourishment buffs that matter in long boss fights; the de-facto standard food mod with a huge addon ecosystem. |
| **Supplementaries** (`supplementaries` / `supplementaries`) | 1.21.1-4.0.2 | 412082 / 9211734 | both | LicenseRef-Supplementaries-Team-License | 261.4M | Vanilla+ utility/decor (quivers, sacks, globes, antique ink, signposts) that gives quests tangible items; also adds the road_sign and galleon structures. |

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Aquaculture 2** (`aquaculture` / `aquaculture`) | 2.7.21 | 60028 / 7901588 | both | LicenseRef-All-Rights-Reserved | 169.0M | Fishing overhaul with Neptunium gear tier; Neptunium competes with Runeborn armaments and NightBeam's Fisherman's Coast already covers fishing flavour. |
| **Cooking for Blockheads** (`cooking-for-blockheads` / `cookingforblockheads`) | 21.1.24+neoforge-1.21.1 | 231484 / 8404453 | both | LicenseRef-All-Rights-Reserved | 201.2M | Kitchen multiblock QoL; useful only if the food layer grows. |
| **Create** (`create` / `create`) | 6.0.10+mc1.21.1 | 328085 / 7963363 | both | LicenseRef-Create-Mod-License | 245.9M | A light Create presence is popular in RPG packs, but it is a 19 MB tech mod with its own progression that pulls focus from a soulslike; only if a 'tinkerer' chapter is wanted (also unlocks IDAS). |
| **Create: Bells & Whistles** (`bellsandwhistles` / `bellsandwhistles`) | v0.4.7-1.21.1 | 905040 / 6299879 | both | GPL-3.0-or-later | 31.0M | Create train decor; only with Create. |
| **End's Delight** (`ends-delight` / `ends_delight`) | 2.6.1+neoforge.1.21.1 [beta] | 662675 / 8335027 | both | MIT | 42.9M | End cooking; only a beta 1.21.1 build. |
| **My Nether's Delight** (`my-nethers-delight` / `mynethersdelight`) | 1.10.4.1 | 1003673 / 8854319 | both | LicenseRef-All-Rights-Reserved | 27.4M | Nether cooking; nice-to-have. |
| **Ocean's Delight** (`oceans-delight` / `oceansdelight`) | 1.0.4 | 841262 / 7939973 | both | MIT | 72.0M | Seafood recipes; small. |

### Decor & building

**Included**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Handcrafted** (`handcrafted` / `handcrafted`) | 4.0.3 | 538214 / 6330030 | both | LicenseRef-Terrarium-Licence | 142.0M | Furniture for player bases and taverns in vanilla style; one decor mod instead of a decor suite. |

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Rechiseled** (`rechiseled` / `rechiseled`) | 1.2.6-neoforge-mc1.21 | 558998 / 8875899 | both | LicenseRef-All-Rights-Reserved | 81.1M | Lighter chisel alternative with connected textures if builders ask for more blocks. |

### Mounts & companions

**Included**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Horseman** (`horseman` / `horseman`) | 1.5.13 | 1082085 / 8734097 | both | MIT | 12.0M | Makes horses a real travel option (hitching, smooth riding, horse inventory switch) for long distance-scaled journeys; MIT, lightweight. |

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Dragon Mounts Remastered** (`dmr` / `dmr`) | 1.9.2 | 975216 / 6974554 | both | LicenseRef-PolyForm-Noncommercial-1.0.0 | 2.6M | Rideable dragons; a flying mount trivialises RPG Mobs' distance-based threat and structure exploration, and the PolyForm-Noncommercial licence needs care. Late-game reward only. |
| **Redomesticate** (`redomesticate` / `redomesticate`) | 1.11.2-1.21.1-neoforge | 1541881 / 9152458 | both | GPL-3.0-only | 68k | Multiloader fork of Domestication Innovation (pet enchantments, pet beds); small (29k MR) and pets are secondary to Fellowship's companions. |

### Atmosphere

**Optional (off by default)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Why |
|---|---|---|---|---|---|---|
| **Serene Seasons** (`serene-seasons` / `sereneseasons`) | 10.1.0.9 [beta] | 291874 / 6182596 | both | LicenseRef-All-Rights-Reserved | 125.7M | Seasons affect crop growth and colours; harmless but adds farming friction - optional. |

### Libraries

**Included (required by the included mods)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Role |
|---|---|---|---|---|---|---|
| **CERBON's API** (`cerbons-api` / `cerbons_api`) | 1.3.0 | 955605 / 6483943 | both | LGPL-3.0-only | 41.8M | Required by Bosses of Mass Destruction. |
| **Cloth Config API** (`cloth-config` / `cloth_config`) | 15.0.140+neoforge | 348521 / 5729127 | both | LGPL-3.0-only | 573.7M | Config library required by Better Combat, Bosses of Mass Destruction and Cristel Lib. |
| **Cristel Lib** (`cristel-lib` / `cristellib`) | neoforge-1.21.1-3.1.7 | 856996 / 8241767 | server | CC-BY-NC-ND-4.0 | 124.7M | Required by Towns and Towers (Cristel Lib declares t_and_t <=1.13.3 incompatible; we use 1.13.11). |
| **Curios API** (`curios` / `curios`) | 9.5.1+1.21.1 | 309927 / 6529130 | both | LGPL-3.0-or-later | 352.5M | Accessory-slot API; required by Cataclysm and used by Artifacts (and Iron's Spells if enabled). |
| **Fragmentum** (`fragmentum` / `fragmentum`) | 5.4.0 | 1123977 / 9202578 | both | LicenseRef-Obscuria-Ecosystem | 6.7M | Obscuria library required by Aquamirae 7.x (replaces Obscure API); bundles Kotlin for Forge 5.3.0 and YACL 3.6.6. |
| **Geckolib** (`geckolib` / `geckolib`) | 4.9.3 | 388172 / 8893490 | both | MIT | 504.1M | Animation library for Mowzie's, Bosses'Rise, BOMD, Born in Chaos, Aquamirae, The Graveyard (and NightBeam's Eclipsed Realm / Skills and Powers). |
| **Lionfish-API** (`lionfish-api` / `lionfishapi`) | 3.1 | 1001614 / 8345326 | both | LGPL-3.0-only | 87.0M | Required by L_Ender's Cataclysm (versionRange 3.1). |
| **Lithostitched** (`lithostitched` / `lithostitched`) | 1.8.1-neoforge-21.1 | 936015 / 9170709 | server | MIT | 124.7M | Worldgen library required by Terralith and Tectonic (jar-in-jars ApolLib). |
| **Moonlight Lib** (`moonlight` / `moonlight`) | 1.21.1-3.7.2 | 499980 / 9122548 | both | LicenseRef-LGPL-with-additional-dependency-clause | 342.9M | Moonlight Lib, required by Supplementaries and Amendments. |
| **playerAnimator** (`playeranimator` / `playeranimator`) | 2.0.4+1.21.1-forge [beta] | 658587 / 7389814 | both | MIT | 199.9M | Animation library required by Better Combat (and by NightBeam's Skills and Powers and Iron's Spells). Only beta builds exist for 1.21.1. |
| **Puzzles Lib** (`puzzles-lib` / `puzzleslib`) | 21.1.66 | 495476 / 9331322 | both | MPL-2.0 | 294.4M | Fuzs library required by Illager Invasion (and Mutant Monsters if enabled). |
| **Resourceful Lib** (`resourceful-lib` / `resourcefullib`) | 3.0.12 | 570073 / 5973188 | both | MIT | 222.6M | Required by Friends&Foes and Handcrafted (and It Takes a Pillage if enabled). |
| **Villager Trading Plus** (`villagerstradingplus` / `villagertradingplus`) | 1.1.1+mc1.21.1-neoforge | 1107609 / 5747126 | both | GPL-3.0-only | 219k | Required by The Graveyard 4.x (version range [1.1.0,2)). |
| **YUNG's API** (`yungs-api` / `yungsapi`) | 1.21.1-NeoForge-5.1.9 | 421850 / n/a | both | LGPL-3.0-only | 225.5M | Required by every YUNG's mod. |

**Optional (only with the optional mod that needs them)**

| Mod (slug / mod id) | NeoForge 1.21.1 build | CF project / file | Side | Licence | Downloads (MR+CF) | Role |
|---|---|---|---|---|---|---|
| **Architectury API** (`architectury-api` / `architectury`) | 13.0.11+neoforge | 419699 / 8492726 | both | LGPL-3.0-only | 462.5M | Required by Simply Swords and Critters and Companions. |
| **Balm** (`balm` / `balm`) | 21.0.66+neoforge-1.21.1 | 531761 / 8969738 | both | LicenseRef-All-Rights-Reserved | 332.3M | Required by Cooking for Blockheads. |
| **Fusion (Connected Textures)** (`fusion-connected-textures` / `fusion`) | 1.3.16-neoforge-mc1.21.1 | 854949 / 9070353 | client | LicenseRef-All-Rights-Reserved | 126.6M | Client-side connected textures, required by Rechiseled. |
| **Fzzy Config** (`fzzy-config` / `fzzy_config`) | 0.7.7+fix1+1.21+neoforge | 1005914 / 9326327 | both | LicenseRef-TDL-M | 141.8M | Required by Simply Swords; requires Kotlin for Forge. |
| **GlitchCore** (`glitchcore` / `glitchcore`) | 2.1.0.2 [beta] | 955399 / 8109792 | both | LicenseRef-All-Rights-Reserved | 100.7M | Optional dependency of Serene Seasons (Modrinth lists it required). |
| **Integrated API** (`integrated-api` / `integrated_api`) | 1.9.1 | 817709 / 9151098 | both | AGPL-3.0-only | 33.2M | Required by IDAS only. |
| **Iron's Lib** (`irons-lib` / `irons_lib`) | 1.21.1-2.3.0 | 1492763 / 9328060 | both | LicenseRef-All-Rights-Reserved | 15.8M | Required by Iron's Spells 'n Spellbooks (range [1.21.1-2,1.21.1-3)). |
| **Kotlin for Forge** (`kotlin-for-forge` / `kotlinforforge`) | 5.12.0 | 351264 / 8335665 | both | LGPL-2.1-only | 265.2M | Required by Fzzy Config (Simply Swords). Fragmentum already jar-in-jars KFF 5.3.0; add the standalone 5.12.0 only if Simply Swords is enabled. |
| **Moog's Structure Lib (moogs_structures)** (`moogs-structure-lib` / `moogs_structures`) | 3.4.2-neoforge-1.21.1 | 1337167 / 9047179 | server | LGPL-3.0-only | 36.9M | Required by Moog's structure packs (MES). |
| **Quark** (`quark` / `quark`) | 4.1-488 | 243121 / 9335735 | both | CC-BY-NC-SA-3.0 | 286.3M | Required by IDAS 1.21.1 only (large vanilla+ mod; would need its own config pass). |
| **Simply Tooltips** (`simply-tooltips` / `simplytooltips`) | 0.1.5 | 1475755 / 8715141 | client | LicenseRef-Timefall-Development-License-1.2 | 5.4M | Client-side tooltip library required by Simply Swords. |
| **SuperMartijn642's Config Lib** (`supermartijn642s-config-lib` / `supermartijn642configlib`) | 1.1.8-neoforge-mc1.21 | 438332 / 5546996 | both | LicenseRef-All-Rights-Reserved | 224.6M | Required by Rechiseled. |
| **SuperMartijn642's Core Lib** (`supermartijn642s-core-lib` / `supermartijn642corelib`) | 1.1.26-neoforge-mc1.21 | 454372 / 9352716 | both | LicenseRef-All-Rights-Reserved | 211.1M | Required by Rechiseled. |
| **YetAnotherConfigLib** (`yacl` / `yet_another_config_lib_v3`) | 3.8.2+1.21.1-neoforge | 667299 / 7437845 | both | LGPL-3.0-or-later | 270.4M | Config lib used optionally by Friends&Foes / It Takes a Pillage and required by Critters and Companions; already jar-in-jar inside Fragmentum (3.6.6). |
| **Zeta** (`zeta` / `zeta`) | 1.1-40 | 968868 / 7980010 | both | CC-BY-NC-SA-3.0 | 83.8M | Required by Quark. |

Jar-in-jar (no separate entry needed): Extensible Enums inside Illager Invasion; Kotlin for Forge 5.3.0 + YACL 3.6.6 inside Fragmentum; ApolLib inside Tectonic/Lithostitched; GreenhouseConfig inside Brewin' And Chewin'; MixinSquared + Sable companion inside Supplementaries; CodecUI inside Moonlight.

## 5. Rejected, with reasons

| Mod (slug) | 1.21.1 NeoForge? | Downloads (MR+CF) | Reason |
|---|---|---|---|
| **Relics** (`relics-mod`) | yes | 68.6M | Levelling relic accessories with their own research/XP system; parallel progression, and the word 'relic' already means Sovereign drops in Runeborn. |
| **Enhanced Celestials** (`enhanced-celestials`) | yes | 47.4M | Blood Moon duplicates NightBeam RPG Mobs' Hunter's Moon (which already doubles rank chances); two lunar-event systems would stack spawns and confuse players. |
| **Alex's Caves (Unofficial Port)** (`alexs-caves-unofficial-port`) | yes | 1.0M | Official Alex's Caves stops at 1.20.1; the 1.21.1 build is an unofficial port on a ported Citadel - too risky for a flagship pack. |
| **Alex's Mobs (Unofficial Port)** (`alexs-mobs-1.21.1`) | yes | 2.4M | Alex's Mobs (Unofficial Port): community port, last update 2026-01-26, needs a separate Citadel port; 90+ animals is bloat next to Naturalist and the bosses layer. |
| **Alex's Mobs Continued** (`alexs-mobs-continued`) | yes | 573k | Second, actively updated port (2026-10-19) on CodxLib; same bloat argument. Prefer this over the other port if fauna is ever expanded. |
| **Enemy Expansion** (`enemy-expansion`) | no | 8.4M | No NeoForge 1.21.1 file (CurseForge-only, older versions). |
| **Ice and Fire: Dragons (CE)** (`ice-and-fire-dragons`) | no | 116.3M | Ice and Fire (Community Edition): no NeoForge 1.21.1 file on CurseForge or Modrinth (latest 1.20.1). |
| **Sculk Horde** (`sculk-horde`) | no | 1.6M | No NeoForge 1.21.1 build (Forge up to 1.20.6), and a world-consuming infection breaks a story pack. |
| **Archers (RPG Series)** (`archers`) | yes | 19.5M | RPG Series class on Spell Engine; ranged skills duplicate Skills and Powers and Fellowship's Ranger; brings ranged-weapon-api. |
| **Ars Nouveau** (`ars-nouveau`) | yes | 120.8M | Whimsical glyph-crafting magic with automation; wrong tone and a fourth magic system next to Runeborn and Skills and Powers. |
| **Goety - The Dark Arts** (`goety`) | yes | 13.1M | Necromancy/dark-arts magic system - on-tone but a full extra magic/progression system (needs Patchouli). |
| **Jewelry (RPG Series)** (`jewelry`) | yes | 20.3M | RPG Series rings/necklaces built around spell_power attributes that do nothing without Spell Engine classes; Artifacts covers accessory loot better. |
| **Paladins & Priests (RPG Series)** (`paladins-and-priests`) | yes | 21.2M | RPG Series class on Spell Engine; duplicates Runeborn's Faith/incantation path and Fellowship's Mender healer role. |
| **Rogues & Warriors (RPG Series)** (`rogues-and-warriors`) | yes | 14.6M | RPG Series class on Spell Engine; duplicates Runeborn's Dexterity/Strength armament paths. |
| **Spell Engine** (`spell-engine`) | yes | 27.6M | Casting framework for the RPG Series; only needed if those classes were taken. |
| **Wizards (RPG Series)** (`wizards`) | yes | 24.1M | RPG Series class on Spell Engine (NeoForge 1.21.1 build exists, 3.1.3). Spell Engine is another casting/class layer duplicating Runeborn origins and Skills and Powers schools; pulls 4+ extra libraries. |
| **Combat Roll** (`combat-roll`) | yes | 52.2M | Duplicates Runeborn's dodge roll (Left Alt, i-frames), and its default key R collides with Runeborn's weapon art (R) and Skills and Powers cast slot 1 (R). |
| **Epic Fight** (`epic-fight`) | yes | 34.3M | Replaces the whole combat/animation model with its own stamina, dodge, guard and skill system: duplicates Runeborn's stamina + dodge roll + weapon arts and is incompatible with Better Combat. |
| **Marium's Soulslike Weaponry** (`mariums-soulslike-weaponry`) | no | 26.2M | No NeoForge 1.21.1 build (Fabric/Forge only; Forge-only jars cannot load on NeoForge). Its Elden-Ring-style boss weapons also duplicate Runeborn's Sovereign relic armaments. |
| **Spartan Weaponry Unofficial** (`spartan-weaponry-unofficial`) | yes | 283k | Unofficial community port (108k MR downloads); its weapon classes duplicate Runeborn's armaments. |
| **Chipped** (`chipped`) | yes | 156.7M | ~10k block variants (bloat) plus Athena CTM; Handcrafted + vanilla is enough for a combat-first pack. |
| **Amplified Nether** (`amplified-nether`) | yes | 20.4M | Incompatible with Incendium, heavy on performance, and the brief is vanilla-first. |
| **Biomes O' Plenty** (`biomes-o-plenty`) | yes | 273.8M | New block palette + TerraBlender/GlitchCore; only beta builds for 1.21.1; overlaps Terralith. |
| **Formations (Structure Library)** (`formations`) | yes | 48.9M | Structure library only needed by Formations content packs, none of which are chosen. |
| **MNS - Moog's Nether Structures** (`mns-moogs-nether-structures`) | yes | 42.8M | Nether filler structures; YUNG's fortresses + Cataclysm/D&T Nether content are enough. |
| **MSS - Moog's Soaring Structures** (`mss-moogs-soaring-structures`) | yes | 25.0M | Floating sky structures - off-tone for a grounded dark-fantasy world. |
| **MVS - Moog's Voyager Structures** (`moogs-voyager-structures`) | yes | 75.9M | Generic overworld structure spam overlapping D&T/Structory/T&T. |
| **Regions Unexplored** (`regions-unexplored`) | yes | 59.1M | Adds a new block/wood palette; conflicts with the vanilla-first brief and doubles Terralith's biome role. |
| **The Aether** (`aether`) | yes | 91.4M | Bright sky dimension - off-tone, and a second dimension chain next to the Eclipsed Realm. |
| **The Undergarden** (`the-undergarden`) | yes | 55.5M | Dark dimension with bosses but beta-only on 1.21.1 and a third extra dimension next to Otherside + Eclipsed Realm. |
| **Waystones** (`waystones`) | yes | 355.7M | Noted for the QoL researcher: Runeborn Ember Shrines already provide named fast-travel points; Waystones would duplicate it. |
| **YUNG's Better Witch Huts** (`yungs-better-witch-huts`) | yes | 88.0M | Conflicts with NightBeam's own 'The Witch Hut' (mod id better_witch_huts, display name 'Better Witch Huts', structure better_witch_huts:witch_hut in swamp/dark forest/plains). YUNG's disables vanilla huts by mixin and adds its own; two 'Better Witch Huts' in the same swamps confuses players and quests. |
| **Croptopia** (`croptopia`) | yes | 57.8M | CurseForge-only NeoForge build; hundreds of crops/foods (item bloat) that duplicate Farmer's Delight. |
| **Domestication Innovation** (`domestication-innovation`) | no | 14.2M | No 1.21.1 build (stops at 1.20.1). Redomesticate is its 1.21.1 fork. |
| **Apotheosis** (`apotheosis`) | yes | 137.1M | Affix loot + gems + boss/elite mobs duplicate Runeborn affinities/tempering, NightBeam loot bags and RPG Mobs ranks; Apothic Attributes re-skins the attribute UI that RAS owns. |
| **Apothic-Enchanting** (`apothic-enchanting`) | yes | 26.0M | Standalone enchanting overhaul (Eterna/Quanta); extra power creep on top of Runeborn's +25 tempering. |
| **Obscure API** (`obscure-api`) | no | 9.5M | Old Aquamirae dependency; no NeoForge 1.21.1 build and no longer needed (Aquamirae 7.x uses Fragmentum). |

## 6. Quest hooks (included content mods)

Ids are taken from each jar's `c:bosses` tag, `data/<ns>/worldgen/structure`, `data/<ns>/advancement` and `assets/<ns>/lang/en_us.json`. Every structure id is in the JSON. Namespace quirks: Bosses'Rise is `block_factorys_bosses`, Born in Chaos is `born_in_chaos_v1`, The Graveyard is `graveyard`, Dungeons and Taverns has mod id `mr_dungeons_andtaverns`, lang namespace `dnt` and structure/advancement namespace `nova_structures`. Towns and Towers has mod id `t_and_t` and structure namespace `towns_and_towers`. Philip's Ruins is `philipsruins`.

Saved language files (`registry/<modid>_en_us.json`) cover every included content mod that ships one. Nullscape, Philip's Ruins, Structory, Towns and Towers, Sparse Structures, YUNG's Bridges and YUNG's Extras ship no `en_us.json`; they are datapack-style or config-only, so their hooks are structure ids only.

- **Artifacts** (`artifacts`)
  - Bosses/elites: `artifacts:mimic`
  - Items: `artifacts:cross_necklace`, `artifacts:flame_pendant`, `artifacts:cloud_in_a_bottle`, `artifacts:crystal_heart`, `artifacts:vampiric_glove`, `artifacts:power_glove`, `artifacts:warp_drive`, `artifacts:night_vision_goggles`

- **Aquamirae** (`aquamirae`)
  - Bosses/elites: `aquamirae:captain_cornelia`, `aquamirae:maze_mother`
  - Structures: `aquamirae:pirate_outpost`, `aquamirae:pirate_shelter`, `aquamirae:pirate_ship`, `aquamirae:shipwreck`, `aquamirae:surface/arch`, `aquamirae:surface/spiral`
  - Items: `aquamirae:frozen_key`, `aquamirae:rune_of_the_storm`, `aquamirae:ship_graveyard_echo`, `aquamirae:shell_horn`, `aquamirae:terrible_upgrade_smithing_template`, `aquamirae:abyssal_upgrade_smithing_template`, `aquamirae:dagger_of_greed`, `aquamirae:tidepiercer`
  - Advancements (FTB Quests advancement tasks): `aquamirae:adventure/find_ice_maze`, `aquamirae:adventure/obtain_frozen_key`, `aquamirae:adventure/survive_the_shipbreaker`
  - Note: 7.x moved from Obscure API to Fragmentum (which jar-in-jars Kotlin for Forge and YACL). The Ice Maze is a frozen-ocean feature, track it via the advancement. Bosses are not in c:bosses.

- **Born in Chaos** (`born_in_chaos_v1`)
  - Bosses/elites: `born_in_chaos_v1:lord_pumpkinhead`, `born_in_chaos_v1:sir_pumpkinhead`, `born_in_chaos_v1:supreme_bonescaller`, `born_in_chaos_v1:nightmare_stalker`, `born_in_chaos_v1:missioner`, `born_in_chaos_v1:dire_hound_leader`, `born_in_chaos_v1:krampus`
  - Structures (31 in total, all in the JSON). Key ones: `born_in_chaos_v1:dark_tower_forest`, `born_in_chaos_v1:infernal_pumpkin`, `born_in_chaos_v1:mound_of_hounds`, `born_in_chaos_v1:firewell`, `born_in_chaos_v1:clown_caravan_plains`, `born_in_chaos_v1:observation_tower_forest`, `born_in_chaos_v1:farm`
  - Items: `born_in_chaos_v1:dark_metal_ingot`, `born_in_chaos_v1:transmuting_elixir`, `born_in_chaos_v1:lord_pumpkinheads_lamp`, `born_in_chaos_v1:nightmare_scythe`, `born_in_chaos_v1:great_reaper_axe`, `born_in_chaos_v1:fangofthe_hound_leader`, `born_in_chaos_v1:seedof_chaos`, `born_in_chaos_v1:soulbane`
  - Note: Mod id born_in_chaos_v1. Lord Pumpkinhead is summoned by using Transmuting Elixir on an Infernal Evil Pumpkin; Sir Pumpkinhead appears 25 Oct-5 Nov. Bosses are NOT in c:bosses - add them via datapack so RPG Mobs treats them as bosses.

- **Bosses of Mass Destruction (Forge/NeoForge)** (`bosses_of_mass_destruction`)
  - Bosses/elites: `bosses_of_mass_destruction:lich`, `bosses_of_mass_destruction:obsidilith`, `bosses_of_mass_destruction:gauntlet`, `bosses_of_mass_destruction:void_blossom`
  - Structures: `bosses_of_mass_destruction:gauntlet_arena`, `bosses_of_mass_destruction:lich_tower`, `bosses_of_mass_destruction:obsidilith_arena`, `bosses_of_mass_destruction:void_blossom`
  - Items: `bosses_of_mass_destruction:soul_star`, `bosses_of_mass_destruction:ancient_anima`, `bosses_of_mass_destruction:blazing_eye`, `bosses_of_mass_destruction:obsidian_heart`, `bosses_of_mass_destruction:void_thorn`, `bosses_of_mass_destruction:crystal_fruit`, `bosses_of_mass_destruction:earthdive_spear`, `bosses_of_mass_destruction:brimstone_nectar`
  - Note: 'lich' here is the Night Lich; The Graveyard also has a graveyard:lich - name quests carefully.

- **Bosses'Rise** (`block_factorys_bosses`)
  - Bosses/elites: `block_factorys_bosses:underworld_knight`, `block_factorys_bosses:infernal_dragon`, `block_factorys_bosses:yeti`, `block_factorys_bosses:sandworm`, `block_factorys_bosses:kraken`
  - Structures: `block_factorys_bosses:dragon_tower`, `block_factorys_bosses:kraken_ship`, `block_factorys_bosses:sandworm_nest`, `block_factorys_bosses:underworld_arena`, `block_factorys_bosses:yeti_hideout`
  - Items: `block_factorys_bosses:underworld_arena_key`, `block_factorys_bosses:ancient_trial_key`, `block_factorys_bosses:knight_sword`, `block_factorys_bosses:dragon_bone`, `block_factorys_bosses:kraken_tooth`, `block_factorys_bosses:kraken_trident`, `block_factorys_bosses:ice_gauntlet`, `block_factorys_bosses:sandworm_gauntlet`

- **Deeper and Darker** (`deeperdarker`)
  - Bosses/elites: `deeperdarker:stalker`
  - Dimensions: `deeperdarker:otherside`
  - Structures: `deeperdarker:ancient_temple`
  - Items: `deeperdarker:heart_of_the_deep`, `deeperdarker:reinforced_echo_shard`, `deeperdarker:warden_carapace`, `deeperdarker:warden_upgrade_smithing_template`, `deeperdarker:sonorous_staff`, `deeperdarker:soul_elytra`, `deeperdarker:resonarium`
  - Advancements (FTB Quests advancement tasks): `deeperdarker:main/enter_otherside`, `deeperdarker:main/find_ancient_temple`, `deeperdarker:main/kill_warden`, `deeperdarker:main/warden_armor`
  - Note: Runeborn already pays a relic for the Warden - Deeper and Darker extends that kill into the Otherside chapter.

- **Friends&Foes (Forge/NeoForge)** (`friendsandfoes`)
  - Bosses/elites: `friendsandfoes:wildfire`, `friendsandfoes:illusioner`, `friendsandfoes:iceologer`
  - Structures: `friendsandfoes:citadel`, `friendsandfoes:iceologer_cabin`, `friendsandfoes:illusioner_shack`, `friendsandfoes:illusioner_training_grounds`
  - Items: `friendsandfoes:wildfire_crown`, `friendsandfoes:wildfire_crown_fragment`, `friendsandfoes:totem_of_freezing`, `friendsandfoes:totem_of_illusion`

- **Illager Invasion** (`illagerinvasion`)
  - Bosses/elites: `illagerinvasion:invoker`, `illagerinvasion:illusioner`
  - Structures: `illagerinvasion:firecaller_hut`, `illagerinvasion:illager_fort`, `illagerinvasion:illusioner_tower`, `illagerinvasion:labyrinth`, `illagerinvasion:sorcerer_hut`
  - Items: `illagerinvasion:hallowed_gem`, `illagerinvasion:primal_essence`, `illagerinvasion:platinum_chunk`, `illagerinvasion:horn_of_sight`, `illagerinvasion:lost_candle`, `illagerinvasion:illusionary_dust`

- **L_Ender's Cataclysm** (`cataclysm`)
  - Bosses/elites: `cataclysm:ignis`, `cataclysm:netherite_monstrosity`, `cataclysm:ender_guardian`, `cataclysm:the_harbinger`, `cataclysm:the_leviathan`, `cataclysm:ancient_remnant`, `cataclysm:maledictus`, `cataclysm:scylla`
  - Structures: `cataclysm:abandoned_spire`, `cataclysm:abandoned_temple`, `cataclysm:abandoned_village`, `cataclysm:acropolis`, `cataclysm:amethyst_nest`, `cataclysm:ancient_factory`, `cataclysm:burning_arena`, `cataclysm:cursed_pyramid`, `cataclysm:desert_occupied_village`, `cataclysm:desert_site`, `cataclysm:desert_temple`, `cataclysm:frosted_prison`, `cataclysm:ruined_citadel`, `cataclysm:soul_black_smith`, `cataclysm:sunken_city`
  - Items: `cataclysm:the_incinerator`, `cataclysm:ignitium_ingot`, `cataclysm:infernal_forge`, `cataclysm:monstrous_horn`, `cataclysm:gauntlet_of_guard`, `cataclysm:void_core`, `cataclysm:wither_assault_shoulder_weapon`, `cataclysm:tidal_claws`, `cataclysm:wrath_of_the_desert`, `cataclysm:soul_render`, `cataclysm:cursium_ingot`, `cataclysm:ceraunus`, `cataclysm:astrape`, `cataclysm:flame_eye`, `cataclysm:monstrous_eye`, `cataclysm:void_eye`, `cataclysm:mech_eye`, `cataclysm:abyss_eye`, `cataclysm:desert_eye`, `cataclysm:cursed_eye`, `cataclysm:storm_eye`
  - Advancements (FTB Quests advancement tasks): `cataclysm:kill_ignis`, `cataclysm:kill_monstrosity`, `cataclysm:kill_ender_guardian`, `cataclysm:kill_harbinger`, `cataclysm:kill_leviathan`, `cataclysm:kill_remnant`, `cataclysm:kill_maledictus`, `cataclysm:kill_scylla`, `cataclysm:kill_all_bosses`
  - Note: Mini-bosses: cataclysm:ender_golem, ignited_revenant, clawdian, coralssus, the_prowler, kobolediator, aptrgangr, wadjet. Licence CC-BY-NC-ND-4.0 (pack redistribution via platform API only).

- **Mowzie's Mobs** (`mowziesmobs`)
  - Bosses/elites: `mowziesmobs:ferrous_wroughtnaut`, `mowziesmobs:frostmaw`, `mowziesmobs:umvuthi`, `mowziesmobs:sculptor`, `mowziesmobs:naga`
  - Structures: `mowziesmobs:frostmaw_spawn`, `mowziesmobs:monastery`, `mowziesmobs:umvuthana_grove`, `mowziesmobs:wrought_chamber`
  - Items: `mowziesmobs:wrought_axe`, `mowziesmobs:wrought_helmet`, `mowziesmobs:ice_crystal`, `mowziesmobs:sol_visage`, `mowziesmobs:earthrend_gauntlet`, `mowziesmobs:sculptor_staff`, `mowziesmobs:naga_fang_dagger`, `mowziesmobs:geomancer_robe`
  - Note: naga is a mini-boss (not in c:bosses). Custom licence (Mowzie's Mobs License) - check its modpack clause before publishing.

- **Naturalist** (`naturalist`)
  - Items: `naturalist:venison`, `naturalist:antler`, `naturalist:bushmeat`, `naturalist:capture_net`, `naturalist:fur`, `naturalist:hide`
  - Note: Quest hook entities: naturalist:bear, naturalist:deer, naturalist:boar, naturalist:alligator, naturalist:komodo_dragon, naturalist:great_white_shark.

- **The Graveyard (Fabric/NeoForge)** (`graveyard`)
  - Bosses/elites: `graveyard:lich`, `graveyard:nightmare`
  - Structures (22 in total, all in the JSON). Key ones: `graveyard:lich_prison`, `graveyard:altar`, `graveyard:crypt`, `graveyard:haunted_house`, `graveyard:large_graveyard`, `graveyard:memorial_tree`, `graveyard:ruins`, `graveyard:overrun_plains_village`
  - Items: `graveyard:vial_of_blood`, `graveyard:corruption`, `graveyard:dark_iron_ingot`, `graveyard:black_bone_staff`, `graveyard:bone_dagger`, `graveyard:sarcophagus`, `graveyard:diary_page`

- **Dungeons and Taverns** (`mr_dungeons_andtaverns`)
  - Structures (97 in total, all in the JSON). Key ones: `nova_structures:tavern_oak`, `nova_structures:illager_manor`, `nova_structures:shrine_combat_tier_1`, `nova_structures:shrine_combat_tier_5`, `nova_structures:undead_crypt`, `nova_structures:creeping_crypt`, `nova_structures:witch_villa`, `nova_structures:lone_citadel`, `nova_structures:remnant_taiga_castle`, `nova_structures:ruin_town`, `nova_structures:nether_keep`, `nova_structures:piglin_donjon`, `nova_structures:end_castle`, `nova_structures:toxic_lair`
  - Advancements (FTB Quests advancement tasks): `nova_structures:adventure/find_tavern`, `nova_structures:adventure/tavern_quest`, `nova_structures:adventure/find_shrine`, `nova_structures:adventure/find_illager_manor`, `nova_structures:adventure/find_witch_villa`, `nova_structures:adventure/kill_all_minibosses`, `nova_structures:end/find_end_castle`, `nova_structures:end/kill_phantom_boss`, `nova_structures:nether/find_keep`

- **Explorer's Compass** (`explorerscompass`)
  - Items: `explorerscompass:explorerscompass`

- **Nature's Compass** (`naturescompass`)
  - Items: `naturescompass:naturescompass`

- **Nullscape** (`nullscape`)
  - Structures: `nullscape:dragon_skeleton`, `nullscape:rift`

- **Philip's Ruins** (`philipsruins`)
  - Structures (17 in total, all in the JSON). Key ones: `philipsruins:lost_soul_city`, `philipsruins:lost_soul_dungeon`, `philipsruins:ancient_crypt`, `philipsruins:ancient_dungeon`, `philipsruins:ocean_fortress`, `philipsruins:rare_ruin`

- **Structory** (`structory`)
  - Structures (15 in total, all in the JSON). Key ones: `structory:abandoned_chapel`, `structory:graveyard`, `structory:old_manor`, `structory:northern_ruin`, `structory:outcast_villager_grassy`, `structory:firetower`

- **Terralith** (`terralith`)
  - Structures (28 in total, all in the JSON). Key ones: `terralith:fortified_village`, `terralith:mage_tower`, `terralith:spire`, `terralith:underground/frosted_dungeon`, `terralith:underground/sunken_tower`, `terralith:witch_hut`, `terralith:glacial_hut`

- **Towns and Towers** (`t_and_t`)
  - Structures (60 in total, all in the JSON). Key ones: `towns_and_towers:village_meadow`, `towns_and_towers:village_swamp`, `towns_and_towers:exclusives/village_tudor`, `towns_and_towers:exclusives/village_swedish`, `towns_and_towers:pillager_outpost_swamp`, `towns_and_towers:mimic_desert`, `towns_and_towers:wreckage_ocean`

- **When Dungeons Arise** (`dungeons_arise`)
  - Structures (40 in total, all in the JSON). Key ones: `dungeons_arise:plague_asylum`, `dungeons_arise:thornborn_towers`, `dungeons_arise:keep_kayra`, `dungeons_arise:illager_fort`, `dungeons_arise:heavenly_conqueror`, `dungeons_arise:heavenly_challenger`, `dungeons_arise:heavenly_rider`, `dungeons_arise:mushroom_mines`, `dungeons_arise:scorched_mines`, `dungeons_arise:undead_pirate_ship`, `dungeons_arise:coliseum`, `dungeons_arise:monastery`, `dungeons_arise:shiraz_palace`, `dungeons_arise:foundry`
  - Advancements (FTB Quests advancement tasks): `dungeons_arise:find_plague_asylum`, `dungeons_arise:find_thornborn_towers`, `dungeons_arise:find_heavenly_conqueror`, `dungeons_arise:find_keep_kayra`, `dungeons_arise:find_illager_fort`, `dungeons_arise:find_undead_pirate_ship`

- **YUNG's Better Desert Temples** (`betterdeserttemples`)
  - Structures: `betterdeserttemples:desert_temple`

- **YUNG's Better Dungeons** (`betterdungeons`)
  - Structures: `betterdungeons:skeleton_dungeon`, `betterdungeons:small_dungeon`, `betterdungeons:small_nether_dungeon`, `betterdungeons:spider_dungeon`, `betterdungeons:zombie_dungeon`

- **YUNG's Better Jungle Temples** (`betterjungletemples`)
  - Structures: `betterjungletemples:jungle_temple`

- **YUNG's Better Mineshafts** (`bettermineshafts`)
  - Structures: `bettermineshafts:mineshaft_acacia`, `bettermineshafts:mineshaft_desert`, `bettermineshafts:mineshaft_dripstone`, `bettermineshafts:mineshaft_ice`, `bettermineshafts:mineshaft_jungle`, `bettermineshafts:mineshaft_lush`, `bettermineshafts:mineshaft_mesa`, `bettermineshafts:mineshaft_mushroom`, `bettermineshafts:mineshaft_oak`, `bettermineshafts:mineshaft_overgrown`, `bettermineshafts:mineshaft_red_desert`, `bettermineshafts:mineshaft_spruce`, `bettermineshafts:mineshaft_spruce_snowy`

- **YUNG's Better Nether Fortresses** (`betterfortresses`)
  - Structures: `betterfortresses:fortress`

- **YUNG's Better Ocean Monuments** (`betteroceanmonuments`)
  - Structures: `betteroceanmonuments:ocean_monument`

- **YUNG's Better Strongholds** (`betterstrongholds`)
  - Structures: `betterstrongholds:stronghold`

- **Brewin' And Chewin'** (`brewinandchewin`)
  - Items: `brewinandchewin:keg`, `brewinandchewin:mead`, `brewinandchewin:strongroot_ale`, `brewinandchewin:tankard`, `brewinandchewin:flaxen_cheese_wedge`

- **Farmer's Delight** (`farmersdelight`)
  - Items: `farmersdelight:cooking_pot`, `farmersdelight:skillet`, `farmersdelight:stove`, `farmersdelight:iron_knife`, `farmersdelight:shepherds_pie`, `farmersdelight:beef_stew`

- **Supplementaries** (`supplementaries`)
  - Structures: `supplementaries:galleon`, `supplementaries:road_sign`
  - Items: `supplementaries:quiver`, `supplementaries:sack`, `supplementaries:globe`, `supplementaries:antique_ink`, `supplementaries:slingshot`, `supplementaries:bomb`, `supplementaries:flute`, `supplementaries:key`

- **Horseman** (`horseman`)
  - Items: `horseman:copper_horn`

Quest hooks for the strongest optional mods, in case they are switched on:

- **The Twilight Forest** (`twilightforest`)
  - Bosses/elites: `twilightforest:naga`, `twilightforest:lich`, `twilightforest:minoshroom`, `twilightforest:hydra`, `twilightforest:knight_phantom`, `twilightforest:ur_ghast`, `twilightforest:alpha_yeti`, `twilightforest:snow_queen`
  - Dimensions: `twilightforest:twilight_forest`
  - Structures (21 in total, all in the JSON): `twilightforest:aurora_palace`, `twilightforest:camp`, `twilightforest:dark_tower`, `twilightforest:fallen_trunk`, `twilightforest:final_castle`, `twilightforest:giant_house`, `twilightforest:hedge_maze`, `twilightforest:hollow_tree`, `twilightforest:hydra_lair`, `twilightforest:knight_stronghold`, `twilightforest:labyrinth`, `twilightforest:large_hollow_hill`, `twilightforest:lich_tower`, `twilightforest:medium_hollow_hill`, `twilightforest:mushroom_tower`, `twilightforest:naga_courtyard`, ...
  - Items: `twilightforest:naga_trophy`, `twilightforest:lich_trophy`, `twilightforest:hydra_trophy`, `twilightforest:fiery_ingot`, `twilightforest:knightmetal_ingot`, `twilightforest:carminite`, `twilightforest:alpha_yeti_fur`, `twilightforest:crown_splinter`

- **Iron's Spells 'n Spellbooks** (`irons_spellbooks`)
  - Bosses/elites: `irons_spellbooks:dead_king`, `irons_spellbooks:fire_boss`
  - Dimensions: `irons_spellbooks:pocket_dimension`
  - Structures: `irons_spellbooks:ancient_battleground`, `irons_spellbooks:catacombs`, `irons_spellbooks:citadel`, `irons_spellbooks:evoker_fort`, `irons_spellbooks:ice_spider_den`, `irons_spellbooks:impaled_icebreaker`, `irons_spellbooks:mangrove_hut`, `irons_spellbooks:mountain_tower`, `irons_spellbooks:pyromancer_tower`
  - Items: `irons_spellbooks:blood_staff`, `irons_spellbooks:arcane_essence`, `irons_spellbooks:citadel_map`, `irons_spellbooks:ancient_battleground_map`, `irons_spellbooks:antiquated_compass`

- **Incendium Legacy** (`incendium`)
  - Structures: `incendium:abandoned_tower`, `incendium:forbidden_castle`, `incendium:infernal_altar`, `incendium:nether_reactor`, `incendium:piglin_village`, `incendium:pipeline`, `incendium:quartz_kitchen`, `incendium:ruined_lab`, `incendium:sanctum`

- **Mutant Monsters** (`mutantmonsters`)
  - Bosses/elites: `mutantmonsters:mutant_zombie`, `mutantmonsters:mutant_skeleton`, `mutantmonsters:mutant_creeper`, `mutantmonsters:mutant_enderman`
  - Items: `mutantmonsters:hulk_hammer`, `mutantmonsters:endersoul_hand`, `mutantmonsters:creeper_shard`

- **Integrated Dungeons and Structures** (`idas`)
  - Structures (84 in total, all in the JSON): `idas:abandoned_lighthouse`, `idas:abandoned_vineyard`, `idas:abandonedhouse`, `idas:ancient_mines`, `idas:ancient_portal/ancient_portal`, `idas:ancient_portal/nether_ancient_portal`, `idas:ancient_statue/ancient_statue_desert`, `idas:ancient_statue/ancient_statue_jungle`, `idas:ancient_statue/ancient_statue_plains`, `idas:animal_den/forest_den`, `idas:animal_den/foxhound_den`, `idas:animal_den/polar_bear_den`, `idas:apothecary_abode`, `idas:ars_nouveau/archmages_tower`, `idas:bazaar`, `idas:bearclaw_inn`, ...

## 7. Compatibility notes (NeoForge 1.21.1)

- **Born in Chaos**: Spawn pressure stacks with RPG Mobs' level scaling; review spawn weights (Born In Configuration / In Control) during balancing.
- **Friends&Foes (Forge/NeoForge)**: Both Friends&Foes and Illager Invasion re-enable and restyle the vanilla Illusioner and add Illusioner structures (shack/training grounds vs tower). Pick one owner: disable F&F's Illusioner in its config. Licence CC-BY-NC-ND-4.0.
- **Illager Invasion**: Illusioner overlap with Friends&Foes (see there).
- **L_Ender's Cataclysm**: Its bosses carry the c:bosses tag; confirm NightBeam RPG Mobs reads that tag so they show a level but are not rank-rolled.
- **Better Combat**: Hard-incompatible with Epic Fight. Runeborn 3.0 ships NO Better Combat weapon_attributes (verified in the jar), so Runeborn's 74 armaments keep vanilla swings unless the pack adds a datapack mapping each Runeborn class to a BC preset (dagger->bettercombat:dagger, katana->katana, greatsword->claymore, colossal sword/great hammer->heavy_axe/hammer, twinblade->twin_blade, reaper->scythe, spear->spear, halberd->halberd, fist->fist, claws->claw, staff->staff). Must be play-tested against Runeborn's per-attack stamina cost.
- **Dungeons and Taverns**: Its minecraft:village_taiga override interacts with Towns and Towers' village tags; its witch_villa / mangrove_witch_hut add more witch content next to NightBeam's The Witch Hut (fine, but avoid 'find the witch hut' quests that match the wrong one).
- **Nullscape**: Not compatible with most End worldgen mods (except Better End); works with YUNG's Better End Island on 1.19+. Must be in the world from creation.
- **Farmer's Delight**: No NightBeam clash: the NightBeam audit excludes Sprout & Soil (unfinished on 1.21.1); Better Farming ++ (optional there) only overlaps in right-click harvesting.
- **Horseman**: Declares incompatibility with HorseBuff.
- **Iron's Spells 'n Spellbooks**: Spell schools and mana duplicate Skills and Powers (Pyromancy/Stormcalling/Tidecalling ~ fire/lightning/ice) and Runeborn FP spells.
- **Shield Expansion**: Its author recommends pairing with Combat Roll (which this pack excludes). Changes vanilla shield behaviour; Fellowship's Bulwark fights sword-and-shield, so test that allies still block correctly.
- **Simply Swords**: Weapon-class overlap with Runeborn; its gem-socket system parallels Runeborn affinities/tempering.
- **Incendium Legacy**: Not compatible with Amplified Nether (per its page).
- **Nullscape + YUNG's Better End Island**: compatible on 1.19+ (YUNG's page). Nullscape is incompatible with most other End terrain mods, so no other End worldgen is included. MES (optional) only adds structures.
- **Tectonic + Terralith**: designed as a pair. Tectonic ships the Terralith-compatible variant inside the mod.
- **Supplementaries** declares Farmer's Delight < 1.3.0 incompatible; the pack uses 1.3.4. **Cristel Lib** declares Towns and Towers <= 1.13.3 incompatible; the pack uses 1.13.11.
- **Dungeons and Taverns** overrides `minecraft:village_taiga`, several vanilla woodland-mansion/archaeology loot tables, and adds `nova_structures:*` enchantments. Tell the loot researcher (Lootr/loot integrations), because these are vanilla loot-table overrides.
- **Better Combat weapon data already shipped** by: Cataclysm (10), Born in Chaos (15), Aquamirae (11), Bosses'Rise (5), Iron's Spells (19, optional), Simply Swords (429, optional). Runeborn: 0.

## 8. Caveats and data gaps

- **Release channels**: playerAnimator (beta only), End's Delight (beta), Serene Seasons and GlitchCore (beta), Incendium (alpha on Modrinth), Undergarden (beta, excluded), Biomes O' Plenty (beta, excluded).
- **Old but only builds**: Dungeons and Taverns v4.4.4 (2024-09), Philip's Ruins 2.0 (2025-01), several YUNG's (2024-10 to 2025-06), Cloth Config 15.0.140 (2024-09) and Resourceful Lib 3.0.12 (2024-12). These are stable, finished 1.21.1 lines.
- **Multi-version jars**: Structory, Structory: Towers and Amplified Nether name their newest file `_26.2_`, but the Modrinth version declares 1.21-1.21.11. Pin `Structory_1.21.x_v1.3.14.jar` if worldgen errors appear.
- **No public Runeborn x Better Combat reports exist** (Runeborn has 3.6k MR downloads). The compatibility claim is based on reading the jars, not on player reports, so it needs an in-house test.
- GitHub issue search is blocked from this environment. Conflict notes come from mod descriptions, mods.toml `incompatible` entries, jar contents and a few web searches: [Nullscape/BEI compatibility](https://modrinth.com/mod/2BwBOmBQ), [Illager Invasion page](https://www.curseforge.com/minecraft/mc-mods/illager-invasion), [Alex's Mobs unofficial port](https://www.curseforge.com/minecraft/mc-mods/alexs-mobs-1-21-1-port).
- CurseForge download totals are cfwidget lifetime totals; Modrinth totals come from the API. The two are summed.

