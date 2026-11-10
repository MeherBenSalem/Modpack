# Launching Season 1

## Platforms: CurseForge and Modrinth

- **Both platforms get the same pack.** Since 1.0.0-beta.11 every mod is on both: the FTB suite (Quests, Library,
  Teams, Filter System, XMod Compat, Ultimine) was replaced by NightBeam's own Core RPG - Quests Engine, and
  AllTheLeaks (CurseForge-only; ModernFix and FerriteCore already cover it) was dropped. `tools/build_pack.py --export`
  warns if a mod is ever missing from one of the exports.
- **CurseForge** (project 1772691): upload `dist/*-curseforge.zip` as the pack file and `dist/*-server.zip` as its
  server pack (Actions -> Publish to CurseForge).
- **Modrinth**: upload `dist/*.mrpack` (Actions -> Publish to Modrinth, once the project exists and its id is set as
  the `REMNANTS_MODRINTH_ID` repository variable). Modrinth packs reference every mod on Modrinth's CDN and carry no
  jars; server owners use the CurseForge server pack or install the `.mrpack` with a Modrinth-aware launcher.
- **AI policy.** Modrinth (enforced since 2026-09-27) bans projects "entirely or primarily comprised of"
  generative-AI output and requires disclosure when the description or substantial content relies on it. This
  pack's quests, story text and scripts were drafted with AI assistance, and the Keeper's narration may be
  synthesised. Before the Modrinth upload, the owner should rewrite and own the text, and the page must carry the
  disclosure. AI-generated icons and gallery images are banned outright there: use real in-game screenshots and
  human-made art.
- CurseForge: check its current content and AI-disclosure rules at upload time and disclose the same way.

## Licences

- Several mods forbid re-hosting or only allow links: FancyMenu, Drippy Loading Screen, LambDynamicLights, Fresh
  Animations, Remnants: Roguelite Dungeons (All Rights Reserved), L_Ender's Cataclysm and Friends&Foes (CC BY-NC-ND).
  The CurseForge zip references every mod by project and file id. The server zip bundles the CurseForge file of
  every server-side mod (as CurseForge server packs do; it is uploaded to CurseForge as this pack's server file and
  never hosted anywhere else), plus the NeoForge installer and start scripts. FancyMenu, Drippy and LambDynamicLights
  are client-only, so they are not in it. Before the first upload, confirm on CurseForge that the server-file rules
  still allow bundling the All Rights Reserved and ND-licensed jars above. Never add jars to `pack/`.
- Non-commercial licences (Jade, Patchouli, the Legendary Tooltips family, Fresh Animations) mean the pack must stay
  free. Paid server ranks that sell gameplay would need those authors' permission.
- Catalogue and Fzzy Config licences were not verified by the research; check them before release.

## Play-test checklist (things a server boot can't prove)

The server boot test (`tools/test_server.py`) proves every server mod loads together, the quests load, the scripts
run and the Last Light NPCs, the Echo and the Eclipse bar work. A client play-test still has to confirm:

1. ~~The client starts with every mod and reaches a world.~~ Verified 2026-10-29 (headless client: title screen,
   world load, no crash). Still worth a look on a real GPU with shaders on.
2. Runeborn stamina and Better Combat combos feel right together (the movesets in `src/data/runeborn_movesets.yaml`).
3. The default keybinds in `config/defaultoptions/options.txt` apply on a fresh install and show no conflicts.
4. Fresh Animations is enabled by default and Entity Model Features renders it.
5. A real death raises an Echo wearing your gear at the corpse, and killing it shows "Echo laid to rest".
6. Each Sovereign kill rekindles one ember on the Long Eclipse bar and adds a heart to every online player.
7. The Ashen Codex opens from the first quest's reward.
8. Runeborn champions still drop Sovereign Fragments with Runeborn's mob levels off.
9. Fellowship sellswords and the Eclipsed Realm's fog gates (allies may not follow you into arenas).
10. Mob LootBags contents feel fair through Act I–II, the RAS item locks (diamond 12, netherite 30) aren't too tight.

## Narration (the Keeper's voice)

- 81 lines are scripted in `src/voice/lines.yaml`, generated from the quests: every Keeper line in the main story
  (spoken when its quest completes), eight unlock lines (the Keeper warns you when each Sovereign's fight becomes
  available; `unlock:` in a quest) and the Threshold's cinematics. KubeJS queues a player's lines so two quests
  finishing together play one after the other.
- The shipped audio is a **placeholder made with Kokoro**, an open-source TTS model (Apache-2.0), mastered by
  `tools/build_voice.py`. The ElevenLabs account connected during development had no credits left, so nothing was
  generated there.
- To upgrade: record or generate each line as `src/voice/raw/<line>.mp3` (or wav/ogg) and run
  `python3 tools/build_voice.py`. Real recordings automatically replace the placeholders.
  The voice picked for the Keeper was "Arkadius - Old Storyteller", eleven_v4, about 7,000 characters for the whole script.
- Players can turn the Keeper down with the *Voice/Speech* volume slider.

## Pack-side fixes for mod bugs (remove when the mod is fixed)

- **Amendments' sliding hotbar selection** draws the selection box over the held item, and Ashen 16x's box is
  opaque, so the selected item vanished. `config/amendments-client.toml` sets `hotbar_slot_animation_speed = 0`.

## The Threshold (first-join starting area)

- New players wake in the Threshold after picking an origin, fight Ser Odric and leave through the Waygate.
- Players who already have 5+ minutes on a world skip it.
- Ops can manage it with `/threshold`:
  - `off` / `on`: switch it off or on for new players.
  - `skip <player>`: send a player past it.
  - `send <player>`: send a player back in.
  - `rebuild`: rebuild the ruin.
- Odric's tuning is at the top of `kubejs/server_scripts/remnants/threshold.js`. The pack scales incoming damage about
  16x to match players' larger health, so he hits for about 60 and four hits kill a fresh character.

## Licences of the new defaults

- **Ashen 16x** (resource pack, on by default) is All Rights Reserved. The CurseForge zip references it by project and
  file id, so CurseForge serves it; never bundle the zip itself.
- **Reactive Music** bundles "copyright free (non-commercially)" tracks, another reason the pack must stay free.
- **Subtle Effects** asks for credit and a link to its project page on the pack page.
- **Fog** is covered by IMB11's mod EULA, which allows CurseForge and Modrinth modpacks.

## What only the owner can make

- **Pack art is drafted** in `art/` (icon, logo, menu background, title card) and the custom main menu is built
  from it (`tools/build_menu.py`). It is code-drawn over a real screenshot; read `art/README.md` on disclosure
  before uploading it anywhere. Upload `art/out/icon.png` as the CurseForge project avatar: a modpack zip can't carry
  an icon. The Drippy loading screen is still the default.
- **Gallery:** 8–12 real in-game screenshots and the trailer reel from the NightBeam video pipeline.
- **Store page:** pitch from `design/STORY.md`, the feature list from `design/PROGRESSION.md`.
- **Season 2:** the story hook is in the Epilogue ("Who broke the sun?"); Twilight Forest is the suggested new
  dimension (the research left it out of Season 1 on purpose).
