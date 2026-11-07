## 1.0.0-beta.11: A Book of Our Own

### Changed

- **New quest book: Core RPG - Quests Engine.** NightBeam's own quest mod replaces the six FTB mods (Quests,
  Library, Teams, Filter System, XMod Compat and Ultimine). Every chapter, quest, reward table and voiced line of
  the Keeper carried over: 33 chapters, 667 quests, 41 reward tables.
  - Open the book with **Ctrl + J** (J alone still toggles your objectives), or use the quest book you are given
    when you join.
  - **Vein mining** is built in: hold **`** (the grave key, as before) while you mine. Scroll with it held to
    change the shape.
  - Parties are made with **/team** (`/team create <name>`, then `/team invite <player>`), or from the team screen.
- **The pack is now on Modrinth too.** Every mod is on both CurseForge and Modrinth, so both get the same pack.
  AllTheLeaks (CurseForge-only) was removed; ModernFix and FerriteCore already cover it.

### Updating an existing world

Quest progress and parties from FTB Quests do not carry over: the new book starts fresh in a world from beta 10 or
earlier, and parties have to be made again with /team. Your items, levels, runes and the world itself are untouched.
A new world is the cleanest start. To skip ahead in an old world, an operator can complete quests you already did
with `/cq complete <player> <quest or chapter>` (for example `/cq complete @s s1_prologue`).
