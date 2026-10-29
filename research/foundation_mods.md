# Remnants | The Modpack, Season 1: foundation mods

*NeoForge 1.21.1 · foundation layer only (performance, quality of life, UI, quests and scripting, multiplayer, menus, juice). Checked 2026-10-29 against the Modrinth API (`loaders=["neoforge"]`, `game_versions=["1.21.1"]`) and CurseForge through CFWidget. The data behind this page is in `foundation_mods.json`.*

## Verdict

**77 jars ship by default (53 mods and 24 required libraries), 37 are opt-in toggles, and 54 were rejected**, from 168 candidates checked.

That is 7 above the ~70 target. The overshoot comes from three library chains the pack wants anyway: FTB Quests needs FTB Library, FTB Teams and Architectury; Easy NPC needs its Core and Config UI modules; Loot Beams needs Nirvana Lib, Common Network, Fzzy Config and Kotlin for Forge. The lean option at the end of this page gets back to 70.

Five decisions shape everything else.

1. **Rendering: Sodium 0.8.13 with Iris 1.8.14-beta.1.** Sodium 0.8 was backported to 1.21.1 in 2026, and Iris 1.8.14-beta.1 requires exactly Sodium 0.8.13. Sodium 0.8 is incompatible with "Sodium Options API" and every mod built on it, according to Sodium's own release notes. If a gameplay mod still needs Sodium 0.6, switch the pair together to Sodium 0.6.13 + Iris 1.8.12.
2. **Quests: FTB Quests, which makes this a CurseForge-first pack.** FTB mods are All Rights Reserved (Feed The Beast Ltd) and are not published on Modrinth, so they can neither be linked from a .mrpack nor placed in its overrides. This matches NightBeam's audience: about 85% of the studio's downloads come from CurseForge. The only Modrinth-hosted alternative is Odyssey Quests (formerly Heracles; MIT, beta).
3. **Recipe viewer: JEI only, no EMI.** Nearly every 1.21.1 content mod ships a JEI plugin, and EMI can only show those plugins when JEI is also installed.
4. **Inventory sorting: Client Sort instead of Inventory Profiles Next.** A 1.21.1 pack reported an IPN crash on middle-click pick-block in multiplayer that is still present in the latest 1.21.1 build. Client Sort sorts through vanilla click packets and needs no server mod.
5. **No third-party minimap.** NightBeam already ships "Remnants | Advanced Minimap & Waypoints", which supports NeoForge 1.21.1 and is needed on both sides. Xaero's, JourneyMap and the FTB Chunks minimap would duplicate it.

**Run NeoForge 21.1.265** (the newest 21.1.x on maven.neoforged.net). FTB Quests 2101.1.37 is built against 21.1.213, so that is the floor.

## What ships by default

Each entry gives the newest NeoForge 1.21.1 release on Modrinth, then the CurseForge project and file ID, then the side and the licence.

Side follows Modrinth's definitions. A **server** mod, such as Leaves Be Gone, LootJS or NetherPortalFix, still ships in the client pack, because single-player runs an integrated server.

### Performance (and core fixes)

- **Sodium** — MR `mc1.21.1-0.8.13-neoforge` · CF 394468/8756580 · client · `LicenseRef-Polyform-Shield-1.0.0`  
  Official CaffeineMC NeoForge build; 0.8.13 is the 2026 backport of Sodium 0.8 to 1.21.1 (+up to 115% world-render FPS vs 0.6). Pin the pair Sodium 0.8.13 + Iris 1.8.14-beta.1. PolyForm Shield licence: reference it from Modrinth or CF; never rehost it. Sodium 0.8 breaks anything built on 'Sodium Options API'; if a gameplay mod still needs Sodium 0.6, fall back to Sodium 0.6.13 + Iris 1.8.12 together.
- **Iris Shaders** — MR `1.8.14-beta.1+1.21.1-neoforge` · CF 455508/8242804 · client · `LGPL-3.0-only`  
  Official Iris for NeoForge (Oculus is dead on 1.21.1). Shaders stay off by default; it is a client toggle. Version 1.8.14-beta.1 is the only Iris that accepts Sodium 0.8.13 (it pins that exact Sodium version). Modrinth marks it release, CurseForge marks the same jar beta: use CF file 8242804, not CF's newest 'release' 1.8.12, which needs Sodium 0.6.13.
- **Sodium Extra** — MR `mc1.21.1-0.9.5+neoforge` · CF 447673/9324102 · client · `LGPL-3.0-only`  
  Extra video toggles (FPS overlay, fog, particles/animations, etc.). The 0.9.x line targets Sodium 0.8 on 1.21.1.
- **Lithium** — MR `mc1.21.1-0.15.4-neoforge` · CF 360438/8330365 · both · `LGPL-3.0-only`  
  Official NeoForge builds since 0.14 (October 2024). General game-logic and server-tick optimisation, used on both sides and safe in vanilla-like RPG packs.
- **ModernFix** — MR `5.27.27+mc1.21.1` · CF 790626/9309399 · both · `LGPL-3.0-only`  
  Faster launch, lower memory, many bug and leak fixes. Its 1.21.1 builds are actively updated (2026-10).
- **FerriteCore** — MR `7.0.3-neoforge` · CF 429235/7524151 · both · `MIT`  
  Cuts memory use of blockstates and models. Essential in any pack with many blocks.
- **ImmediatelyFast** — MR `1.6.15+1.21.1-neoforge` · CF 686911/9165518 · client · `LGPL-3.0-or-later`  
  Speeds up immediate-mode rendering (HUD, text, entities). Recent builds fix Iron's Spells cooldown rendering, which matters if the magic layer uses Iron's.
- **Entity Culling** — MR `1.11.3` · CF 448233/9100286 · client · `LicenseRef-tr7zw-Protective-License`  
  Skips rendering entities and block entities that are hidden behind walls. Large win in mob-heavy RPG scenes. The tr7zw licence allows Modrinth and CurseForge modpacks.
- **More Culling** — MR `1.0.10` · CF 630104/8833217 · client · `GPL-3.0-only`  
  Extra culling for leaves, item frames, signs and similar. 1.0.8 fixed the crash with Sodium 0.8 and 1.0.7 fixed an Epic Fight incompatibility. Needs Cloth Config.
- **AllTheLeaks** — MR — · CF 1091339/8943912 · both · `unknown (CurseForge-only; not stated via CFWidget)`  
  Memory-leak fixes for NeoForge, vanilla and popular mods (by Uncandango; about 80M CurseForge downloads). It matters for long co-op sessions. Available on CurseForge only, so it cannot be referenced by URL in a .mrpack. In a Modrinth build, drop it unless the licence allows bundling it in overrides (no licence was visible through CFWidget).
- **Leaves Be Gone** — MR `v21.1.1-1.21.1-NeoForge` · CF 686435/8036398 · server · `MPL-2.0`  
  Fast leaf decay (server-side, Fuzs). Pairs with FTB Ultimine tree chopping. Uses Puzzles Lib.
- **Clumps** — MR `19.0.0.1` · CF 256717/5623731 · both · `MIT`  
  Merges XP orbs, which helps when RPG mobs and bosses drop large amounts of XP. Tiny.
- **spark** — MR `1.10.124-neoforge-1.21.1` · CF 361579/6225208 · both · `GPL-3.0-only`  
  Profiler (/spark profiler, /spark health). Needed to diagnose lag reports from players and servers.
- **Dynamic FPS** — MR `3.11.4` · CF 335493/7546938 · client · `MIT`  
  Throttles FPS when the game window is unfocused or minimised. Saves battery and heat on laptops. Cloth Config is optional and provides its config screen.
- **Packet Fixer** — MR `3.3.1` · CF 689467/7221528 · both · `MIT`  
  Raises packet and NBT size limits that big packs hit (full backpacks, large quest books, loot NBT). Prevents 'packet too big' disconnects in co-op.
- **Cloth Config API** *(library)* — MR `15.0.140+neoforge` · CF 348521/5729127 · both · `LGPL-3.0-only`  
  Library: required by More Culling, Client Sort and SRDP; optional config screen for Dynamic FPS, Chat Heads and others.

### Recipe, info and UI

- **Just Enough Items (JEI)** — MR `19.64.0.455` · CF 238222/9205121 · both · `MIT`  
  Recipe viewer. Chosen over EMI because nearly every 1.21.1 content mod (magic, combat, RPG) ships a JEI plugin, FTB XMod Compat and Sophisticated integrate with JEI, and JEI alone costs one library instead of EMI+JEI running side by side. Newest release is 19.64.0.455. The 19.70 betas exist, and since 19.55 JEI requires MezzConfig.
- **MezzConfig** *(library)* — MR `0.6.9` · CF 1689768/9318719 · both · `MIT`  
  Library: required by JEI 19.55+ (mezz's config lib). Only beta builds exist (0.6.9).
- **Jade** — MR `15.10.6+neoforge` · CF 324717/8591319 · both · `CC-BY-NC-SA-4.0`  
  Shows what you are looking at (blocks, entities, mob health) and is the standard info HUD. CC-BY-NC-SA: fine in a free modpack, and the non-commercial clause matters only if the pack itself is sold. Configure its entity health display to avoid duplicating Remnants RPG Mobs' bars.
- **AppleSkin** — MR `3.0.9+mc1.21` · CF 248787/7854442 · both · `Unlicense`  
  Food/saturation preview. Works client-only; the server copy syncs exact saturation. Ships on both sides.
- **Mouse Tweaks** — MR `1.21-2.26.1-neoforge` · CF 60089/5637846 · client · `BSD-3-Clause`  
  Drag and scroll-wheel item transfer. A universal staple.
- **Client Sort** — MR `3.89.2+1.21.1` · CF 1049891/8978780 · both · `Apache-2.0`  
  Inventory and container sorting through vanilla click packets, so it works on any server without a server mod. Configurable buttons and hotkeys. Chosen over Inventory Profiles Next. Needs Cloth Config.
- **Controlling** — MR `19.0.5` · CF 250398/6368976 · client · `MIT`  
  Searchable keybind menu with conflict view. Essential with many keybinds. Needs Searchables.
- **Searchables** *(library)* — MR `1.0.2` · CF 858542/5831692 · client · `MIT`  
  Library: required by Controlling.
- **Polymorph** — MR `1.1.0+1.21.1` · CF 388800/6794589 · both · `LGPL-3.0-or-later`  
  Resolves recipe conflicts between mods by letting players pick the output. A safety net in a pack assembled from many content mods. Needed on both sides.
- **Enchantment Descriptions** — MR `21.1.11` · CF 250419/8693034 · both · `LGPL-2.1-only`  
  Shows what each enchantment does in tooltips, which helps when the gameplay layer adds many enchantments. Needs Bookshelf + Prickle (shared with AttributeFix and Open Loader).
- **Bookshelf** *(library)* — MR `21.1.81` · CF 228525/7606240 · both · `LGPL-2.1-only`  
  Library: required by Enchantment Descriptions (and AttributeFix / Open Loader if enabled).
- **Prickle** *(library)* — MR `21.1.11` · CF 1023259/6961457 · both · `LGPL-2.1-only`  
  Library (Darkhax config/JSON lib): required by Enchantment Descriptions.
- **Legendary Tooltips** — MR `1.5.5` · CF 532127/6400660 · client · `CC-BY-NC-ND-4.0`  
  Rarity- and tag-driven tooltip frames, the RPG 'legendary item' look. Fully data-driven so the pack can style NightBeam gear tiers. CC-BY-NC-ND: fine to reference in a free pack; never modify or rehost it.
- **Item Borders** — MR `1.2.5` · CF 513769/5591010 · client · `CC-BY-NC-ND-4.0`  
  Rarity-coloured slot borders, consistent with Legendary Tooltips (same author and libraries). An optional integration of Sophisticated Backpacks.
- **Equipment Compare** — MR `1.3.13` · CF 502561/6375501 · client · `CC-BY-NC-ND-4.0`  
  Shows the currently equipped item next to a hovered weapon or armor tooltip. Core RPG gear-decision QoL.
- **Iceberg** *(library)* — MR `1.3.2` · CF 520110/6423863 · both · `CC-BY-NC-ND-4.0`  
  Library: required by Legendary Tooltips, Item Borders and Equipment Compare.
- **Prism** *(library)* — MR `1.0.11` · CF 638111/6372979 · client · `CC-BY-NC-ND-4.0`  
  Library: required by Legendary Tooltips and Item Borders.
- **Shoulder Surfing Reloaded** — MR `1.21.1-5.2.0+neoforge` · CF 243190/9013811 · client · `MIT`  
  Over-the-shoulder third-person camera popular in RPG and soulslike packs (MIT, active). Declares Better Third Person incompatible. Coordinate with the combat layer: SSR 1.21.1 disables outdated Epic Fight mixins, and the 'SSR Camera Fixes & Additions' bridge (Epic Fight, Better Combat, Iron's Spells) only supports SSR 4.x, not 5.x. Pin SSR to match the combat mod.
- **Not Enough Animations** — MR `1.12.6` · CF 433760/8925075 · client · `LicenseRef-tr7zw-Protective-License`  
  Third-person player animations (eating, maps, ladders), which matter with a shoulder camera. Client-only. The tr7zw licence allows modpacks.
- **Puzzles Lib** *(library)* — MR `21.1.66` · CF 495476/9331322 · both · `MPL-2.0`  
  Library (Fuzs): required by Leaves Be Gone, plus Pick Up Notifier and Overflowing Bars if enabled.

### Quests, story and scripting infrastructure

- **FTB Quests** — MR — · CF 289412/9298629 · both · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Quest book backbone: chapters, rich text and images for story, team-shared progress through FTB Teams, reward tables, and KubeJS/stage hooks through FTB XMod Compat. CurseForge only, All Rights Reserved (Feed The Beast Ltd), not on Modrinth, so the pack must be published on CurseForge first (which matches NightBeam's 85%-CurseForge audience). A Modrinth .mrpack can only link users to CurseForge for the FTB jars. The Modrinth-friendly alternative is Odyssey Quests.
- **FTB Library** *(library)* — MR — · CF 404465/9350706 · both · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Library: required by FTB Quests, FTB Teams, FTB XMod Compat, FTB Ultimine (and FTB Chunks / FTB Essentials if enabled). CurseForge only, ARR.
- **FTB Teams** *(library)* — MR — · CF 404468/8724782 · both · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Library and party system: shared quest progress for co-op parties (and shared claims if FTB Chunks is enabled). CurseForge only, ARR.
- **FTB XMod Compat** — MR — · CF 889915/9344504 · both · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Bridges FTB Quests to KubeJS (custom tasks and rewards, stages), JEI (recipe lookups from quests) and Waystones. Story scripting needs it. CurseForge only, ARR.
- **Architectury API** *(library)* — MR `13.0.11+neoforge` · CF 419699/8492726 · both · `LGPL-3.0-only`  
  Library: required by FTB Quests, FTB Library, FTB Teams, FTB XMod Compat and FTB Ultimine (and Simple Discord Rich Presence).
- **Patchouli** — MR `1.21.1-93-neoforge` · CF 306770/7730942 · both · `CC-BY-NC-SA-3.0`  
  In-game lore and guide book, written as JSON in a resource or data pack (no Java). Fits a story codex and is widely used by magic and content mods. CC-BY-NC-SA-3.0: modpack use is fine.
- **Easy NPC (Bundle)** — MR `7.17.1` · CF 559312/9310929 · both · `MIT`  
  Story NPCs with dialog trees, trades, actions and commands, with no coding (MIT, very active 2026-10). The bundle jar only installs the modules: Easy NPC Core and Config UI are separate required jars.
- **Easy NPC: Core** *(library)* — MR `7.17.1` · CF 1308987/9310906 · both · `MIT`  
  Library/module: required by Easy NPC.
- **Easy NPC: Config UI** *(library)* — MR `7.17.1` · CF 1214728/9310917 · both · `MIT`  
  Module: required by Easy NPC (config tools and required networking).
- **FancyMenu** — MR `3.9.14-1.21.1-neoforge` · CF 367706/9002957 · both · `LicenseRef-DSMSLv3.1`  
  Custom main menu and other screens (branding, buttons, background video and audio) for the 'Remnants | The Modpack' look. Needs Konkrete + Melody. The DSMSL licence allows modpacks only as a mod reference downloaded from the official source. Never ship the jar inside pack files or a server pack; it is server-optional, so leave it out of the server zip.
- **Drippy Loading Screen** — MR `3.1.5-1.21.1-neoforge` · CF 511770/8552907 · client · `LicenseRef-DSMSLv3`  
  Custom world-loading screen built with the FancyMenu editor. Pair with FancyMenu. A separate 'Drippy Early Loading Module' exists for NeoForge's early window but isn't needed. DSMSL licence: reference it only, never bundle it.
- **Konkrete** *(library)* — MR `1.9.9-1.21-neoforge` · CF 410295/5453385 · both · `Apache-2.0`  
  Library: required by FancyMenu, Drippy and Just Zoom.
- **Melody** *(library)* — MR `1.0.10-1.21-neoforge` · CF 938643/5453382 · client · `MIT`  
  Library: required by FancyMenu and Drippy (audio).
- **Default Options** — MR `21.1.8+neoforge-1.21.1` · CF 232131/8498229 · client · `LicenseRef-All-Rights-Reserved`  
  Ships default options.txt, keybinds and server list without overwriting user changes on updates. Also enables Fresh Animations and other bundled resource packs by default. Needs Balm.
- **KubeJS** — MR `2101.7.2-build.377` · CF 238086/8843626 · both · `LGPL-3.0-only`  
  Scripting backbone: recipes, tags, item tweaks, events, player stages, and loading the pack's own data and assets from kubejs/data and kubejs/assets. Build 377 requires Rhino and Better Advanced Tooltips.
- **Rhino** *(library)* — MR `2101.2.7-build.85+Rhino-1.21` · CF 416294/8218748 · both · `MPL-2.0`  
  Library: JavaScript engine required by KubeJS.
- **Better Advanced Tooltips** *(library)* — MR `2101.1.0-build.5` · CF 1637623/8576077 · both · `MIT`  
  Library: new required dependency of KubeJS 2101.7.2 build 374+ (Lat). Shows tag and component tooltips in F3+H.
- **LootJS** — MR `1.21.1-3.7.0+neoforge` · CF 570630/8009262 · server · `LGPL-3.0-only`  
  KubeJS addon for loot-table modification (boss drops, chest tiers, per-biome loot). Server-side logic; ships in the client pack too for single-player.
- **Crash Assistant** — MR `1.11.12` · CF 1154099/8636685 · client · `LicenseRef-LicenseRef-KostromDan-MML-1.1.3`  
  Friendly crash and startup-failure GUI with log upload and 'what changed vs the official modlist' detection. Cuts pack-support load. The KostromDan licence explicitly allows use in modpacks without asking, and prefers that the jar be downloaded from CF or Modrinth.
- **Better Compatibility Checker** — MR `21.1.8` · CF 551894/7404415 · both · `LicenseRef-All-Rights-Reserved`  
  Shows the pack name and version in the server list and warns about client/server version mismatches. Essential for co-op.

### Storage and travel

- **Sophisticated Backpacks** — MR `1.21.1-3.26.17.2232` · CF 422301/9341438 · both · `LicenseRef-All-Rights-Reserved`  
  Upgradeable backpacks (pickup, magnet, feeding, crafting, sorting), the modern staple. Chosen over Traveler's Backpack because its upgrades are configurable, it sorts natively and it integrates with JEI, Item Borders and Curios. ARR: reference it from CF or Modrinth and do not rehost.
- **Sophisticated Core** *(library)* — MR `1.21.1-1.5.19.2434` · CF 618298/9341397 · both · `LicenseRef-All-Rights-Reserved`  
  Library: required by Sophisticated Backpacks and Sophisticated Storage.
- **Waystones** — MR `21.1.46+neoforge-1.21.1` · CF 245755/8969751 · both · `LicenseRef-All-Rights-Reserved`  
  Fast-travel network (works as a soulslike 'bonfire' map). FTB XMod Compat links it to quests. Needs Balm.
- **Balm** *(library)* — MR `21.0.66+neoforge-1.21.1` · CF 531761/8969738 · both · `LicenseRef-All-Rights-Reserved`  
  Library (BlayTheNinth): required by Waystones, Default Options and NetherPortalFix.
- **Lootr** — MR `1.21.1-1.11.38.127` · CF 361276/8968561 · both · `MIT`  
  Per-player loot in every chest and loot container, essential for co-op: each player gets their own dungeon and boss loot.
- **Corpse** — MR `neoforge-1.21.1-1.1.22` · CF 316582/9289316 · both · `LicenseRef-All-Rights-Reserved`  
  On death your items stay in a corpse entity at the death spot: a soulslike 'recover your bloodstain' loop that does not place blocks or need a valid grave position. Picked over GraveStone. The gameplay layer may replace it with its own death-penalty system.

### Multiplayer

- **FTB Ultimine** — MR — · CF 386134/8231400 · both · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Vein mining (hold a key). Opt-in per action, with hunger cost and tool/tag limits configurable. Covers ores and trees, reuses FTB Library and Architectury, and cuts gathering chores in a combat-focused RPG. Requires the server side. CurseForge only, ARR.
- **NetherPortalFix** — MR `21.1.1+neoforge-1.21.1` · CF 241160/5623547 · server · `LicenseRef-All-Rights-Reserved`  
  Makes portals return to the portal you came from in multiplayer. Server-side, tiny, uses Balm.
- **Chunky** — MR `1.4.23` · CF 485681/6383261 · both · `GPL-3.0-only`  
  World pre-generation. Pre-generate the spawn region on servers and for single-player to avoid worldgen stutter from heavy structure and biome mods. Distant Horizons respects it.
- **Ping Wheel** — MR `1.12.2` · CF 734339/7996932 · both · `MIT`  
  Radial ping markers ('enemy here / go here') for 2–8-player co-op communication without voice. Beta 1.12.2 for 1.21.1; needed on both sides.

### Juice (feel, sound, light, animation)

- **Loot Beams: Refork** — MR `neoforge-1.21.1-3.4.7` · CF 1150640/8358509 · client · `MIT`  
  Rarity-coloured light beams and labels on dropped loot: the signature RPG 'loot pop'. The only maintained NeoForge 1.21.1 loot-beam mod (Loot Beams Up and the original have no NeoForge 1.21.1 build). MIT. Costs Nirvana Lib → Common Network + Fzzy Config → Kotlin for Forge.
- **Nirvana Lib** *(library)* — MR `neoforge-1.21.1-2.2.0` · CF 1164411/7986004 · both · `MIT`  
  Library: required by Loot Beams: Refork.
- **Common Network** *(library)* — MR `1.0.21-1.21.1` · CF 806044/7087488 · both · `MIT`  
  Library: required by Nirvana Lib.
- **Fzzy Config** *(library)* — MR `0.7.7+fix1+1.21+neoforge` · CF 1005914/9326327 · both · `LicenseRef-TDL-M`  
  Library: required by Nirvana Lib. Uses a custom TDL-M licence (Timefall Development Licence Modified). I could not read its modpack terms; check them before release. Referencing it from CF or Modrinth does not redistribute the jar.
- **Kotlin for Forge** *(library)* — MR `5.12.0` · CF 351264/8335665 · both · `LGPL-2.1-only`  
  Library (Kotlin runtime): required by Fzzy Config. Many gameplay mods need it too.
- **AmbientSounds** — MR `6.3.11` · CF 254284/9254776 · client · `LGPL-3.0-only`  
  Biome, time and weather ambience, a large immersion win for a story pack. Client-only, needs CreativeCore.
- **CreativeCore** *(library)* — MR `2.13.51` · CF 257814/9108041 · both · `LGPL-3.0-only`  
  Library: required by AmbientSounds.
- **LambDynamicLights** — MR `4.8.11+1.21.1` · CF 393442/8780227 · client · `LicenseRef-Lambda-License`  
  Hand-held and dropped light sources light the world (torches in dungeons). The multi-loader jar supports NeoForge; 4.8.9+ updated for Sodium 0.8, and 4.8.11 is the declared end-of-life for 1.21. The 'fabric-api' dependency on Modrinth applies only to Fabric. Declares Sodium Dynamic Lights incompatible.
- **Entity Model Features (EMF)** — MR `3.3.12-neoforge-1.21` · CF 844662/9188526 · client · `LGPL-3.0-only`  
  OptiFine-format custom entity models. Required by Fresh Animations, and it lets the pack ship resource-pack mob variants.
- **Entity Texture Features (ETF)** — MR `7.2.6-neoforge-1.21` · CF 568563/9188408 · client · `LGPL-3.0-only`  
  Random, emissive and conditional entity textures. Required by EMF and Fresh Animations.
- **Fresh Animations (resource pack)** — MR `1.11.1` · CF 453763/9261871 · client · `LicenseRef-See-Terms-of-Use-in-Description`  
  Resource pack that animates vanilla mobs (needs EMF+ETF). Terms allow including it in a mod pack but forbid redistribution: reference it by Modrinth URL or CF project instead of rehosting, and enable it via Default Options. No paid-product use.

## Opt-in toggles

These are shipped disabled, or left out and documented. For client-only mods this is a client toggle. For server-logic mods it is a server-profile toggle.

### Performance (and core fixes)

- **Reese's Sodium Options** — MR `mc1.21.1-2.2.4+neoforge` · CF 511319/8891797 · client · `MIT`  
  Tabbed or searchable video-settings screen. Sodium 0.8 already reworked its own Video Settings UI, so this is cosmetic. Ship it as a client toggle at most.
- **Distant Horizons** — MR `3.3.3-1.21.1` · CF 508933/9004764 · both · `LGPL-3.0-only`  
  LOD terrain far past render distance. Heavy on CPU, RAM and disk, and it generates extra chunks in the background. Ship it as an opt-in client toggle, off by default. 3.3.3 supports 1.21.1 NeoForge and turns its own worldgen off while Chunky runs. Pair with an Iris shaderpack that supports DH. No source confirms DH 3.3 + Iris 1.8.14 + Sodium 0.8 together, so test before enabling.
- **Fast IP Ping** — MR `v1.0.12-mc1.21.1-neoforge` · CF 904356/8905303 · client · `LGPL-3.0-only`  
  Client-only. Speeds up multiplayer server-list pings. Harmless; add it if a server list is part of the experience.

### Recipe, info and UI

- **Just Enough Resources (JER)** — MR `1.6.0.57` · CF 240630/9311693 · client · `LicenseRef-Dont-Be-a-Jerk`  
  JEI plugin that shows mob drops, dungeon loot and ore distribution. Useful in an RPG, but it spoils boss and chest loot. Pack-designer decision.
- **Inventory Essentials** — MR `21.1.20+neoforge-1.21.1` · CF 368825/9035078 · both · `LicenseRef-All-Rights-Reserved`  
  Lightweight bulk-transfer shortcuts (Balm, both sides). Overlaps Mouse Tweaks; optional extra.
- **Configured** — MR — · CF 457570/7276577 · client · `MIT (per Modrinth project page; NeoForge build CF-only)`  
  In-game config editor (client side; a server install enables remote config editing). On CurseForge only for NeoForge 1.21.1 (the Modrinth project lists no NeoForge build). NeoForge 21.1 has its own config screens, so this is a convenience, not a requirement.
- **Catalogue** — MR — · CF 459701/6926815 · client · `unknown (CurseForge-only; not stated via CFWidget)`  
  Nicer mod list screen than NeoForge's built-in one. CurseForge only; cosmetic.
- **Toast Control** — MR `1.21.1-9.0.1` · CF 271740/6751464 · client · `MIT`  
  Suppresses recipe and advancement toast spam. Requires Placebo, a large library. Optional, because FTB Quests and KubeJS can already silence most toasts.
- **Placebo** *(library)* — MR `1.21.1-9.9.4` · CF 283644/9153039 · both · `MIT`  
  Library: required by Toast Control (and FastWorkbench). Ship it only if Toast Control is enabled.
- **Better Advancements** — MR `0.4.3.21` · CF 272515/5850587 · client · `LicenseRef-Dont-Be-a-Jerk`  
  Nicer advancement screen (0.4.3.21, beta). In a quest-driven story pack, FTB Quests is the progression UI, so this is optional.
- **Just Zoom** — MR `3.1.0-1.21.1-neoforge` · CF 561885/9325459 · client · `LicenseRef-DSMSLv3.1`  
  Zoom key (Keksuccino). Uses Konkrete, already present for FancyMenu, so it costs nothing extra. The vanilla spyglass exists, so optional.
- **Pick Up Notifier** — MR `v21.1.1-1.21.1-NeoForge` · CF 351441/6409785 · both · `MPL-2.0`  
  Item pickup feed (Fuzs). Nice loot feedback that uses Puzzles Lib, already present. Optional to keep the HUD clean next to RPG HUD elements.
- **Overflowing Bars** — MR `v21.1.1-1.21.1-NeoForge` · CF 852662/5770623 · client · `MPL-2.0`  
  Stacks health and armour rows when values exceed 20. Only needed if the gameplay or RPG-stats layer doesn't draw its own health HUD.
- **Item Highlighter** — MR `1.1.11` · CF 521590/5591015 · client · `CC-BY-NC-ND-4.0`  
  Marks newly picked-up items in the inventory (Iceberg). Small QoL.
- **Advancement Plaques** — MR `1.6.8` · CF 499826/5905995 · client · `CC-BY-NC-ND-4.0`  
  Replaces advancement toasts with plaques (Iceberg + Prism). Cosmetic, worth it only if advancements are used for story beats.
- **Chat Heads** — MR `0.15.7` · CF 407206/8642154 · client · `MPL-2.0`  
  Player heads in chat. Client-only multiplayer polish.
- **Crafting Tweaks** — MR `21.1.11+neoforge-1.21.1` · CF 233071/8697050 · both · `LicenseRef-All-Rights-Reserved`  
  Rotate, balance and clear buttons on crafting grids (Balm), integrated with Sophisticated. Little value in a low-crafting RPG.
- **TrashSlot** — MR `21.1.11+neoforge-1.21.1` · CF 235577/8163135 · both · `LicenseRef-All-Rights-Reserved`  
  Inventory trash slot (Balm). Optional QoL. Sophisticated Backpacks has an optional integration.

### Quests, story and scripting infrastructure

- **FTB Filter System** — MR — · CF 943925/7429011 · both · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Item filters for quest tasks (tag, NBT, OR/AND filters). Add it when the quest author needs smart item tasks. CurseForge only, ARR.
- **FTB Quests Optimizer** — MR `3.2.0-1.21.1` · CF 912469/7576461 · both · `MIT`  
  Server-side performance fix for large quest books with many inventory-check tasks. Add it if the story quest book grows large.
- **Easy Model Entities** — MR `2.6.0` · CF 1539533/9202419 · both · `MIT`  
  Optional Easy NPC module for custom NPC models. Add it if the story NPCs need non-humanoid or custom models.
- **MoreJS** — MR `1.21.1-0.16.0+neoforge` · CF 666198/7103440 · both · `LGPL-3.0-only`  
  KubeJS addon with villager and wandering-trader trades, enchanting events and structure hooks. Add it if the story economy uses villager trades.
- **Open Loader** — MR `21.1.5` · CF 354339/6546293 · both · `LGPL-2.1-only`  
  Use it to drop third-party datapack or resource-pack zips into a global folder. Adds no new libraries, since it reuses Bookshelf + Prickle. Optional because KubeJS + Default Options already cover pack-authored data, assets and default resource packs.

### Storage and travel

- **Sophisticated Storage** — MR `1.21.1-1.6.10.2206` · CF 619320/9341485 · both · `LicenseRef-All-Rights-Reserved`  
  Upgradeable chests and barrels. Nice, but a low-tech RPG can live with vanilla chests + Client Sort. Enable it if base-building is part of the loop.
- **Comforts** — MR `9.0.5+1.21.1` · CF 276951/7515858 · both · `LGPL-3.0-or-later`  
  Sleeping bags and hammocks. Sleeping bags skip the night without moving spawn, which conflicts with a Waystone/bonfire respawn design. Designer's call.

### Multiplayer

- **FTB Chunks** — MR — · CF 314906/8791113 · both · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Chosen claim mod (pick over Open Parties and Claims) because it reuses FTB Teams parties already needed by FTB Quests. Optional (server-profile toggle): 2–8 friends rarely need claims, and its built-in minimap must be disabled in client config so it doesn't duplicate Remnants Minimap. CurseForge only, ARR.
- **Simple Voice Chat** — MR `neoforge-1.21.1-2.6.22` · CF 416089/8601207 · both · `LicenseRef-All-Rights-Reserved`  
  Proximity voice chat (needs the server mod and a UDP port). Opt-in for groups who want it.
- **FTB Essentials** — MR — · CF 410811/8442866 · server · `All Rights Reserved (Feed The Beast Ltd; CurseForge-only)`  
  Server commands: /home, /spawn, /back, /tpa, /rtp, /nick and so on. Optional server toggle. If enabled, disable /back, /home and /rtp in the config, since they trivialise soulslike death stakes and Waystones handles travel. CurseForge only, ARR.
- **No Chat Reports** — MR `NeoForge-1.21.1-v2.9.1` · CF 634062/5885735 · both · `WTFPL`  
  Removes chat signing and report prompts and the 'unverified message' noise on private co-op servers. Last 1.21.1 build is 2024-11. Optional on both sides.
- **Simple Discord Rich Presence** — MR `88.0.1` · CF 334853/7505758 · client · `LicenseRef-All-Rights-Reserved`  
  Discord status 'Playing Remnants | The Modpack', which is free word-of-mouth marketing. Uses Architectury + Cloth Config, already present. Client toggle, recommended on.

### Juice (feel, sound, light, animation)

- **Sound Physics Remastered** — MR `neoforge-1.21.1-1.5.2` · CF 535489/9279974 · both · `GPL-3.0-only`  
  Reverb and occlusion. Beta for 1.21.1, noticeable CPU cost, and it can muffle boss audio cues. Client toggle.
- **Presence Footsteps (NeoForge port)** — MR `1.21.1-1.12.0-beta.1` · CF 1390302/7252696 · client · `MIT`  
  Unofficial NeoForge port (beta, MIT) of Presence Footsteps. Rich footstep sounds. Client toggle; test with AmbientSounds.
- **Falling Leaves (NeoForge/Forge)** — MR `1.21.1-2.6.0` · CF — · client · `LGPL-3.0-only`  
  Leaf particles from trees (Cheaterpaul's NeoForge port, 2026-10). Cheap client polish; coordinate with the visuals layer.
- **Particle Rain** — MR `v4.0.2+1.21.1-neoforge` · CF 421897/9113934 · client · `MIT`  
  Particle rain, snow and sandstorm weather plus fog. Client toggle. Coordinate with the visuals layer and shaderpack, since some shaders render their own rain.
- **Fancy World Animations** — MR `1.2.31` · CF 1452982/8221257 · client · `MIT`  
  Smooth door, trapdoor, lever and chest animations. Client toggle. Overlaps any 'animated blocks' choice the visuals layer makes.
- **Fusion (Connected Textures)** — MR `1.3.16-neoforge-mc1.21.1` · CF 854949/9070353 · client · `LicenseRef-All-Rights-Reserved`  
  Native NeoForge connected-textures engine (Sodium and Iris compatible). Only needed if the pack ships a CTM-style resource pack.

### Fixes owned by another layer

- **AttributeFix** — MR `21.1.3` · CF 280510/7115922 · both · `LGPL-2.1-only`  
  Raises vanilla attribute caps (armour 30, etc.) that RPG stat and gear mods exceed. Zero extra libraries (Bookshelf + Prickle). Belongs to the combat/RPG layer, which should confirm it.

## Rejected alternatives

### Performance (and core fixes)

- **Sodium Options API** (MR `neoforge-1.21.1-1.0.10` · CF 1103431/6100815): Sodium 0.8.12+ release notes say it is 'not compatible with any version of Sodium Options API … and any mods that depend on it'. Last 1.21.1 build is 2025-01.
- **Embeddium** (MR `1.0.15+mc1.21.1` · CF 908741/6118392): Sodium fork. Last 1.21.1 build is 2025-01, and it cannot coexist with Sodium. Official Sodium on NeoForge supersedes it.
- **Oculus** (no NeoForge 1.21.1 build found): Embeddium shader port with no NeoForge 1.21.1 build. Iris has an official NeoForge build.
- **Radium Reforged** (MR `0.13.1` · CF —): Unofficial Lithium port. Beta, last built 2024-09, and redundant now that Lithium ships for NeoForge. Do not run both.
- **Noisium** (MR `2.3.0+mc1.21-1.21.1` · CF —): Last 1.21.1 build is 2024-08 and the project is effectively archived. Worldgen-noise mixins risk clashing with the gameplay layer's worldgen mods for little gain.
- **C2ME (NeoForge)** (MR `0.4.0-alpha.0.124+1.21.1` · CF —): Only alpha builds (0.4.0-alpha). Concurrent chunk generation is the most common source of worldgen-mod incompatibilities. Revisit later for dedicated servers only.
- **Krypton** (no NeoForge 1.21.1 build found): Fabric only, with no NeoForge port. Network-stack savings do not matter for 2–8 players.
- **Fast Leaf Decay** (no NeoForge 1.21.1 build found): No NeoForge build for 1.21.1 (the Modrinth project is Fabric). Leaves Be Gone covers it.
- **BadOptimizations** (MR `2.4.1` · CF 949555/7338300): Small client micro-optimisations that overlap ModernFix and ImmediatelyFast. Its own wiki marks some options incompatible with 'camera lock-on' style mods, a risk for soulslike lock-on combat.
- **ScalableLux** (MR `0.1.0.1+neoforge.1cb1e91` · CF 1055925/6952385): Light-engine replacement (NeoForge 0.1.0.1, 2025-09). Stability comes first. Revisit only if spark shows lighting as a bottleneck.
- **Moonrise** (MR `0.1.0-beta.15+2eae1b1` · CF 1096335/7089177): Beta, and it declares itself incompatible with several mods. Server-side chunk-system rewrite that is too risky for a content-heavy pack.

### Recipe, info and UI

- **EMI** (MR `1.1.24+1.21.1+neoforge` · CF 580555/8081408): Strong alternative with recipe tree and favourites. It loads JEI plugins only when JEI is also installed ("install JEI alongside EMI … JEI will be hidden"), so EMI would mean two recipe mods. Choose EMI+JEI instead of JEI only if the team wants EMI's UX.
- **EMI Loot** (MR `0.7.9+1.21+neoforge` · CF 681783/7417271): Depends on EMI (not chosen). It also pulls Fzzy Config and Symbols 'n' Stuff, and it shows boss loot tables, which spoils discovery.
- **Jade Addons (Neo/Forge)** (MR `6.1.2+neoforge` · CF 583345/9056575): Only adds tooltips for specific tech and storage mods that this pack does not run. Add it later if the gameplay layer needs it.
- **Inventory Profiles Next** (MR `neoforge-1.21.1-2.2.5` · CF 495267/7810574): Feature-rich but heavy (Kotlin for Forge + libIPN, AGPL). A NeoForge 1.21.1 pack (Gregnautics Continued) reported an IndexOutOfBounds client crash on middle-click pick-block in multiplayer that is still present in the latest 1.21.1 build (2.2.5), and swapped it for Client Sort. Co-op stability wins.
- **libIPN** (MR `neoforge-1.21.1-6.6.3` · CF 679177/7810552): Library for Inventory Profiles Next only (not chosen).
- **Obscure Tooltips** (MR `4.2.5` · CF 715660/8922038): Flashy alternative to Legendary Tooltips. Pick one tooltip renderer. It needs Fragmentum and its Obscuria licence is custom, while Legendary Tooltips is more configurable for custom rarity tiers.
- **Fragmentum** (MR `5.4.0` · CF 1123977/9202578): Library for Obscure Tooltips and Loot Journal (neither chosen).
- **Better Third Person** (MR `1.9.0` · CF 435044/5833474): Declared incompatible by Shoulder Surfing Reloaded. Last 1.21.1 build is 2024-10.
- **Zoomify** (no NeoForge 1.21.1 build found): No NeoForge 1.21.1 build (Fabric only on CF and Modrinth).
- **Xaero's Minimap** (MR `neoforge-1.21.1-26.6.0` · CF 263420/9067173): NightBeam ships its own 'Remnants | Advanced Minimap & Waypoints' (NeoForge 1.21.1, needed on both sides). A second minimap would duplicate the HUD. Fallback if Remnants Minimap is dropped: Xaero's Minimap + World Map (ARR; reference it, do not rehost).
- **Xaero's World Map** (MR `neoforge-1.21.1-1.47.0` · CF 317780/9067277): Use only if Remnants Minimap has no fullscreen map. Integrates with Open Parties and Claims, not FTB Chunks.
- **JourneyMap** (MR `1.21.1-6.0.9+neoforge` · CF 32274/8923668): Alternative to Remnants Minimap / Xaero. Heavier, with its own waypoint system. Not needed.
- **Neat** (MR `1.21.1-47-neoforge` · CF 238372/7774002): Mob health bars. Deferred to the gameplay layer: Remnants RPG Mobs and Jade may already show health. Avoid two health-bar systems.
- **Highly Customizable Damage Numbers** (MR `v1.1.31+mc1.21.1` · CF —): Damage-number option (NeoForge 1.21.1, 2026-04). Deferred to the combat and RPG-mobs layer to avoid duplicate damage feedback. Listed only as an option.
- **Damage Numbers** (MR `1.4.1-neoforge` · CF —): Alternative damage-number mod. Last build 2024-06 (1.21), CF has no 1.21.1 NeoForge file. Deferred to the gameplay layer.

### Quests, story and scripting infrastructure

- **Odyssey Quests (formerly Heracles)** (MR `2.0.3` · CF 845831/9250436): Terrarium's continuation of Heracles: tree-style quests, MIT, on both Modrinth and CurseForge (2.0.3, beta) with Resourceful Lib. The only credible FTB Quests alternative if a Modrinth-first .mrpack becomes the priority. Smaller ecosystem: no KubeJS bridge comparable to FTB XMod Compat and no FTB Teams integration.
- **"Heracles" on CurseForge (project-1505798, unrelated)** (MR — · CF 1505798/7887164): WARNING: the CurseForge URL slug 'heracles' now resolves (via CFWidget) to project 1505798, an unrelated 2026 'optimization' mod by MaxCreateMC with ~945 downloads (virtual-thread AI/network rewrite, 'incompatibilities possible'). It is not the quest mod. Never add it by slug.
- **Modonomicon** (MR `1.21.1-1.121.0` · CF 538392/9351619): Alternative book mod with unlockable entries (MIT). FTB Quests already handles progression gating, so Patchouli is enough. It will come in anyway if a gameplay mod (e.g. Occultism) depends on it.
- **Custom NPCs** (no NeoForge 1.21.1 build found): No NeoForge 1.21.1 build on either CurseForge or Modrinth. Easy NPC is the 1.21.1 answer.
- **YOSBR** (no NeoForge 1.21.1 build found): No NeoForge 1.21.1 build (Fabric/Quilt only). Default Options covers it.
- **ProbeJS** (MR `8.0.3` · CF 585406/8304356): Dev-only: generates TypeScript typings for KubeJS script authoring. Use it in the dev instance, never ship it.
- **Paxi** (MR `1.21.1-NeoForge-5.1.3` · CF 1015157/6485740): Global datapack/resourcepack loader. Requires YUNG's API (the CF NeoForge build is a separate '[1.20.4–1.21.1 only]' project). KubeJS already loads pack data and assets.
- **YUNG's API** (MR `1.21.1-NeoForge-5.1.9` · CF 1015100/8894736): Library for Paxi (not chosen). Note: the gameplay layer will likely add it anyway via YUNG's structure mods.
- **Global Packs** (MR `21.0.6` · CF 317134/6634585): Same job as Paxi and Open Loader. ARR, last built 2025-06. Not needed.

### Storage and travel

- **Traveler's Backpack** (MR `1.21.1-10.1.40` · CF 321117/9297032): Pick one backpack mod. Sophisticated has more upgrades and better sorting and JEI integration. Traveler's needed a separate 'Legendary Tooltips x Traveler's Backpack Fix'.
- **GraveStone Mod** (MR `neoforge-1.21.1-1.0.40` · CF 238551/8671622): Same job as Corpse (pick one). It places a block, which can fail in dungeons and Lootr spaces.
- **Carry On** (MR `2.2.6` · CF 274259/8512888): Lets players pick up chests and mobs, which can cheese bosses and NPCs and relocate Lootr containers. Needs extensive blacklisting in a story pack.
- **Storage Drawers** (MR `1.21.1-13.11.4` · CF 223852/6995432): Tech-leaning bulk storage; not the low-tech RPG vibe.
- **Tom's Simple Storage** (MR `1.21-2.4.2` · CF 378609/8769956): Storage terminal network, too tech for a low-tech RPG. Sophisticated Storage is the optional storage path.

### Multiplayer

- **Open Parties and Claims** (MR `neoforge-1.21.1-0.33.0` · CF 636608/9221991): Good claims mod (pairs with Xaero maps), but it would add a second party system next to FTB Teams. Only beta builds.
- **FallingTree** (MR `1.21.1-1.21.1.11` · CF 349559/6835168): Tree felling, redundant with FTB Ultimine.
- **VeinMiner (Miraculixx)** (MR `2.11.2` · CF —): Redundant with FTB Ultimine, and needs a different Kotlin runtime (kotlin-lang-forge).
- **CraftPresence** (MR `2.7.1+1.21.1-neoforge` · CF 297038/7704907): More configurable Discord RPC but needs UniLib. SRDP is simpler and already covered by existing libraries.
- **Better Ping Display** (MR `1.21.1-1.1` · CF —): Numeric ping in the tab list. Nice-to-have; not needed for friends' co-op.

### Juice (feel, sound, light, animation)

- **Loot Journal: Pickup Notifier** (MR `6.2.2` · CF 1120395/8922056): Pickup feed alternative to Pick Up Notifier. Needs Fragmentum, and on CurseForge the NeoForge build is a separate project (1120395).
- **Presence Footsteps** (no NeoForge 1.21.1 build found): Official mod is Fabric-only on 1.21.1. See the NeoForge port above.
- **Falling Leaves** (no NeoForge 1.21.1 build found): Original is Fabric-only. See the NeoForge port above.
- **Cool Rain Reforged** (MR `1.0.2` · CF 1346978/8819888): Overlaps Particle Rain.
- **Visuality** (no NeoForge 1.21.1 build found): No NeoForge 1.21.1 build (Fabric/Quilt only).
- **Punchy!** (no NeoForge 1.21.1 build found): No 1.21.1 NeoForge build.
- **Inventory Particles** (MR `3.2.0+1.21.1+neoforge` · CF 1339689/8939238): Cosmetic GUI particles. Needs MossyLib; CC-BY-ND. Not worth another library.
- **Sodium Dynamic Lights** (MR `neoforge-1.21.1-1.0.10` · CF —): Depends on Sodium Options API, which Sodium 0.8 does not support. Declared incompatible by LambDynamicLights.
- **Continuity** (MR `3.0.0+1.21.neoforge` · CF —): Its NeoForge build needs Sinytra Connector + Forgified Fabric API (Fabric-on-NeoForge layer). Not acceptable for a clean pack.

## Conflicts and compatibility findings

### Rendering stack (most important)

- **Sodium 0.8 on 1.21.1 replaces 0.6.** Sodium's 1.21.1 line went from 0.6.13 straight to 0.8.12 and then 0.8.13, a backport of modern Sodium 0.8.
- **What 0.8 breaks.** Its release notes say it is "not compatible with any version of 'Sodium Options API' … and any mods that depend on it", so **Sodium Dynamic Lights is out**. They also say "Iris works as of 1.8.13".
- **The Iris pairing is exact.** On Modrinth, Iris `1.8.14-beta.1+1.21.1-neoforge` (marked release) requires Sodium version `uMOpc5uV` (0.8.13). The older Iris 1.8.12 requires Sodium 0.6.13.
- **CurseForge trap.** CurseForge tags Iris 1.8.14-beta.1 as *beta* (file 8242804), so CF's newest "release" Iris (1.8.12, file 6661598) does **not** work with CF's newest Sodium (0.8.13, file 8756580). Pin file 8242804 in the CF manifest.
- **Known crash with Supplementaries.** A Sodium issue (#3722) reports a world-load crash with Sodium 0.8.12-alpha.1 + Supplementaries on NeoForge 1.21.1 that 0.6.13 did not have. If the gameplay layer adds Supplementaries, or other mods with Sodium mixins such as Flywheel/Create, smoke-test them. The fallback is the pair **Sodium 0.6.13 + Iris 1.8.12**, which must be switched together. Sodium Extra 0.9.x is built for Sodium 0.8.
- **Mods updated for Sodium 0.8:**
  - **More Culling:** 1.0.8 "fix crash with sodium 0.8", 1.0.7 "fix incompat with epic fight". Ship 1.0.10.
  - **LambDynamicLights:** 4.8.9 "Updated Sodium configuration screen compatibility with Sodium 0.8.x". 4.8.11 is the declared end-of-life build for 1.21.
- **Distant Horizons 3.3.3** supports 1.21.1 NeoForge. I found no report confirming DH 3.3 + Iris 1.8.14 + Sodium 0.8 together, which is one reason it ships opt-in and off.

### Declared incompatibilities (from Modrinth version metadata)

| Mod | Declares incompatible with |
|---|---|
| Shoulder Surfing Reloaded | Better Third Person, YDM's Custom Camera View, Nimble |
| LambDynamicLights | Sodium Dynamic Lights, RyoamicLights |
| Embeddium | Rubidium, TexTrue's Embeddium Options. It is also a Sodium replacement, so never run it with Sodium. |
| Radium | Canary. Radium is an unofficial Lithium port; never run both. |
| Moonrise | Canary, Not Enough Crashes, Starlight (NeoForge) |

### Integration conflicts found in research

- **Inventory Profiles Next.** The changelog of a 1.21.1 pack (Gregnautics Continued) reports an IndexOutOfBoundsException client crash on middle-click pick-block in multiplayer, still present in IPN 2.2.5. The pack replaced IPN with Client Sort, and this pack does the same. No source reported an IPN + Sophisticated Backpacks conflict.
- **Shoulder Surfing Reloaded and combat mods.**
  - SSR 1.21.1 disables outdated Epic Fight mixins.
  - The bridge add-on "SSR: Camera Fixes & Additions" (Epic Fight, Better Combat, Better Lockon, Iron's Spells) supports SSR 4.x only, not 5.x.
  - The combat layer decides the SSR version.
  - BadOptimizations marks some of its options incompatible with "camera lock-on" mods, which is another reason it is excluded.
- **Continuity on NeoForge** needs Sinytra Connector + Forgified Fabric API, so it is out. Fusion is the native NeoForge connected-textures option.
- **EMI** shows JEI-only plugins only when JEI is installed too ("install JEI alongside EMI … JEI will be hidden"). That means EMI+JEI or JEI alone, never EMI alone, in a pack full of JEI-plugin content mods.
- **FTB Chunks** has its own minimap and fullscreen map. If it is enabled, turn its minimap off in the client config so it doesn't stack with Remnants Minimap. Xaero's maps integrate with Open Parties and Claims, not FTB Chunks.
- **Traveler's Backpack** needed a separate "Legendary Tooltips x Traveler's Backpack Fix" mod, another reason Sophisticated Backpacks was picked.
- **Design conflicts with a soulslike:**
  - Carry On can pick up mobs, bosses and Lootr chests.
  - FTB Essentials `/back` and `/home` remove death stakes.
  - Comforts sleeping bags skip night without moving spawn.
  - These are opt-in or rejected, with config notes.
- **The "heracles" CurseForge slug is squatted.** CFWidget resolves `minecraft/mc-mods/heracles` to project **1505798**, an unrelated April-2026 "optimization" mod (about 945 downloads, rewrites AI and networking on virtual threads, "incompatibilities possible"). The real Heracles is now **Odyssey Quests** (CF 845831, Modrinth `odyssey-quests`). Never add mods by guessed slug.
- **The Modrinth slug `odyssey` is not the quest mod.** It is an unrelated adventure-content mod.
- **New hidden required libraries in 2026 builds:**
  - **JEI 19.55+** requires **MezzConfig** (beta 0.6.9).
  - **KubeJS 2101.7.2 build 374+** requires **Better Advanced Tooltips**.
  - The **Easy NPC "Bundle"** jar does *not* contain the modules. It requires Easy NPC Core + Easy NPC Config UI.
  - **Fzzy Config** (in the Loot Beams chain) now requires Kotlin for Forge.
- **Split CurseForge projects.** Paxi, YUNG's API, Loot Journal and Fragmentum keep their NeoForge 1.21.1 jars in separate "(NeoForge)" CurseForge projects. Their main projects only have Forge-tagged 1.21.1 files.
- **Fresh Animations 1.11.1** no longer declares EMF/ETF as Modrinth dependencies, but it still needs them. Ship EMF + ETF explicitly (both are included).

## Distribution and licensing

- **CurseForge is the primary release.** Every default-on jar has a CurseForge project and file, and the CF manifest only needs project and file IDs.
- **Modrinth (.mrpack) is incomplete by necessity.** 71 of the 77 default-on jars have Modrinth URLs and hashes in the JSON. The 6 without are FTB Quests, FTB Library, FTB Teams, FTB XMod Compat, FTB Ultimine and AllTheLeaks, which are CurseForge-only. The FTB mods are All Rights Reserved (`LICENSE.md` in FTBTeam's repos), so they cannot go in .mrpack overrides. A Modrinth edition would either have to send players to CurseForge, as packs like "Vanilla II" do, or swap FTB Quests for Odyssey Quests and re-author the questline. I don't recommend that for Season 1.
- **Never rehost these:**
  - Sodium (PolyForm Shield)
  - LambDynamicLights: the Lambda License requires written approval to distribute binaries, and it is client-only, so keep it out of server packs.
  - Fresh Animations: its terms say "may include … in your mod pack" but "may not redistribute", and forbid paid products.
  - Any ARR or CC-BY-NC-ND jar
  - Keksuccino's DSMSL mods (FancyMenu, Drippy, Just Zoom): the licence allows modpacks only as a reference downloaded from the official source, so keep them out of server-pack zips. FancyMenu is server-optional.
  Reference them through CurseForge or Modrinth.
- **If the pack is ever sold or paywalled** (Patreon-exclusive builds, for example), these become blockers and need permission:
  - The non-commercial licences: Jade (CC-BY-NC-SA-4.0), Patchouli (CC-BY-NC-SA-3.0), Legendary Tooltips, Item Borders, Equipment Compare, Iceberg and Prism (all CC-BY-NC-ND-4.0).
  - Fresh Animations' "no paid product" clause.
- **Licences I could not verify:**
  - AllTheLeaks: CF-only, and no licence is shown through CFWidget.
  - Catalogue: CF-only.
  - Fzzy Config: custom TDL-M. Its licence repository could not be read.
  Check these before release.

## Integration to-dos (configuration the pack must ship)

- **Default Options:**
  - Default keybinds, laid out so these don't collide: SSR camera toggle, Ping Wheel, FTB Ultimine hold-key, Client Sort, LambDynamicLights.
  - Enable Fresh Animations by default.
  - Iris shaders off, Distant Horizons absent or off.
- **FancyMenu + Drippy:** the branded "Remnants | The Modpack" main menu and loading screen.
- **Better Compatibility Checker:** pack name and version.
- **Crash Assistant:** official modlist baseline, so it can show users what they added or removed.
- **Jade:** hide entity health if Remnants RPG Mobs draws its own bars.
- **Legendary Tooltips + Item Borders:** map NightBeam rarity tiers or tags to frame and border colours.
- **FTB Ultimine:** conservative limits, a hunger cost, and tool/tag restrictions.
- **FTB Chunks (if enabled):** minimap off.
- **FTB Essentials (if enabled):** `/back`, `/home` and `/rtp` off.
- **Chunky:** a documented pre-generation radius for servers. Optionally pre-generate the spawn region before the first story beat.
- **Lootr:** confirm the gameplay layer's dungeon and boss chests use loot tables, so Lootr converts them.

## Lean option (≤70 jars by default)

Two changes bring the default set to exactly 70:

1. Move **Loot Beams: Refork** and its chain to opt-in: 5 jars (Loot Beams, Nirvana Lib, Common Network, Fzzy Config, Kotlin for Forge). Note that Kotlin for Forge will probably come back with the gameplay layer.
2. Move **AmbientSounds + CreativeCore** to opt-in: 2 jars.

I'd rather keep both, because loot beams and ambience are what players notice first in an RPG pack.

## Handoffs to the gameplay researcher

- **Attribute caps:** AttributeFix is listed as opt-in in this layer. The RPG stats and gear layer should confirm it, since the 1.21.1 vanilla caps (armour 30, and so on) are often exceeded.
- **Health bars and damage numbers:** Neat, Highly Customizable Damage Numbers and Overflowing Bars are deliberately not on by default, to avoid duplicating Remnants RPG Mobs or RPG Stats HUDs.
- **Camera:** SSR version pinning depends on the combat mod (Epic Fight vs Better Combat).
- **Libraries the gameplay layer will probably add anyway:** Curios or Accessories, GeckoLib, YUNG's API, Kotlin for Forge, Modonomicon. Deduplicate against `foundation_mods.json`.
- **Visual overlap:** any particle, shader or animated-block choices from the visuals layer should be checked against Particle Rain, Falling Leaves, Fancy World Animations and Fresh Animations, all of which are juice-tier and mostly opt-in here.

## Sources

- Modrinth API, project and version endpoints for every slug in the JSON (`https://api.modrinth.com/v2/project/{slug}/version?loaders=["neoforge"]&game_versions=["1.21.1"]`), queried 2026-10-29.
- CFWidget (`https://api.cfwidget.com/{projectId}` and `/minecraft/mc-mods/{slug}`), queried 2026-10-29. Slug lookups were unreliable (404s, an "UNUSED" Cloth Config project, the squatted "heracles"), so CF IDs were confirmed by project ID and title.
- Sodium mc1.21.1-0.8.12 release notes (compatibility list): https://modrinth.com/mod/sodium/version/S3DUMfBo
- Sodium issue #3722 (0.8.12-alpha + Supplementaries crash): https://github.com/CaffeineMC/sodium/issues/3722
- Gregnautics Continued changelog (IPN pick-block crash, replaced by Client Sort): https://www.curseforge.com/minecraft/modpacks/gregnautics-continued/files/8449862
- SSR: Camera Fixes & Additions (Epic Fight / Better Combat bridge, SSR 4.x): https://www.curseforge.com/minecraft/mc-mods/shoulder-surfing-reloaded-camera-fixes-additions
- Vanilla II (Modrinth pack pointing users to CurseForge for FTB mods): https://modrinth.com/modpack/vanilla-ii
- FTB dependency declarations and licence: https://raw.githubusercontent.com/FTBTeam/FTB-Quests/1.21.1/main/neoforge/src/main/resources/META-INF/neoforge.mods.toml and https://raw.githubusercontent.com/FTBTeam/FTB-Library/1.21.1/main/LICENSE.md
- Fresh Animations terms: https://modrinth.com/resourcepack/fresh-animations
- Lambda License: https://github.com/LambdAurora/LambDynamicLights/blob/1.21.5/LICENSE
- Crash Assistant licence (modpack clause): https://github.com/KostromDan/Crash-Assistant/blob/1.19-1.20.1/LICENSE.md
- NeoForge versions: https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml
- NightBeam distribution context: `reports/NightBeam mod market gaps.md` in this repo (CurseForge supplies about 85% of downloads).
