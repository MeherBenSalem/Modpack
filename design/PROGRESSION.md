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

## Side chapters

| Group | Chapters |
|---|---|
| Paths of the Ashborn | The Ashen Codex (how everything works), The Armory, The Remnant Constellation, The Ashen Company, The Fractured Archive |
| The World Under Ash | Boss Compendium (every boss), The Dungeon Trail, Wayfarer, Bestiary |
| Hearth & Harvest | Hearth & Harvest (food, farming, fishing), Last Light (home building, storage), The Clockwork Path (Create) |
| Ashen Contracts | The Huntmaster's repeatable bounty board |

## Tuning knobs

- Mob curve: `config/remnant_mobs/levels.json`, `ranks.json`
- Runes and costs: `config/runeborn-server.json` (`runeGainMultiplier`, `levelCostMultiplier`)
- Player leveling: `config/ras/settings.json`; gear gates: `config/ras/items_lock.json`
- Bag drop rate: `config/mob_loot_bags/drops.json` (`global_multiplier: 0.75`); bag contents: `src/data/loot_bags.yaml`
- Echo strength: `ECHO_HEALTH_BONUS` / `ECHO_DAMAGE_BONUS` in `kubejs/server_scripts/remnants/echo.js`
