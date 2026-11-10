# Marketing: the CurseForge page

The project page for Remnants | The Modpack, in the same layout as NightBeam's other pages (Remnant Bosses, Runeborn):
a banner, a divider, a header and a card per section, bullet lists and a couple of GIFs.

| File | Size | What it is |
|---|---|---|
| `CURSEFORGE.md` | | The page text (CurseForge's Markdown editor). Images load from this repo's `main` branch on raw.githubusercontent.com |
| `MODRINTH.md` | | The same page for Modrinth: Modrinth install steps, Modrinth credit links, and the AI-use disclosure Modrinth requires |
| `../art/sponsors/apex-hosting-banner-849x141.png` | 849×141 | The sponsor banner, as Apex Hosting supplied it; both pages link it to https://apexhost.gg/NightBeam |
| `images/banner.png` | 1800×600 | Title, tagline and chips over the eclipse at sunset |
| `images/divider.png` | 1400×40 | Gold rule with a diamond (transparent) |
| `images/header-*.png` | 1400×120 | Section headers: threshold, story, bosses, systems, world, install (transparent edges) |
| `images/card-*.png` | 1600×900 | Feature cards: threshold, story, sovereigns, remnants, soulslike, world |
| `images/gifs/odric.gif`, `felled.gif` | 600 wide, 12 fps | Ser Odric's Ash Slam; his fall in soul fire |
| `images/trailer.png` | 1600×900 | A trailer frame with a play button, linked to the trailer on YouTube (https://youtu.be/U_x7PBLXGaM) |

## Before you paste the page

The images load from this repository's `main` branch on raw.githubusercontent.com, which needs the repository to stay
**public** (it is, like the other NightBeam repos). If it ever goes private, every image on the CurseForge page turns
into its alt text; upload the PNGs and GIFs through CurseForge's own image uploader and swap the URLs instead.

## The sponsor block (Apex Hosting)

Both pages carry the sponsor banner, a "Sponsored by Apex Hosting" label, the code APEX25 and the community server
address (`sv6af1d94aa636b.apexmc.co:1376`). Where it sits differs, because the platforms' rules differ:

- **CurseForge: at the bottom, after the description.** Its Moderation Policies (checked 2026-11-10) say server
  hosting affiliate banners "must appear at the bottom of the page, following the project description", of
  "reasonable size", and that the top of a page may hold functional link badges only, with no promotional material.
  A hosting banner at the top of a CurseForge page is therefore against the rules. The one allowed top placement is
  CurseForge's own slot: Author Console -> the project -> Description -> server hosting affiliation, which takes a
  custom banner of 884×58 and a partner URL (the supplied banner is 849×141, so Apex would have to provide that size).
- **Modrinth: at the top,** under the title banner. Its Content Rules have no placement rule; they ask that anything
  shown in an image is also there as text (it is) and that links lead to relevant public pages. Since 2026-09-27 a
  project that contains advertising or sponsorships must switch on the **advertising disclosure** in its settings:
  do that before publishing this version, because the pack itself now carries the sponsor button.
- The banner loads from this repository's `main` branch, so it shows only once this change is merged. Paste the
  pages after the merge, not before.
- Re-read both rule pages when the sponsor changes: https://support.curseforge.com/en/support/solutions/articles/9000197279-moderation-policies
  and https://modrinth.com/legal/rules.

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
