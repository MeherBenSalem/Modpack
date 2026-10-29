# Launching Season 1

## Platform: CurseForge first

- **CurseForge is the primary platform.** FTB Quests, FTB Library, FTB Teams, FTB Filter System, FTB XMod Compat,
  FTB Ultimine and AllTheLeaks exist only on CurseForge, and ~85% of NightBeam's downloads already come from there.
  Upload `dist/*-curseforge.zip` as the pack file and `dist/*-server.zip` as its server pack.
- **Modrinth needs two decisions before it's possible:**
  1. The quest book would have to move to a Modrinth-hosted quest mod (Odyssey Quests, formerly Heracles), or the FTB
     mods be bundled with permission. `tools/build_pack.py --export` lists every mod a Modrinth export is missing.
  2. Modrinth's AI policy (enforced since 2026-09-27) bans projects "entirely or primarily comprised of"
     generative-AI output and requires disclosure when the description or substantial content relies on it. This
     pack's quests, story text and scripts were drafted with AI assistance. Before any Modrinth upload, the owner
     should rewrite and own the text, and the page must carry the disclosure. AI-generated icons and gallery images
     are banned outright there: use real in-game screenshots and human-made art.
- CurseForge: check its current content and AI-disclosure rules at upload time and disclose the same way.

## Licences (why the server pack downloads its jars)

- Several mods forbid re-hosting or only allow links: FancyMenu, Drippy Loading Screen, LambDynamicLights, Fresh
  Animations, Remnants: Roguelite Dungeons (All Rights Reserved), L_Ender's Cataclysm and Friends&Foes (CC BY-NC-ND).
  The CurseForge zip references every mod by project and file id, and the server zip ships an `install.sh` that
  downloads each jar from its official host and checks its sha1. Never add jars to `pack/`.
- Non-commercial licences (Jade, Patchouli, the Legendary Tooltips family, Fresh Animations) mean the pack must stay
  free. Paid server ranks that sell gameplay would need those authors' permission.
- AllTheLeaks, Catalogue and Fzzy Config licences were not verified by the research; check them before release.

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

## What only the owner can make

- **Pack art is drafted** in `art/` (icon, logo, menu background, title card) and the custom main menu is built
  from it (`tools/build_menu.py`). It is code-drawn over a real screenshot; read `art/README.md` on disclosure
  before uploading it anywhere. Upload `art/out/icon.png` as the CurseForge project avatar: a modpack zip can't carry
  an icon. The Drippy loading screen is still the default.
- **Gallery:** 8–12 real in-game screenshots and the trailer reel from the NightBeam video pipeline.
- **Store page:** pitch from `design/STORY.md`, the feature list from `design/PROGRESSION.md`.
- **Season 2:** the story hook is in the Epilogue ("Who broke the sun?"); Twilight Forest is the suggested new
  dimension (the research left it out of Season 1 on purpose).
