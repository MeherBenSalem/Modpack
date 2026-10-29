// Echo of the Fallen: where an Ashborn dies, an Echo of them rises, wearing their armour and holding their weapon,
// standing over the runes Runeborn left on the ground. Kill your Echo to take them back. Die again first and the
// old Echo fades (so do the runes; that part is Runeborn's rule).
// The copies have a 0% drop chance (set as SNBT floats), so nothing is duplicated; real items wait in the corpse.

const ECHO_TAG = 'remnants_echo'
const ECHO_SKIP_DIMENSIONS = ['tbos:fractured_archive', 'remnants:threshold'] // own death rules; no Echo in the tutorial
const ECHO_HEALTH_BONUS = 1.0   // +100% max health on top of whatever RPG Mobs rolls
const ECHO_DAMAGE_BONUS = 0.5   // +50% attack damage

function echoMobFor(dimension) {
  if (dimension === 'minecraft:the_nether') return 'minecraft:wither_skeleton'
  if (dimension === 'minecraft:the_end') return 'minecraft:enderman'
  return 'minecraft:zombie'
}

function echoPlayerTag(player) {
  return `${ECHO_TAG}_${String(player.username).toLowerCase()}`
}

// Raise an Echo at x/y/z. `gear` is the fallen player (their equipment is copied) or null.
function echoRaise(server, level, x, y, z, username, tag, gear) {
  var echo = level.createEntity(echoMobFor(String(level.dimension)))
  if (!echo) return null
  echo.setPosition(x, y, z)
  echo.addTag(ECHO_TAG)
  echo.addTag(tag)
  if (gear) {
    echo.headArmorItem = gear.headArmorItem.copy()
    echo.chestArmorItem = gear.chestArmorItem.copy()
    echo.legsArmorItem = gear.legsArmorItem.copy()
    echo.feetArmorItem = gear.feetArmorItem.copy()
    echo.mainHandItem = gear.mainHandItem.copy()
    echo.offHandItem = gear.offHandItem.copy()
  }
  echo.spawn()

  // The newest Echo is the one carrying this tag nearest to where it rose (older ones were killed first).
  var at = `execute in ${String(level.dimension)} positioned ${x} ${y} ${z} run`
  var self = `@e[tag=${tag},limit=1,sort=nearest]`
  var name = JSON.stringify(JSON.stringify({ text: `Echo of ${username}`, color: 'dark_red', italic: false }))
  server.runCommandSilent(`${at} attribute ${self} minecraft:generic.max_health modifier add remnants:echo_health ${ECHO_HEALTH_BONUS} add_multiplied_total`)
  server.runCommandSilent(`${at} attribute ${self} minecraft:generic.attack_damage modifier add remnants:echo_damage ${ECHO_DAMAGE_BONUS} add_multiplied_total`)
  server.runCommandSilent(`${at} effect give ${self} minecraft:fire_resistance infinite 0 true`)
  // Health last: loading Health clamps it to the new, higher maximum.
  server.runCommandSilent(`${at} data merge entity ${self} {PersistenceRequired:1b,CanPickUpLoot:0b,CustomNameVisible:1b,` +
    `ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f],CustomName:${name},Health:4096.0f}`)
  return echo
}

EntityEvents.death('minecraft:player', event => {
  var player = event.entity
  var server = event.server
  var level = event.level
  if (ECHO_SKIP_DIMENSIONS.includes(String(level.dimension))) return
  if (server.persistentData.getBoolean('remnants_echoes_off')) return

  var tag = echoPlayerTag(player)
  // The previous Echo fades with the runes it guarded.
  server.runCommandSilent(`kill @e[tag=${tag}]`)
  if (echoRaise(server, level, player.x, player.y, player.z, player.username, tag, player)) {
    server.runCommandSilent(`tellraw ${player.username} [{"text":"Where you fell, ","color":"gray"},` +
      `{"text":"your Echo rises","color":"dark_red"},{"text":". It guards your runes.","color":"gray"}]`)
  }
})

EntityEvents.death(event => {
  var e = event.entity
  if (e.isPlayer() || !e.tags.contains(ECHO_TAG)) return
  var killer = event.source.actual
  if (killer && killer.isPlayer()) {
    event.server.runCommandSilent(`title ${killer.username} actionbar {"text":"Echo laid to rest","color":"gold"}`)
  }
})
