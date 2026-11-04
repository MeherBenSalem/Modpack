# Reel plan: Remnants: Ashen Legacy, 1.0.0-beta.9 "The Keeper's Voice"

A 53.5 s vertical trailer (1080×1920, 60 fps) for YouTube Shorts, Instagram Reels and TikTok, and the same edit
re-framed to 1920×1080. Only real footage of this pack. The Keeper narrates, in the voice beta 9 gives him.

## The idea

Beta 9's news is that the Keeper speaks: an opening tale on first join, a word for every land, every act. So the
trailer *is* the Keeper telling the tale, using his real in-game recordings, while the footage shows the pack doing
exactly what he says. The beats are the pitch from `design/STORY.md`: the sun was eaten, the dead come back wrong, you
wake as an Ashborn, the fights, your own Echo, relight the world.

## Structure (music: "Epical Drums 03", 80 BPM, one continuous excerpt from 126.04 s, placed at 4.0 s)

| Reel time | Shot (all real captures) | Keeper (existing in-game takes) | Music / sound |
| --- | --- | --- | --- |
| 0.0–4.75 | Black, then the real first-join intro card: "Once, there was one sun." | "Listen." / "Once, the world had one sun…" | A church bell, low wind; "AN OPENING TALE ON YOUR FIRST JOIN"; the music enters at 4.0 |
| 4.75–7.75 | The Threshold at its frozen dusk: the Ashborn walks toward the black sun | "He drank the last of the light himself," | Trailer whoosh-impact on the reveal |
| 7.75–10.0 | The Overworld: the eclipsed sun over a valley; the Ashborn's helm crosses its disc | "…and the sky went" | |
| 10.0–12.25 | The Eclipsed Realm: tilt up to its black sun | "…black." | Deep impact on "black" |
| 12.25–17.5 | A Champion (level and rank plates) walks out of the sunset, an Elite and a named Remnant behind; the fight | "Nothing that dies here stays dead. It comes back wrong." | Darkness sweep |
| 17.5–21.25 | `/threshold send`: the crypt and "The Threshold" | "But you came back with a spark still in you." | The Threshold's bell; "BETA 9 · THE KEEPER'S VOICE" |
| 21.25–25.0 | Through the fog gate; Ser Odric rises under the black sun | "Fog. Beyond it, Odric." | The music's breakdown; a horn |
| 25.0–30.25 | Ser Odric: swings, a flask, his Ash Slam lands on the word "lands" | "You're not strong yet, so don't be there when it lands." | The drop at 25.0; blades; the slam |
| 30.25–37.0 | The Champion; then a Sovereign: the Dusk Rider's title card and charge | | Blades on the beat; a horn |
| 37.0–43.0 | Your Echo wears your armour where you fell; you fight it | "Something is wearing your face, and it is holding your light." | Heartbeat, low horn |
| 43.0–49.0 | Kindled Ember Shrines at dusk; the Dusk Rider in its darkness pulse on "Sovereign" | "Relight the world, one shrine and one Sovereign at a time." | |
| 49.0–53.5 | Title over the Ashborn facing the black sun | "Now, wake up." | Final hit at 49.0; "BETA 9 · OUT NOW ON CURSEFORGE"; the bell again |

Left out on purpose: the area-name cards and the Keeper's line for each new land. In this build they never fired
while recording (regions.js reaches its settle check but never writes `remnants_region_seen`; something after it
throws inside a silent try/catch), so the reel does not show or claim them. Reported to the owner as a bug.

`source/plan.py` is the single source of truth: it turns this into exact times on the beat grid, checks that every
line fits its slot (it refuses a plan where one would not), and writes `edl.json`, `cues.json` and `SCRIPT.md`.

## Rules this follows

- The pack is called **Remnants: Ashen Legacy**; the story's own names only; "soulslike", never another game. Only
  beta 9 features are claimed, and only CurseForge is named as a store.
- The Eclipsed Realm's great golden tree never appears (every realm shot faces south, away from it).
- Narration is never sped up or stretched; the edit is timed around the real lines.
- Footage is never played slower than real time; every output frame comes from a real render (about 119 renders
  per game second were captured, see `source/prep.py`).
- The voice gets only the channel narration chain; the music is sidechain-ducked under it.
