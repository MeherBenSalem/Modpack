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
// killing one drops a Sovereign Fragment and counts as Runeborn's champion feat. Runeborn's own champions only spawn
// with its mob levels on, which the pack turns off (RPG Mobs ranks the mobs), so without this champions carried no
// Fragments and runeborn:feats/champion was never granted.
//
// RPG Mobs and Runeborn both call their advancement "Champion's Bane". RPG Mobs awards its own
// (remnant_mobs:champions_bane) for any mob of champion rank or higher, to the attacker or to whoever hurt the mob
// last. Beta 10 granted Runeborn's only when the killing blow itself came from a player and the mob was exactly a
// champion, so a champion that burned in daylight, bled out, fell, or was finished by a sellsword or a pet showed the
// popup (RPG Mobs') and dropped nothing, and the Act I quest, which waited for Runeborn's, never completed. Now:
// - the quest reads remnant_mobs:champions_bane, the advancement the player really receives (s1_01_embers.yaml);
// - the Fragment and Runeborn's feat follow RPG Mobs' own rule (its Rewards.killer and Rewards.onDeath), below;
// - Runeborn's feat is also granted whenever RPG Mobs' advancement is earned, and at login to anyone who already
//   has it, so the two never disagree again, in old worlds too.
var CHAMPION_ADVANCEMENT = 'remnant_mobs:champions_bane'
var CHAMPION_FEAT = 'runeborn:feats/champion'
var CHAMPION_RANK_TAGS = ['remnant_mobs.champion', 'remnant_mobs.remnant']   // champion rank or higher
var CHAMPION_DATA_TAG = 'remnant_mobs:data|'    // remnant_mobs:data|level|rank|traits|seed|flags
var CHAMPION_MINION_FLAG = 2                    // RPG Mobs' MobData.MINION: summoned by a trait, pays nothing

function championRanked(entity) {
  var ranked = false
  var minion = false
  entity.tags.forEach(function (tag) {
    tag = String(tag)
    if (CHAMPION_RANK_TAGS.indexOf(tag) >= 0) ranked = true
    if (tag.indexOf(CHAMPION_DATA_TAG) === 0) {
      var flags = parseInt(tag.split('|')[5] || '0', 10)
      if (!isNaN(flags) && (flags & CHAMPION_MINION_FLAG) !== 0) minion = true
    }
  })
  return ranked && !minion
}

// The player a kill belongs to, as RPG Mobs decides it: the attacker, or whoever hurt the mob last.
function championKiller(entity, source) {
  var killer = source.actual
  if (!killer || !killer.isPlayer()) killer = entity.getKillCredit()
  if (!killer || !killer.isPlayer() || killer.isFake()) return null
  return killer
}

EntityEvents.death(function (event) {
  var e = event.entity
  if (e.isPlayer() || !championRanked(e)) return
  var killer = championKiller(e, event.source)
  if (!killer) return
  var server = event.server
  server.runCommandSilent(`advancement grant ${killer.username} only ${CHAMPION_FEAT}`)
  server.runCommandSilent(`execute in ${String(e.level.dimension)} run summon minecraft:item ${e.x} ${e.y + 0.5} ${e.z} {Item:{id:"runeborn:sovereign_fragment",count:1},PickupDelay:10}`)
})

PlayerEvents.advancement(function (event) {
  if (String(event.advancement.id) !== CHAMPION_ADVANCEMENT) return
  event.server.runCommandSilent(`advancement grant ${event.player.username} only ${CHAMPION_FEAT}`)
})

// Worlds from beta 10 and earlier: the popup came, Runeborn's feat did not.
PlayerEvents.loggedIn(function (event) {
  event.server.runCommandSilent(`execute as ${event.player.username} if entity @s[advancements={${CHAMPION_ADVANCEMENT}=true,${CHAMPION_FEAT}=false}] run advancement grant @s only ${CHAMPION_FEAT}`)
})
