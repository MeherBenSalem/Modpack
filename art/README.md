# Pack art

The icon, logo, main-menu background and title card for Season 1. Everything is drawn as SVG/HTML in
`src/art.html` and rendered with the pre-installed Chromium; the only picture in it is a real in-game screenshot.

| File | Size | Where it goes |
|---|---|---|
| `out/icon.png` | 512×512 | CurseForge project avatar (upload on the project page; a modpack zip can't carry it) |
| `out/logo.png` | 1600×700, transparent | Main menu (copied into `pack/config/fancymenu/assets/`), page headers |
| `out/menu_background.png` | 1920×1080 | Main-menu background: the shot with a dark band on the left for the buttons |
| `out/title_card.png` | 1920×1080 | First gallery image, page banner, video thumbnail base |
| `shots/ember_shrine_sunset.png` | 1920×1080 | The in-game shot: an Ashborn-armoured stand at an Ember Shrine at sunset |

## Regenerate

```bash
node art/render.cjs art/shots/ember_shrine_sunset.png   # art/out/*.png
python3 tools/build_menu.py                              # pack/config/fancymenu/ (layout + assets)
python3 tools/test_client.py --menu --size 1920x1080     # screenshot of the real title screen: run/client/menu.png
```

To use a different background, take a 1920×1080 screenshot in the pack (F1 hides the HUD) and pass it to
`render.cjs`. Keep the left third fairly dark or empty: the logo and buttons sit there.

The small icon buttons under the column (Create, language, Supplementaries, accessibility) are lined up by
`pack/kubejs/client_scripts/remnants/title_menu.js`, because FancyMenu 3.9.14 can't target the 1.21.1 language and
accessibility buttons. If you move the column in `build_menu.py`, change the numbers at the top of that script too.

## Fonts

Cinzel, Cinzel Decorative and EB Garamond, all SIL Open Font License 1.1 (`fonts/OFL-*.txt`). They may be bundled
and used in commercial work; the font files themselves can't be sold on their own.

## Disclosure

The art was written as SVG/HTML code by an AI assistant (no image generator was used) over a real screenshot.
Modrinth bans AI-generated icons and gallery images; whether code-drawn vector art counts is the owner's call.
Check each platform's rules before upload, and disclose the same way as the rest of the pack (see
`design/LAUNCH.md`).
