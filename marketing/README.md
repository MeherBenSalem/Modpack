# Marketing: the CurseForge page

The project page for Remnants | The Modpack, in the same layout as NightBeam's other pages (Remnant Bosses, Runeborn):
a banner, a divider, a header and a card per section, bullet lists and a couple of GIFs.

| File | Size | What it is |
|---|---|---|
| `CURSEFORGE.md` | | The page text (CurseForge's Markdown editor). Images load from this repo's `main` branch on raw.githubusercontent.com |
| `images/banner.png` | 1800×600 | Title, tagline and chips over the eclipse at sunset |
| `images/divider.png` | 1400×40 | Gold rule with a diamond (transparent) |
| `images/header-*.png` | 1400×120 | Section headers: threshold, story, bosses, systems, world, install (transparent edges) |
| `images/card-*.png` | 1600×900 | Feature cards: threshold, story, sovereigns, remnants, soulslike, world |
| `images/gifs/odric.gif`, `felled.gif` | 600 wide, 12 fps | Ser Odric's Ash Slam; his fall in soul fire |

## Before you paste the page

**This repository is private, so raw.githubusercontent.com links won't load on CurseForge.** Either make the repository
public (the other NightBeam repos serve their page images this way), or upload the PNGs and GIFs through CurseForge's
own image uploader and swap the URLs in `CURSEFORGE.md`.

## Regenerate

```bash
node marketing/render.cjs              # every image in src/images.json -> images/
node marketing/render.cjs card-world   # one image
```

`src/marketing.html` draws each piece (fonts from `art/fonts`, SIL OFL). `src/images.json` holds the text, the stats
and which screenshot each card uses. The screenshots in `src/shots/` are frames of the trailer's in-game footage, recorded
inside this pack with the studio's frame-locked recorder (MeherBenSalem/moneymaker, `recorder/neoforge/`).

## Disclosure

The layout and type were drawn as HTML/CSS code by an AI assistant; every picture inside them is a real in-game frame.
Check CurseForge's current AI-disclosure rules at upload time and disclose the same way as the rest of the pack
(`design/LAUNCH.md`, `art/README.md`).
