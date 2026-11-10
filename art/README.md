# Pack art

The icon, logo, main-menu background and title card for Season 1. Everything is drawn as SVG/HTML in
`src/art.html` (the icon in `src/icon.html`) and rendered with the pre-installed Chromium; the only picture in it is a real in-game screenshot.

| File | Size | Where it goes |
|---|---|---|
| `out/icon.png`, `out/icon_1024.png` | 512×512, 1024×1024 | CurseForge project avatar (upload on the project page; a modpack zip can't carry it). Drawn in `src/icon.html`: an Ashborn's greatsword planted in ash blocks before the black sun, the broken Sun-Crown at its foot, ruined spires in the haze, embers rising |
| `out/logo.png` | 1600×700, transparent | Main menu (copied into `pack/config/fancymenu/assets/`), page headers |
| `out/menu_background.png` | 1920×1080 | Main-menu background: the shot with a dark band on the left for the buttons |
| `out/title_card.png` | 1920×1080 | First gallery image, page banner, video thumbnail base |
| `shots/ember_shrine_sunset.png` | 1920×1080 | The in-game shot: an Ashborn-armoured stand at an Ember Shrine at sunset |
| `out/menu_background_dark.png` | 1920×1080 | The title screen and loading screen plate: the shot darkened, the logo centred |
| `out/menu/btn_<entry>_<normal\|hover>.png` | 640×64 | Text-only menu entries; hover adds the gold glow and rules |
| `out/menu/btn_server_<normal\|hover>.png` | 736×120 | The "Need a server?" entry of the title screen (184×30 GUI units at 4×): the menu's own lettering, "Sponsored by Apex Hosting" under it and the Apex mark |
| `out/sponsor/apex_icon.png` | 64×64 | The Apex mark alone, for the button on the Multiplayer screen |
| `sponsors/apex-hosting-banner-849x141.png` | 849×141 | The banner Apex Hosting supplied. The store pages link it as it is, and the Apex mark above is a crop of it (`.apex-mark` in `src/art.html`), never a redrawn logo |
| `out/sounds/ui_hover.ogg`, `ui_click.ogg` | | Synthesised here (`numpy`): a soft chime and a struck bell |
| `out/loading_bar_frame.png`, `loading_bar_fill.png` | 1200×40 | The loading screen's thin gold bar |

## Regenerate

```bash
node art/render.cjs art/shots/ember_shrine_sunset.png   # art/out/*.png
node art/render.cjs --sponsor                            # only the sponsor button and the Apex mark
python3 tools/build_menu.py                              # pack/config/fancymenu/ (layout + assets) and the sponsor sprites
python3 tools/test_client.py --menu --size 1920x1080     # screenshot of the real title screen: run/client/menu.png
```

To use a different background, take a 1920×1080 screenshot in the pack (F1 hides the HUD) and pass it to
`render.cjs`. Keep the left third fairly dark or empty: the logo and buttons sit there.

The small icon buttons (Create, language, Supplementaries, accessibility) sit in the bottom-left corner, placed by
`pack/kubejs/client_scripts/remnants/title_menu.js`, because FancyMenu 3.9.14 can't target the 1.21.1 language and
accessibility buttons. The "Need a server?" button is not a FancyMenu element either: `tools/build_menu.py` copies its sprites to
`pack/kubejs/assets/remnants/textures/gui/sprites/sponsor/` and
`pack/kubejs/client_scripts/remnants/community.js` adds a vanilla button on the title screen and on the Multiplayer
screen (see "Community server and sponsor" in `design/LAUNCH.md`). The eclipsed sun in the sky is `pack/kubejs/assets/minecraft/textures/environment/sun.png`.

## Fonts

Cinzel, Cinzel Decorative and EB Garamond, all SIL Open Font License 1.1 (`fonts/OFL-*.txt`). They may be bundled
and used in commercial work; the font files themselves can't be sold on their own.

## Disclosure

The art was written as SVG/HTML code by an AI assistant (no image generator was used) over a real screenshot.
Modrinth bans AI-generated icons and gallery images; whether code-drawn vector art counts is the owner's call.
Check each platform's rules before upload, and disclose the same way as the rest of the pack (see
`design/LAUNCH.md`).
