# Atmosphere and music mods for Remnants | The Modpack (MC 1.21.1, NeoForge 21.1.x)

Research date: 2026-10-29. I checked every candidate below against Modrinth API v2 (search with `versions:1.21.1` + `categories:neoforge`, then the project's own NeoForge 1.21.1 version list) and cfwidget (`api.cfwidget.com/{id}`, filtered to files tagged both `1.21.1` and `NeoForge`). For the shortlisted mods and their close alternatives, I also downloaded the jar and read its `neoforge.mods.toml` and mixin targets. I checked any Sodium and Iris class references against the pack's own Sodium 0.8.13 and Iris 1.8.14 jars.

**Existing mods excluded from suggestions:** AmbientSounds, Particle Rain, Fresh Animations/EMF/ETF, LambDynamicLights, Cataclysm, Mowzie's, Iris/Sodium/Sodium Extra, FancyMenu, Drippy, Runeborn, the Remnants family (incl. minimap) and the rest of `src/mods.json`.

---

## Ranked shortlist

| # | Mod | CurseForge project / 1.21.1 NeoForge file | Side | Verdict |
|---|---|---|---|---|
| 1 | **Traveler's Titles (NeoForge)** | **1015155** / 6294123 `TravelersTitles-1.21.1-NeoForge-5.1.3.jar` | client | **Recommend.** Souls-style biome and dimension title cards. Needs only YUNG's API, which is already in the pack. |
| 2 | **Reactive Music** | 960382 / 8530938 `reactivemusic-neoforge-1.3.5+1.21.1.jar` | client | **Recommend.** Replaces the vanilla soundtrack with situational fantasy/Celtic music (night, underground, nearby mobs, dying, boss…). Its YAML songpacks let you make a grimmer soundtrack of your own. Jar is 295 MB. |
| 3 | **Subtle Effects** | 1023913 / 9150589 `SubtleEffects-neoforge-1.21.1-1.15.1.jar` | client (+opt. server) | **Recommend.** Sparks, smoke, burning-entity effects and a low-health heartbeat. Has its own particle culling. Fzzy Config is already in the pack. |
| 4 | **Sound Physics Remastered** | 535489 / 9279974 `sound-physics-remastered-neoforge-1.21.1-1.5.2.jar` (beta) | client | **Recommend as an optional client toggle.** Adds reverb and occlusion, so crypts and catacombs sound like crypts. Beta, has a CPU cost, and can muffle boss audio cues. |
| 5 | **Fog** (IMB11) | 815438 / 7079142 `Fog-neoforge-1.11.0-1.21.1.jar` | client | **Recommend.** Fog thickens with depth in caves, follows the weather and moon phase, and changes colour by biome. Needs **MRU** (new library) and YACL ≥3.6.2. |
| 6 | **Polytone** | 958094 / 9356160 `polytone-1.21-5.3.4-neoforge.jar` | client | **Recommend (as a tool).** Lets a resource pack set custom lightmaps (darker nights), sky and fog colours per biome or dimension, and colormaps. It does nothing until you ship a pack: this is how the overworld gets "the Long Eclipse" look. |
| 7 | **More Darkness** | 1511006 / 8574545 `more_darkness-neoforge-1.21.1-2.0.1+1.21.1.jar` | client | **Maybe (optional toggle, default off).** Night light follows the moon, caves go pitch black, and eyes adapt over time, so torches and LambDynamicLights matter. It changes gameplay, has a small user base, and overlaps Polytone lightmaps. |
| 8 | **Presence Footsteps (NeoForge port)** | 1390302 / 7252696 `PresenceFootsteps-1.21.1-1.12.0-beta.1-1.21NeoForge.jar` (beta) | client | **Maybe (optional toggle).** Detailed footsteps and armour sounds. Unofficial beta port, last updated 2025-11. |

Cheap extras if you want more ambient life, all client-only and dependency-free:
- **Cave Dust Rethinking** (CF 1617531 / 8975999): basalt-style ash drifting in caves, which fits "you wake in the ash".
- **Falling Leaves (NeoForge/Forge)** (CF **463155** / 9225531; the earlier foundation research found no CF id).
- **Visuality: Reforged** (CF 704256 / 8559477): hit, bone and slime particles. The earlier research wrongly said Visuality had no NeoForge build; this Reforged port does.

---

## Findings to act on

1. **Runeborn's Sovereigns cannot be given music by any third-party mod.** Runeborn ships no music. In `core/boss/Bosses.class` the Sovereigns are built on vanilla entity types: wither_skeleton, stray, evoker, vindicator, ravager, piglin_brute and skeleton_horse, among others. Their boss bar is Runeborn's own packet (`Packets$BossBar` → `client/BossBars`), not a vanilla `ServerBossEvent`. That has two consequences:
   - Battle Music's per-entity mapping would also fire on every ordinary wither skeleton or stray.
   - Reactive Music's `BOSS` event keys off vanilla boss bars and won't see them.

   The clean fix is in Runeborn itself. The Eclipsed Realm already has the pattern to copy: `client/ClientBossMusicHandler`, `network/ClientboundBossMusicPacket` and the `skeletonfight_theme` sound.
2. **Boss bars are already contested, so don't add a boss-bar overhaul.** Three pack mods already touch `BossHealthOverlay`:
   - The Eclipsed Realm mixes into it (`BossHealthOverlayMixin`, custom pixel bars).
   - Bosses of Mass Destruction mixes into it too.
   - Runeborn reads it through `BossOverlayAccessor`.
3. **Death screen: avoid.** Runeborn hooks `DeathScreen` (`RunebornNeoForgeClient`) and draws its own "YOU DIED" banner.
4. **The Eclipsed Realm has its own visuals.** It draws its own sky (`LevelRendererSkyMixin` → `eclipseSky` in `renderSky`), its own area banners (`RealmOverlay`) and camera shake.
   - In Traveler's Titles, blacklist the dimension `remnant_bosses:eclipsed_realm`.
   - Keep any sky mod (Polytone sky, Nuit, Subtle Skybox) scoped to the overworld, and test it in the Realm.
5. **YACL.** Fog, More Darkness, Better Clouds and Sounds all need `yet_another_config_lib_v3`. The pack only has YACL 3.6.6 nested inside Fragmentum. That satisfies their ranges (`[3.6.2,)`, `[3.5.0,4.0.0)`), but if you adopt any of them, add standalone **YACL** (CF 667299 / 7437845 `yet_another_config_lib_v3-3.8.2+1.21.1-neoforge.jar`, Modrinth `yacl`) so you don't depend on Fragmentum's jar-in-jar.
6. **MRU** (IMB11 library, needed by Fog and Sounds): CF 669659 / 9004036 `mru-1.0.41+1.21.1-neoforge.jar`, Modrinth `mru` / `SNVQ2c0g`. Licence ARR (IMB11 EULA), both sides optional, 22.2M Modrinth / 34.1M CF downloads.
7. **Keybind collisions with the shipped `defaultoptions/options.txt`.**
   - Simple Music Control's default "next track" key is **M**, which is the minimap world map.
   - ATMOSPHERICS' editor hotkey is **B**, which is the minimap marker.
   - Unbind or move both if you use them.
8. **Music mods are mutually exclusive, and some are heavy.** Pick one music engine or soundtrack:
   - Reactive Music, Maestro, True Adaptive Music, Ambience Mini, DCME, Immersive Music or Medieval Music.
   - Jar sizes: Medieval Music 347 MB, Reactive Music 295 MB, Immersive Music 155 MB, Battle Music 114 MB. Every client downloads these.
9. **Reactive Music settings to change before shipping.**
   - Remove or retune its `BOSS` entries, which play whenever a vanilla boss bar is visible. Otherwise they stack on Cataclysm, Mowzie's, Aquamirae and Realm boss themes.
   - Decide on menu music. FancyMenu has `play_vanilla_menu_music = true`, and Reactive Music's `MAIN_MENU` entry will take that over.
10. **A grim sky with no new mod.** Retexture `minecraft:textures/environment/sun.png` (and `moon_phases.png`) in the pack's own resource pack, for example as a black sun with a corona. Polytone then handles sky and fog colour.
11. **Overlap groups: pick one from each.**

    | Group | Candidates |
    |---|---|
    | Lightmap | Polytone lightmaps, More Darkness, Selas |
    | Fog | Fog, Fog Overrides, Simple Fog Control, Polytone fog colours, ATMOSPHERICS, Dynamic Surroundings |
    | Sky | Nuit, Subtle Skybox, Polytone sky, ATMOSPHERICS, plus the Realm's own sky |
    | Leaves | Falling Leaves, Particular, Falling Leaves Plus |
    | Footsteps | Presence Footsteps, Dynamic Surroundings, Tread Lightly |
    | Sound physics | Sound Physics Remastered, Sound Physics Perfected |

12. **Licences and distribution.** The CurseForge zip references files by project and file id, and the `.mrpack` by Modrinth URL, so nothing is redistributed. ARR mods are therefore fine unless the author forbids pack use, and none below do. **CurseForge-only:** Medieval Music has no 1.21.1 build on Modrinth, so it can't go in the `.mrpack`. **Modrinth-only** (unusable for the CF zip): First Steps, Enhanced Biomes Music, YouDiedReforged.

---

## 1. Music

### Reactive Music: **recommend**
- **Ids:** Modrinth `reactive-music` / `Bqnfeesx`. CF **960382**, file **8530938** `reactivemusic-neoforge-1.3.5+1.21.1.jar` (release, 2026-07-29, 294.8 MB).
- **Licence:** GPL-3.0-only (code). The bundled "Adventure Redefined" tracks are by Vindsvept, Adrian von Ziegler and Mufaya, described as "copyright free (non-commercially)". A free pack is fine.
- **Side and dependencies:** client. On NeoForge the jar declares only NeoForge. The page says YACL is required, but the 1.21.1 jar has no YACL calls (checked).
- **Downloads:** 7.66M Modrinth / 2.27M CF. 4 NeoForge 1.21.1 builds.
- **What it does:** event-driven music. Events include MAIN_MENU, DAY/NIGHT/SUNRISE/SUNSET, RAIN/SNOW/STORM, UNDERGROUND/DEEP_UNDERGROUND, UNDERWATER, NETHER, VILLAGE, NEARBY_MOBS, BOSS and DYING. The songpack is a YAML file (`musicpack/ReactiveMusic.yaml`); a resource-pack songpack can replace it with a darker set.
- **Notes:** the stock tracks lean toward "wonder" more than "grim". The author says there's no plan to support 26.x, which is irrelevant here. No Sodium or Iris interaction.
- **Verdict:** the best ready-made soundtrack for a medieval or fantasy pack. Make it unique by adding your own songpack.

### Maestro (Obscuria): **maybe** (the best authoring engine if you'd rather script music per structure in JSON)
- **Ids:** Modrinth `maestro-music` / `jcZX6rvP`. CF **1454351**, file **8922083** `maestro-neoforge-1.21.1-4.0.1.jar` (release, 2026-09-19, 0.1 MB).
- **Licence:** Obscuria Modding/Ecosystem License, the same author and licence as Aquamirae and Fragmentum, which are already shipped.
- **Side and dependencies:** Modrinth lists client and server as required, but the jar marks its dependencies `CLIENT`; treat it as a client mod and verify. Requires Fragmentum (in pack).
- **Downloads:** 13k Modrinth / 191k CF.
- **What it does:** a data-driven layer that *extends* vanilla music using biomes, structures, entities, bosses, weather and screens. With it you could script music for Much More Dungeons labyrinths, Ember Shrines or the Hunter's Moon. The optional **Maestro: Overture** resource pack (CF 1456190 / 7613312 `Maestro-Overture.zip`, 33.6 MB, tagged 1.21.1 and 1.21.11 on CF; Modrinth lists 2.0.0 only for 1.21.8–1.21.11) only covers 8 vanilla structures.
- **Verdict:** use it *instead of* Reactive Music if you want a fully authored soundtrack.

### True Adaptive Music: **maybe** (engine alternative)
- **Ids:** Modrinth `true-adaptive-music` / `UeDAoEyD`. CF **1208639**, file **9034644** `TrueAdaptiveMusic-neoforge-cf-2.9.3+1.21.1.jar` (2026-10-02).
- **Licence:** GPL-3.0-or-later.
- **Side and dependencies:** client. Requires Kotlin for Forge (in pack).
- **Downloads:** 100k Modrinth / 17.5k CF.
- **What it does:** "Music Packs" with combat, boss, biome and structure logic, plus an in-game pack browser.
- **Verdict:** actively updated, but a smaller community than Reactive Music.

### Ambience Mini: **maybe** (engine alternative)
- **Ids:** Modrinth `ambience-mini` / `TsW1jKuo`. CF **1311926**, file **9322895** `AmbienceMini-1.21.1-2.7.12.jar` (2026-10-25).
- **Licence:** LGPL-3.0 on Modrinth; the jar says "All Rights Reserved".
- **Side:** client, with an optional server part for structure detection.
- **Downloads:** 5k Modrinth / 19k CF.
- **What it does:** a configurable engine for combat, bosses, structures, health and so on. It ships no music.
- **Verdict:** capable, but very small user base.

### Medieval Music (someaddon): **maybe** (CurseForge-only, tone)
- **Ids:** CF **521932**, file **5543469** `zmedievalmusic-1.21-2.1.jar` (2024-07-18, **347 MB**). Not on Modrinth for 1.21.1: Modrinth's `medieval-music` is an unrelated 26.x resource pack.
- **Licence:** music is 40 Alexander Nakarada tracks under CC-BY 4.0, with attribution listed on the page.
- **Side and dependencies:** client, none.
- **Downloads:** 31.4M CF.
- **What it does:** replaces the vanilla music pool. It has no situational logic, and the tracks are tavern and adventure in tone ("Now We Feast", "Celebration"), not grim.
- **Verdict:** only if you want a straight swap. It's the heaviest jar, can't go in the `.mrpack`, and fights Reactive Music.

### The Immersive Music Mod (TIMM): **maybe → avoid for this pack**
- **Ids:** Modrinth `immersivemusicmod` / `EgBj3Bnf`. CF **1066903**, file **7266606** `timm-1.1-neoforge-1.21.jar` (2025-11-27, 155 MB).
- **Licence:** GPL-3.0 code. The music (Gold Eagle) is free to share except behind a paywall.
- **Side and dependencies:** client. Modrinth lists Cloth Config (in pack).
- **Downloads:** 686k Modrinth / 917k CF.
- **What it does:** 147 original biome tracks, with Terralith supported.
- **Verdict:** high quality, but the C418-style calm tone works against "grim". It replaces music, so it conflicts with Reactive Music.

### Battle Music: **avoid** (maybe only as a generic combat-music layer)
- **Ids:** Modrinth `battlemusic` / `8HFCp5k3`. CF **1027182**, file **8668465** `battlemusic-1.2.2.jar` (2026-08-17, 114 MB).
- **Licence:** CC-BY-4.0 on Modrinth; the jar says "All Rights Reserved". It bundles 22 tracks from Minecraft Dungeons, Legends and Story Mode, which are Mojang/Telltale-owned.
- **Side and dependencies:** client, none.
- **Downloads:** 1.37M Modrinth / 1.11M CF.
- **Why avoid:**
  - Its defaults *replace* Cataclysm's own boss OST.
  - Its per-entity mapping can't single out Sovereigns (see Findings 1).
  - The stock tone is heroic.

### Simple Music Control: **maybe** (only with vanilla or Maestro music; redundant with Reactive Music)
- **Ids:** Modrinth `simple-music-control` / `8AX2hHnX`. CF **1185599**, file **9332437** `simple_music_control-neoforge-1.5.6+1.21.1.jar` (2026-10-26).
- **Licence:** MIT.
- **Side and dependencies:** client. Requires Fzzy Config (in pack). Optional Sodium `[0.8.12,)`, built for the pack's Sodium 0.8 config API.
- **Downloads:** 496k Modrinth / 106k CF.
- **What it does:** shorter gaps between tracks, a now-playing widget and a next-track key.
- **Note:** the next-track key defaults to **M**, which collides with the minimap world map.

### Constant Music: **maybe** (same role as Simple Music Control)
- **Ids:** Modrinth `constant-music` / `tvuSEM6E`. CF **949032**, file **6954009** `constantmusic-neoforge-1.0.6+mc1.21.1.jar` (2025-09-01).
- **Licence:** LGPL-3.0; "Feel free to use this mod in any modpack".
- **Side and dependencies:** client, none.
- **Downloads:** 1.57M Modrinth / 3.86M CF.

### Biome Beats: **maybe** (engine for your own tracks)
- **Ids:** Modrinth `biomebeats` / `QQ6fyLzC`. CF **921811**, file **8888983** `biomebeats-neoforge-1.21-2.1.1.jar` (2026-09-15).
- **Licence:** MIT; "Feel free to use this mod in any modpack".
- **Side and dependencies:** client, none.
- **Downloads:** 31k Modrinth / 453k CF.

### Music engines to avoid

| Mod | Ids | Why avoid |
|---|---|---|
| DCME | Modrinth `uDwJAaHz`; CF 1460839 / 9325635 | ARR. Ships no music. **Blocks other mods' music by namespace** (it would mute Cataclysm, Aquamirae and Realm themes unless configured). 6–7k downloads. |
| Music Triggers | CF 518410 / 6497407 | Only an **alpha** for 1.21.1 (7.0.4, 2025-05-05). Needs The Impossible Library. |
| Music and Melody | CF 1544814 / 8804568 | Custom "Legacy License". A music player plus online features rather than a mood mod. |
| Boss Music Mod (exiled) | CF 501159 / 5865195 | Wither and Ender Dragon only. Last updated 2024-11. |
| Enhanced Biomes Music | — | Modrinth-only. |

---

## 2. Area, biome and structure title cards

### Traveler's Titles (NeoForge): **recommend**
- **Ids:** Modrinth `travelers-titles` / `JtifUr64` (version `1.21.1-NeoForge-5.1.3`). CF **1015155**, a separate "(NeoForge)" project like the other YUNG ports in `curation.yaml`. The main project 504908 only has *Forge* 1.21.1 files. File **6294123** `TravelersTitles-1.21.1-NeoForge-5.1.3.jar` (release, 2025-03-11).
- **Licence:** LGPL-3.0.
- **Side and dependencies:** client. Requires YUNG's API ≥ 1.21.1-NeoForge-5.1.2; the pack has 5.1.9.
- **Downloads:** 9.6M Modrinth / 6.2M CF (NeoForge project) + 56.2M CF (main project).
- **Config:**
  - Blacklists for biomes and dimensions: add `remnant_bosses:eclipsed_realm`, because the Realm draws its own banners.
  - Text X/Y offsets (keep it clear of Runeborn's cinematic banners and the Hunter's Moon title), colour, fade timings, and a skylight-only option.
  - A custom title sound through a resource pack, and grim biome names through lang overrides.
  - 5.1.3 added names for Terralith and Nullscape biomes.
- **Compatibility:** no Sodium or Iris interaction.

### Wandering Traveler: **maybe** (prettier, immature)
- **Ids:** Modrinth `wandering-traveler` / `kZlMne3t`. CF **1673904**, file **9242602** `wanderingtraveler-neoforge-1.6.0.jar` (2026-10-18, 6.6 MB).
- **Licence:** ARR, but "Can I use it in a modpack? Yes, and there is no need to ask."
- **Side and dependencies:** client. Requires Cloth Config (in pack). No mixins.
- **Downloads:** 4k Modrinth / 2.2k CF.
- **What it does:** hand-drawn art title cards. You can add a PNG per biome id, for example for the Realm biomes or Terralith.
- **Verdict:** modded-biome art is still being added. Use it *instead of* Traveler's Titles, never both.

### Areas (Serilum): **maybe** (for hand-built hubs such as Last Light; not automatic)
- **Ids:** Modrinth `areas` / `NWvsqJ2Z`. CF **391701**, file **9276950** `areas-1.21.1-7.0.jar` (2026-10-21).
- **Licence:** ARR; free to use in any modpack hosted on CurseForge or Modrinth.
- **Dependencies:** Collective (in pack).
- **Downloads:** 975k Modrinth / 10.7M CF.
- **What it does:** named regions defined by signs, with join and leave messages.

### Area-title mods to avoid

| Mod | Ids | Why avoid |
|---|---|---|
| First Steps (structure titles) | Modrinth `98tY8ITu` | CF project 1592852 has **no 1.21.1 NeoForge file**, so it's Modrinth-only. |
| RPGTitles | — | 2024 build, no CF 1.21.1 file. |

---

## 3. Visual atmosphere (no shaders)

### Fog (IMB11): **recommend**
- **Ids:** Modrinth `fog` / `WuGVWUF2`. CF **815438**, file **7079142** `Fog-neoforge-1.11.0-1.21.1.jar` (2025-10-07).
- **Licence:** ARR. The page states only ARR; IMB11's mod EULA, linked from their Sounds page, allows CurseForge and Modrinth modpacks.
- **Side:** client.
- **Dependencies:**
  - Architectury ≥13.0.8 (in pack).
  - YACL ≥3.6.2 (see Findings 5).
  - **MRU** ≥1.0.19 (CF 669659 / 9004036).
- **Downloads:** 1.91M Modrinth / 2.88M CF.
- **What it does:** cave fog thickens with depth, fog follows the weather and moon phase, and fog is coloured by biome.
- **Compatibility:** the page says it's Sodium-compatible and shader-compatible with default-fog shaders. No Sodium class references. It mixes into FogRenderer, LevelRenderer and DimensionSpecialEffects, as does Polytone, so test the two together and disable Polytone's fog colours if they fight.

### Polytone: **recommend** (tool)
- **Ids:** Modrinth `polytone` / `3qAYkBMB`. CF **958094**, file **9356160** `polytone-1.21-5.3.4-neoforge.jar` (2026-10-28).
- **Licence:** GPL-3.0-or-later on Modrinth; the jar says "Supplementaries Team License v1.5". Same author as Supplementaries, Amendments and Moonlight, which are already shipped.
- **Side and dependencies:** client. No required dependencies (it jar-in-jars CodecUI, exp4j and nexp).
- **Downloads:** 20.0M Modrinth / 10.8M CF.
- **What it does:** a resource pack can define custom lightmaps (darker nights, darker caves per dimension), sky and fog colours per biome, colormaps, and particle and block-sound tweaks.
- **Compatibility:**
  - It has Sodium compat mixins. All 16 Sodium classes it references exist in the pack's Sodium 0.8.13 (I checked class presence only, not method signatures, so boot-test it).
  - It mixes into LightTexture, so don't stack it with More Darkness or Selas.

### More Darkness: **maybe** (optional toggle)
- **Ids:** Modrinth `more-darkness` / `ghnOnAJe`. CF **1511006**, file **8574545** `more_darkness-neoforge-1.21.1-2.0.1+1.21.1.jar` (2026-08-04).
- **Licence:** ARR on Modrinth, MIT in the jar. No modpack clause.
- **Side and dependencies:** client. YACL ≥3.6.2.
- **Downloads:** 22k Modrinth / 14k CF.
- **What it does:** nights follow the moon phase, caves go pitch black, water gets murky, and eyes adapt (gradual dark sight, colourless low light, glare on leaving the dark). Each system can be toggled.
- **Compatibility:** mixes into LightTexture, FogRenderer and LevelRenderer. Iris shader packs usually override the lightmap.

### Nuit: **maybe** (custom skybox engine, beta)
- **Ids:** Modrinth `nuit` / `YBz7DOs8`. CF **408209**, file **8891287** `nuit-neoforge-1.0.0-beta.6+mc1.21.1.jar` (beta, 2026-09-15).
- **Licence:** MIT, "fully modpack-compatible".
- **Side and dependencies:** client, none.
- **Downloads:** 14.9M Modrinth / 9.7M CF.
- **Verdict:** the right tool if you want a full "eclipsed sky" skybox, but it's beta on NeoForge and needs a custom sky pack. Keep it to the overworld: the Realm has its own sky mixin.

### Fog Overrides: **maybe** (alternative to Fog, with no new library)
- **Ids:** Modrinth `fogoverrides` / `B1vBJNM4`. CF **398134**, file **6512893** `fogoverrides-1.21.1-2.3.0.jar` (2025-05-09).
- **Licence:** LGPL-3.0; OK in modpacks hosted on CurseForge or Modrinth.
- **Side and dependencies:** client. Cloth Config and Architectury (both in pack).
- **Downloads:** 8.9M Modrinth / 0.9M CF.
- **What it does:** config-driven fog distances per dimension, biome and underwater. The author tries to keep Sodium compatibility but makes no promise for shaders.

### ATMOSPHERICS: **maybe** (powerful, but overlaps)
- **Ids:** Modrinth `atmospherics` / `ft2cYBpB`. CF **1493725**, file **8412083** `atmospherics-2.6.5-mc-1.21.1.jar`, which is **beta** on CF (2026-07-11). Modrinth has 2.6.5.2 as a release (2026-09-16); CF lags.
- **Licence:** ARR, no modpack statement.
- **Side:** client.
- **Downloads:** 1.23M Modrinth / 231k CF.
- **What it does:** a real-time per-biome editor for fog, sky, clouds, haze and stars. Presets can ship as a resource pack.
- **Notes:** the editor hotkey is **B**, which collides with the minimap marker. Pick it *or* Polytone and Fog.

### Subtle Skybox: **maybe** (low value for "grim")
- **Ids:** Modrinth `subtle-skybox` / `18yT8qGk`. CF **1344151**, file **6980618** `subtleskybox-forge-0.2.0.jar`; despite the "-forge" name, this is the NeoForge build (2025-09-09).
- **Licence:** LGPL-3.0.
- **Side:** client.
- **Downloads:** 36k Modrinth / 929k CF.
- **What it does:** a nicer night sky.

### Better Clouds: **maybe** (cosmetic)
- **Ids:** Modrinth `better-clouds` / `5srFLIaK`. CF **1285973**, file **9005637** `better-clouds-1.13.11+1.21.1-neoforge.jar` (2026-09-29).
- **Licence:** MPL-2.0; assets CC BY-SA.
- **Side and dependencies:** client. YACL `[3.5,4.0)`.
- **Downloads:** 5.77M Modrinth / 4.29M CF.
- **Compatibility:** it removed its Sodium options-page mixin in 1.13.5, so the dead Sodium 0.6 GUI references in the jar aren't loaded. Iris-compatible.

### Visual mods to avoid

| Mod | Ids | Why avoid |
|---|---|---|
| Simple Fog Control | CF 622640 / 6353377 | MIT and fine, but Sodium Extra already exposes fog toggles. |
| Selas | CF 1604188 / 8772150 | Darker-night lightmap, but beta 0.1.3 with only 836 Modrinth downloads. |
| Glowtone | CF 1338155 / 8441260 | Beta. FrozenBlock licence. Mixes into Sodium's fluid renderer. |
| Colorful Lighting | — | Page says "not compatible with Sodium". |
| True Darkness | — | No build newer than 2022; nothing for 1.21.1. |
| Ambient Environment | CF 320163 / 5799489 | Bedrock-style colour noise. Not mood. Last build 2024-10. |

### Death screen and boss bar
- **Enhanced Boss Bars:** avoid. Modrinth `J5bVsBt9`; CF **1063296** / 9292243 `enhanced_boss_bars-1.1.3-1.21.1-neoforge.jar`; ARR; 2.17M Modrinth / 10.7M CF. A fourth `BossHealthOverlay` mixin next to the Realm, BOMD and Runeborn.
- **Death screens:** avoid. Covers Epic Death Screen (CF 1484326 / 8851230, a beta-named jar), YouDiedReforged (Modrinth-only), Better Death and similar. Runeborn owns the death screen.

---

## 4. Sound and other mood mods (safe on a large pack)

### Sound Physics Remastered: **recommend** (optional client toggle)
- **Ids:** Modrinth `sound-physics-remastered` / `qyVF9oeo`. CF **535489**, file **9279974** `sound-physics-remastered-neoforge-1.21.1-1.5.2.jar` (**beta**, 2026-10-21; earlier 1.21.1 builds were alpha).
- **Licence:** GPL-3.0.
- **Side and dependencies:** client. Optional Cloth Config (in pack) and Simple Voice Chat.
- **Downloads:** 57.7M Modrinth / 154M CF.
- **Notes:** 1.5.2 fixed OpenAL reference distance and restored linear attenuation. It has a CPU cost and can muffle boss cues (from the earlier foundation research).

### Presence Footsteps (NeoForge, unofficial port): **maybe**
- **Ids:** Modrinth `pf-neoforge` / `JIEwmDVI`. CF **1390302**, file **7252696** `PresenceFootsteps-1.21.1-1.12.0-beta.1-1.21NeoForge.jar` (beta, 2025-11-23).
- **Licence:** MIT.
- **Side and dependencies:** client, none.
- **Downloads:** 1.34M Modrinth / 759k CF.

### Subtle Effects: **recommend**
- **Ids:** Modrinth `subtle-effects` / `4q8UOK1d`. CF **1023913**, file **9150589** `SubtleEffects-neoforge-1.21.1-1.15.1.jar` (2026-10-12).
- **Licence:** ARR. Terms: "✅ Use this mod in modpacks with credit and one or more links to any of the project pages".
- **Side and dependencies:** client; a few features need it on the server. Fzzy Config ≥0.7.7 (pack has 0.7.7+fix1). No Sodium references.
- **Downloads:** 13.3M Modrinth / 24.2M CF.
- **Note:** the heartbeat threshold is configurable as absolute health. Tune it for RPG-scaled max HP.

### Dynamic Surroundings (OreCruncher, official): **maybe, only as a *replacement* for AmbientSounds + Particle Rain**
- **Ids:** Modrinth `dynamicsurroundingsfabric` / `H7fshfpD`. CF **238891**, file **9353209** `dynamicsurroundings-neoforge-1.21.1-0.4.8.jar` (2026-10-28, 15.7 MB).
- **Licence:** MIT.
- **Side and dependencies:** client. Architectury ≥13.0.8 (in pack).
- **Downloads:** 7.27M Modrinth / 75.8M CF.
- **What it does:**
  - Biome sounds, a storm and wind simulation, and branching lightning.
  - Ground fog in swamps and eerie biomes, and sky fog driven by biome, time and weather.
  - Waterfall effects, auroras, and footstep remapping.
- **Verdict:** great for mood, but it duplicates what the pack already ships, and the 0.4.x line on 1.21.1 changes weekly. The unofficial "Dynamic Surroundings Rebirth by uawiegrfv" (CF 1666351) is an AI-reworked fork per the original author, with about 5k downloads: avoid it.

### Sounds (IMB11): **maybe**
- **Ids:** Modrinth `sound` / `ZouiUX7t`. CF **925889**, file **7325254** `sounds-2.4.22+lts+1.21.1-neoforge.jar` (2025-12-12).
- **Licence:** ARR, plus an EULA: "free to use this mod within your Modrinth & CurseForge modpacks".
- **Side and dependencies:** client. YACL and MRU.
- **Downloads:** 20.4M Modrinth / 18.0M CF.
- **What it does:** 170+ new interaction and UI sound effects. It shares the MRU dependency with Fog.

### Distant Thunders: **maybe** (tiny)
- **Ids:** Modrinth `distant-thunders` / `cY4e8fDt`. CF **1534382**, file **8506385** `distantthunders-mc1.21.1-neoforge-1.1.0.jar` (2026-07-25).
- **Licence:** MIT.
- **Side and dependencies:** client. Architectury (in pack).
- **Downloads:** 37k Modrinth / 24k CF.
- **What it does:** thunder arrives later the farther the strike is.

### Cinematic Cataclysm: **maybe, test first**
- **Ids:** Modrinth `cinematic-cataclysm` / `1WAsDg6d`. CF **1399324**, file **7550281** `cinematiccataclysm-1.0.1-1.21.1.jar` (2026-01-30).
- **Licence:** ARR. Its notes address modpack makers.
- **Side:** **both** (server required).
- **Downloads:** 65k Modrinth / 5.59M CF.
- **What it does:** intro cutscenes for Scylla, Maledictus, Leviathan, Ancient Remnant and Ignis.
- **Risks:**
  - It "heavily relies on internal code of Cataclysm" and predates Cataclysm 3.30–3.33; the pack ships **3.33**.
  - It needs the cutscene entities added to **EntityCulling's** tick-culling whitelist (EntityCulling is in the pack).

### Camera Overhaul: **maybe** (feel, not atmosphere)
- **Ids:** Modrinth `cameraoverhaul` / `m0oRwcZx`. CF **423602**, file **8979489** `CameraOverhaul-v2.1.2-neoforge+mc[1.21-1.21.1].jar` (2026-09-26).
- **Licence:** GPL-3.0+.
- **Side and dependencies:** client. Cloth Config. Its `mods.toml` range `>=16.0.0` isn't a Maven range; NeoForge reads it as a soft recommendation, so 15.0.140 should load. Confirm in the boot test.
- **Downloads:** 6.89M Modrinth / 10.5M CF.
- **Compatibility:** it mixes into Camera and GameRenderer, as do Shoulder Surfing Reloaded and the Realm's CameraShakeMixin. Test with the over-the-shoulder camera.

### Particle and leaf alternatives
- **Particular Reforged:** maybe. Modrinth `pYFUU6cq`, CF 1219053 / 8662697. LGPL-3.0. 5.7M Modrinth / 34.3M CF. Fireflies, cascades, leaves and cave dust; overlaps Falling Leaves and Cave Dust Rethinking.
- **Falling Leaves Plus:** maybe. Modrinth `PZyzzLjz`, CF 1577351 / 8809179. MPL-2.0. Needs Puzzles Lib (in pack).
- **Cave Dust Rethinking:** cheap extra. Modrinth `7pdlDpFR`, CF 1617531 / 8975999 `cave_dust_rethinking-3.4.0+1.21.1-neoforge.jar`. MPL-2.0. 38k Modrinth / 40k CF.
- **Falling Leaves (NeoForge/Forge):** cheap extra. Modrinth `2JAUNCL4`, CF **463155** / 9225531 `fallingleaves-1.21.1-2.6.0.jar`. LGPL-3.0. 6.16M Modrinth / 70.5M CF.
- **Visuality: Reforged:** cheap extra. Modrinth `z13R7Et1`, CF 704256 / 8559477 `visuality-forge-3.0.0.jar`. MIT. 5.92M Modrinth / 36.5M CF.

### Sound mods to avoid

| Mod | Ids | Why avoid |
|---|---|---|
| Drip Sounds | CF 448311 / 9142530 | The current NeoForge jar (0.6.3 beta) has **unexpanded `${mc_min}` placeholders** in `mods.toml`, which is a load-time risk. AmbientSounds already covers cave ambience. |
| Sound Physics Perfected | CF 1328492 / 8239462 | CF lags Modrinth. Never run it alongside Remastered. |
| Tread Lightly | — | 1.9k downloads. |
| Hear the Wind | — | Wind during fast movement; little value here. |

---

## Method and sources
- **Modrinth API v2:** `/search` (facets `versions:1.21.1` and `categories:neoforge`), `/project/{id}`, and `/project/{id}/version?loaders=["neoforge"]&game_versions=["1.21.1"]`. Queried 2026-10-29.
- **cfwidget:** `api.cfwidget.com/{id}` and `/minecraft/mc-mods/{slug}`. A User-Agent was set.
  - For Camera Overhaul (423602), Sounds (925889) and Falling Leaves (463155), cfwidget slug lookups 404'd. I got the project ids from public packwiz manifests on GitHub and confirmed them by id on cfwidget.
  - CurseForge's own site and API returned 403 through the proxy, so they weren't used.
- **Jar inspection (read only):** I read `neoforge.mods.toml` and mixin configs from the Modrinth jars of the candidates. For the pack's own mods I used the jars in `/home/user/modpack/.cache/jars` (Runeborn, Eclipsed Realm, RPG Mobs, BOMD, Shoulder Surfing, Sodium, Iris), to find the boss-bar, death-screen, sky, camera and music hooks cited above.
- Nothing under `/home/user/modpack` was modified, and Minecraft was not launched.
