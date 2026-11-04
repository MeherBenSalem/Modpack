// Balance fixes the mods' defaults can't express.

// The vanilla Warden is in Mob LootBags' default boss tag, so every kill drops 3 Epic-or-better bags. Ancient City
// shriekers summon a new Warden whenever they are triggered, so players farmed it endlessly for Legendary and Mythic
// bags (CurseForge, Nov 2026). Out of the boss tag, it drops bags like any other strong mob. Its VP per kill is capped
// in config/ras/mob_xp.json (src/stat_locks.yaml). Wither, Ender Dragon and Elder Guardian stay bosses: they don't
// respawn on demand.
ServerEvents.tags('entity_type', function (event) {
  event.remove('mob_loot_bags:bosses', 'minecraft:warden')
})
