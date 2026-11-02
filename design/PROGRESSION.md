# Progression: how Season 1 plays

One rule set, one curve. Every system below is owned by exactly one mod; overlapping systems are switched off.

| System | Owner | Notes |
|---|---|---|
| Mob levels, ranks, traits, named Remnants, Hunter's Moon | Remnants: RPG Mobs | Runeborn's own mob levels are off (`mobLevelsEnabled: false`); its champions stay on because they carry Sovereign Fragments |
| Player levels (Valor → RPG level → attribute points, the **K** screen, item locks) | Remnants: RPG Stats (RAS) | Diamond tools/armour need attribute level 12, netherite 30 (Attack Power for weapons, Protection for armour) |
| Soulslike layer: runes, Ember Shrines, flasks, stamina, dodge, armaments, weapon arts, spells, Sovereigns | Runeborn | Shrine level-ups also grant RAS levels (the two systems are designed together) |
| Combat feel | Better Combat + Runeborn | Runeborn's 72 armaments get Better Combat movesets by weapon class (`src/data/runeborn_movesets.yaml`) |
| Class layer | Remnants: Skills and Powers | The Remnant Constellation (P), casts on Z/X/C/V, Essence |
| Companions | Remnants: Fellowship | Sellswords hired with gold |
| Loot | Mob LootBags (re-tuned), RPG Mobs rank loot, structure chests (Lootr) | Bags pay runes, stones, shards and tomes (`src/data/loot_bags.yaml`) |
| Travel | Ember Shrines (Overworld), Grace Embers (the Realm) | No Waystones: travel is earned |
| Death | Runeborn (runes stay where you fell), Corpse (items wait in your corpse), the pack's Echo of the Fallen | Kill your Echo to get back to your runes |

## The main story

| Chapter | Levels | Gate in | Key beats | Ends with |
|---|---|---|---|---|
| Prologue: Ashborn | 1–5 | — | Origin, stamina and dodge, runes, first death and Echo, ranks, first Valor | Finding a village |
| Act I: Embers | 5–15 | A village | First Ember Shrine (the Keeper arrives), level up and tempering, shrine travel, first sellsword (the Captain arrives), Elites, loot bags, dungeons, champions and Sovereign Fragments | **The Dusk Rider** (the Smith arrives) |
| Act II: The Hunt | 15–30 | Dusk Rider | Hunter's Moon, Champions, the first Remnant, the Labyrinths, the Arcane Spire, choosing a path, Crown Shards; optional Frostmaw and Rimefrost Vaults | **Varghast**, **Sylvara** |
| Act III: The Deep | 30–50 | Sylvara | Ancient City and the Warden, ocean monuments and the Elder Guardian, the Ancient Remnant, the Cursed Keep; optional Otherside, Leviathan, Kraken, Abyssal Halls | **Kaelthar**, **Ysolde** |
| Act IV: Ash and Crown | 50–70 | Ysolde | The Nether, fortresses, the Wither (keep the star), netherite, the stronghold, the End and the Dragon (bottle its breath); optional Ignis, Netherite Monstrosity, Underworld Knight, Infernal Bastille | **Morgrath**, **Vaelorn** |
| Act V: The Eclipsed Realm | 70+ | Vaelorn | Eclipse Shard and Waygate, graces, the Burial Guardian and Crypt Key, Memory Shards and the Lens | **Gravebound Warden**, **Forgotten Watcher**, **Ossukage**, **The Hollow Sovereign** |
| Epilogue: First Light | — | Hollow Sovereign | The sun returns; the Season 2 hook | — |

Each Sovereign's first defeat on a world rekindles one of eight embers on the **Long Eclipse** bar and gives every
player a permanent heart.

## The Ember Forge: one progression for every mod

Combat progress (levels, runes, armaments) was never the problem; crafting was. Storage, Create, wands and compasses
were all free from day one, and the two storage families (Sophisticated and OmniVault) ran side by side without ever
touching. The Ember Forge ties every one of them to the story. Source: `src/progression.yaml`, compiled by
`tools/build_progression.py` into `kubejs/server_scripts/remnants/forge.js` (and the items' startup/client scripts),
which also checks that every id exists and every material can be obtained.

| Tier | Opens after | Seal (crafted once, stays in the grid) | Alloy | Create machine | Replaces |
|---|---|---|---|---|---|
| I | First Ember Shrine | — | **Ashen Alloy**: 2 iron, 2 andesite alloy, Faded Rune → 3 | Mixer | iron |
| II | The Dusk Rider | **Seal of Dusk**: his relic, 4 Fragments, 4 Ashen | **Duskforged Ingot**: 4 Ashen, 2 golden sheets, Remnant Shard, Tempering Stone II → 4 | Press | gold |
| III | Varghast, Sylvara | **Seal of the Hunt**: both relics, 4 Fragments, 2 Duskforged, a Roast Chicken feast | **Moonsilver**: 2 Duskforged, 2 diamond, 3 amethyst, Lustrous Stone I → 2 blend, blasted | Blast furnace | diamond |
| IV | Kaelthar, Ysolde, the Warden | **Seal of the Deep**: both relics, Heart of the Deep, 2 Moonsilver, 3 Fragments, Flaxen Cheese Wheel | **Deepsteel**: 4 Moonsilver, Reinforced Echo Shard, 2 prismarine crystals, Lustrous Stone III → 4 blend, haunted | Fan through soul fire | netherite |
| V | Morgrath, Vaelorn, Wither, Dragon | **Seal of Ash**: both relics, Nether Star, dragon's breath, 2 Deepsteel, 2 Fragments, Steak Dinner | **Sunforged**: 4 Deepsteel, netherite, 2 blaze powder, Lustrous Stone VI → 4 blend, + glowstone | Heated mixing (blaze burner) | — |
| VI | The Eclipsed Realm | — | **Eclipse Core**: 4 Sunforged, 4 Grave Iron, 4 Royal Soul Fragments, Eclipse Shard | Mechanical crafting | nether star |

A Sovereign leaves one relic: trade it for its armament at a shrine, or bind it into a seal. Its sigil calls it again
for a second one. Every seal also takes a dish from the Hearth's kitchens, so cooking is part of the road too.

**What the tiers gate**

- **Story order.** Each Sovereign's sigil needs the seal of the act before (the Dusk Rider's needs Ashen Alloy), and
  the Eclipse Shard needs Sunforged and the Seal of Ash. The quest book mirrors it: the Ember Forge chapter's seals
  depend on the act bosses, and the next act's Sovereign quests depend on the seals.
- **Storage, interlocked.** Every Sophisticated Backpacks / Sophisticated Storage / OmniVault recipe is rebuilt with
  the tier materials (copper → Create copper sheets, iron → Ashen, gold → Duskforged, diamond → Moonsilver,
  netherite → Deepsteel, storage blocks one tier higher, nether stars → Eclipse Core). On top of that the two
  families need each other: a backpack starts as a Supplementaries Sack; OmniVault drawers are built on Sophisticated
  barrels; the OmniVault Logic Processor (Duskforged) runs the Sophisticated Controller and every advanced
  Sophisticated upgrade; the Storage Hub is built around a Sophisticated Controller; the Crafting Terminal needs a
  backpack Crafting Upgrade; the Wireless Terminal needs a Storage Link; OmniVault backpacks are rebuilt Sophisticated
  backpacks. The Vaults chapter walks the ladder.
- **Create** is required now (the alloys come out of its machines), and Create's own brass age still needs a blaze
  from the Nether.
- **Gear and tools.** Vanilla diamond gear takes a Duskforged Ingot; building wands follow the tiers (iron Ashen,
  diamond Moonsilver, netherite Deepsteel, infinity an Eclipse Core); Nature's Compass needs Ashen, the Explorer's
  Compass Duskforged.
- **Omnium without the Nether.** A Create mixing recipe makes Omnium dust from amethyst, redstone and a Remnant
  Shard, so Tier II storage doesn't wait for Nether quartz.

**How long it takes (one player, first run)**

| Part | Levels | Hours | What eats the time |
|---|---|---|---|
| Prologue | 1–5 | 2–3 | the Threshold, first death, the first village |
| Act I: Embers | 5–15 | 10–12 | shrines, a Create mixer line, Ashen Alloy, six Fragments, the Dusk Rider |
| Act II: The Hunt | 15–30 | 14–16 | the Seal of Dusk (a second Rider fight if you took the glaive), presses, two Sovereigns, a feast |
| Act III: The Deep | 30–50 | 16–18 | Ancient City and the Warden, monuments, Moonsilver, cheese, two Sovereigns |
| Act IV: Ash and Crown | 50–70 | 18–20 | the Nether and a blaze burner, soul fire haunting, Wither, Dragon, two Sovereigns |
| Act V: The Eclipsed Realm | 70+ | 14–16 | Sunforged, the Realm's four bosses, Grave Iron and Royal Soul Fragments, the Eclipse Core |
| **Total** |  | **≈ 75–85** | plus the side chapters, contracts and optional bosses |

## RPG Stats gates

`src/stat_locks.yaml` (compiled by `tools/build_stat_locks.py` into `config/ras/`) puts gear on the K screen's
attributes, following the acts so a player who spends points evenly meets each gate about when the item shows up:
weapons and tools need **Attack Power**, guns and bows **Attack Speed**, armour **Protection**, anything that flies
**Agility** (jetpack 10, elytra 15, soul elytra 22), compasses and the Fortune Talisman **Exploration**, gauntlets
and the heaviest hammers **Fortitude**. Thresholds: Act I up to 6, Act II 8-14, Act III 14-24, Act IV 24-32,
Act V 32-40. Modded ores follow diamond's level gate (titanium 10, diamond-tier ores 12, cobalt 20, ancient debris
30, orichalcum 32). Level-ups pay the pack's own economy (runes every level, a tempering stone every 5 levels, a
lustrous stone every 10) instead of RPG Stats' default diamonds and diamond armour, which skipped the Ember Forge.

## Side chapters

| Group | Chapters |
|---|---|
| Paths of the Ashborn | The Ashen Codex (how everything works), The Armory, The Remnant Constellation, The Ashen Company, The Fractured Archive |
| The World Under Ash | Boss Compendium (every boss), The Dungeon Trail, Wayfarer, Bestiary |
| The Long Eclipse | The Ember Forge (the six alloys and four seals that gate everything) sits after the Prologue |
| Hearth and Harvest | Hearth and Harvest (food, farming, fishing), The Ash Garden (Sprout & Soil), Last Light (home, sacks, wands, the village), The Clockwork Path (Create; required for the Forge), The Vaults (Sophisticated and OmniVault, one interlocked ladder) |
| Ashen Contracts | The Huntmaster's repeatable bounty board |

## Tuning knobs

- Mob curve: `config/remnant_mobs/levels.json`, `ranks.json`
- Runes and costs: `config/runeborn-server.json` (`runeGainMultiplier`, `levelCostMultiplier`)
- Player leveling: `config/ras/settings.json`; gear gates: `config/ras/items_lock.json`
- Bag drop rate: `config/mob_loot_bags/drops.json` (`global_multiplier: 0.75`); bag contents: `src/data/loot_bags.yaml`
- Forge costs and what each tier gates: `src/progression.yaml` (then `python3 tools/build_progression.py`)
- Echo strength: `ECHO_HEALTH_BONUS` / `ECHO_DAMAGE_BONUS` in `kubejs/server_scripts/remnants/echo.js`
