// Balance fixes the mods' defaults can't express.

// The vanilla Warden is in Mob LootBags' default boss tag, so every kill drops 3 Epic-or-better bags. Ancient City
// shriekers summon a new Warden whenever they are triggered, so players farmed it endlessly for Legendary and Mythic
// bags (CurseForge, Nov 2026). Out of the boss tag, it drops bags like any other strong mob. Its VP per kill is capped
// in config/ras/mob_xp.json (src/stat_locks.yaml). Wither, Ender Dragon and Elder Guardian stay bosses: they don't
// respawn on demand.
ServerEvents.tags('entity_type', function (event) {
  event.remove('mob_loot_bags:bosses', 'minecraft:warden')
})

// Champions (RPG Mobs' champion rank: purple ring, own boss bar) are the Sovereigns' sworn champions of the story:
// killing one counts as Runeborn's champion feat and drops a Sovereign Fragment. Runeborn's own champions only spawn
// with its mob levels on, which the pack turns off (RPG Mobs ranks the mobs), so without this the Act I quest
// "Champion's Bane" (advancement runeborn:feats/champion) could never complete and champions carried no Fragments.
EntityEvents.death(function (event) {
  var e = event.entity
  if (e.isPlayer() || !e.tags.contains('remnant_mobs.champion')) return
  var killer = event.source.actual
  if (!killer || !killer.isPlayer()) return
  var server = event.server
  server.runCommandSilent(`advancement grant ${killer.username} only runeborn:feats/champion`)
  server.runCommandSilent(`execute in ${String(e.level.dimension)} run summon minecraft:item ${e.x} ${e.y + 0.5} ${e.z} {Item:{id:"runeborn:sovereign_fragment",count:1},PickupDelay:10}`)
})
