// The Threshold: where every new Ashborn wakes. A floating ruin in its own dimension (remnants:threshold, frozen at
// dusk), built once per world by function remnants:threshold/build (tools/build_threshold.py writes both the function
// and the coordinates in threshold_layout.js).
//
// A new player picks an origin (Runeborn's screen), the screen fades to black and they wake in the Crypt while the
// Keeper speaks. West through the Hall of Messages, through the fog gate, into the Arena: Ser Odric, the Gatekeeper.
// Fell him, or fall to him once, and the Ember Door opens; the Last Stair leads to the Waygate and the world.
//
// Multiplayer: everyone shares one Threshold. Whoever is inside the arena when the fog seals fights together; others
// wait at the fog until the fight ends. Each player's progress is their own (persistentData remnants_threshold:
// "" -> pending -> hub -> done). Players who had already played before this existed skip it. Ops: /threshold.
// Wrapped in a function: server scripts share one scope, and these helper names are generic.

(function () {
var T = global.THRESHOLD
var GameType = Java.loadClass('net.minecraft.world.level.GameType')
var DIM = T.dimension
var STATE = 'remnants_threshold'
var BOSS_TAG = 'remnants_gatekeeper'
var SQUIRE_TAG = 'remnants_squire'
var BOSSBAR = 'remnants:gatekeeper'
var BOSS_NAME = 'Ser Odric'
var BOSS_TITLE = 'Gatekeeper of the Threshold'
var SKIP_IF_PLAYED_TICKS = 6000      // players with 5+ minutes on this world before the Threshold existed skip it
var ORIGIN_WAIT_TICKS = 3600         // start anyway if no origin was picked within 3 minutes
var SLAM_EVERY = 8                   // checks (of 10 ticks) between Ash Slams
var SLAM_RADIUS = 5
// Damage before the pack's player-health scaling (~16x: a raw 7 took 116 of a fresh Knight-Errant's 250 HP).
var SLAM_DAMAGE = 3                  // ~50 after scaling
var ODRIC_ATTACK = 1.6               // base attack -> ~3.7 raw after level and rank, ~60 a hit: four hits kill
var EMPTY_GRACE = 6                  // checks (3 s) the arena may look empty before the fight resets

var fight = null                     // {participants: [names], checks, slamIn, phase2}
var counter = 0

function inThreshold(p) { return String(p.level.dimension) === DIM }
function state(p) { return p.persistentData.getString(STATE) }
function setState(p, s) { p.persistentData.putString(STATE, s) }
function cmd(server, c) { return server.runCommandSilent(c) }
function inDim(c) { return `execute in ${DIM} run ${c}` }
function json(o) { return JSON.stringify(o) }

// server.getPlayer() takes a UUID in KubeJS 2101; the Threshold keeps names, so look players up by name.
function playerNamed(server, name) {
  var found = null
  server.players.forEach(function (p) { if (!found && String(p.username) === String(name)) found = p })
  return found
}

function titleCard(server, name, title, subtitle, fadeIn, stay, fadeOut) {
  cmd(server, `title ${name} times ${fadeIn || 10} ${stay || 60} ${fadeOut || 20}`)
  cmd(server, `title ${name} subtitle ${json(subtitle || { text: '' })}`)
  cmd(server, `title ${name} title ${json(title || { text: '' })}`)
}

// An area name, the way regions.js shows them: subtitle-sized (fits any GUI scale), flavour in the action bar.
function areaCard(server, name, area, flavour) {
  cmd(server, `title ${name} times 25 70 30`)
  cmd(server, `title ${name} subtitle ${json({ text: area, color: '#E8D5A3' })}`)
  cmd(server, `title ${name} title ${json({ text: '' })}`)
  cmd(server, `title ${name} actionbar ${json({ text: flavour, color: 'gray', italic: true })}`)
}

function grant(server, name, key) {
  cmd(server, `advancement grant ${name} only remnants:threshold/${key}`)
}

function narrate(server, p, line, chat) {
  remnantsNarrate(server, p, line, chat)
}

// ---------------------------------------------------------------- building

function ensureBuilt(server) {
  if (server.persistentData.getInt('remnants_threshold_built') >= T.version) return
  var f = T.forceload
  cmd(server, inDim(`forceload add ${f[0]} ${f[1]} ${f[2]} ${f[3]}`))
  server.scheduleInTicks(60, function () {
    cmd(server, inDim('function remnants:threshold/build'))
    server.scheduleInTicks(20, function () {
      cmd(server, inDim('forceload remove all'))
      server.persistentData.putInt('remnants_threshold_built', T.version)
      console.info(`[Remnants] The Threshold was built (layout v${T.version})`)
    })
  })
}

ServerEvents.loaded(function (event) {
  var server = event.server
  ensureBuilt(server)
  // A fight can't survive a restart: clear any Gatekeeper left over and reopen the fog.
  server.scheduleInTicks(100, function () { resetFight(server, false) })
})

// ---------------------------------------------------------------- arrival

function playTime(p) {
  try { return p.stats.getPlayTime() } catch (e) { return 0 }
}

PlayerEvents.loggedIn(function (event) {
  var p = event.player
  var server = event.server
  if (state(p) !== '') return
  if (server.persistentData.getBoolean('remnants_threshold_off') || playTime(p) > SKIP_IF_PLAYED_TICKS) {
    skip(server, p)
    return
  }
  setState(p, 'pending')
  p.persistentData.putInt('remnants_threshold_wait', 0)
})

function skip(server, p) {
  setState(p, 'done')
  grant(server, p.username, 'woke')
  grant(server, p.username, 'beyond')
}

// Runeborn hands out the Ember Flask with the origin. (runCommandSilent returns nothing in KubeJS 2101, so this
// reads the inventory instead of asking `execute if items`.)
function hasOrigin(server, p) {
  var inv = p.inventory
  for (var i = 0; i < inv.getContainerSize(); i++) {
    var st = inv.getItem(i)
    if (!st.isEmpty() && String(st.id) === 'runeborn:ember_flask') return true
  }
  return false
}

// The wake: black screen, a bell, the Keeper's voice, the area name.
function wake(server, p) {
  var name = p.username
  var w = T.wake
  setState(p, 'hub')
  if (!p.isCreative() && !p.isSpectator()) {
    p.persistentData.putBoolean('remnants_threshold_adv', true)
    p.setGameMode(GameType.ADVENTURE)          // the API, not /gamemode: no chat message
  }
  cmd(server, `effect give ${name} minecraft:blindness 7 0 true`)
  cmd(server, `effect give ${name} minecraft:slowness 6 255 true`)
  cmd(server, `effect give ${name} minecraft:resistance 10 4 true`)
  cmd(server, inDim(`tp ${name} ${w[0]} ${w[1]} ${w[2]} ${w[3]} 15`))
  cmd(server, inDim(`spawnpoint ${name} ${Math.floor(w[0])} ${w[1]} ${Math.floor(w[2])} ${w[3]}`))
  grant(server, name, 'woke')
  server.scheduleInTicks(30, function () {
    cmd(server, `execute as ${name} at @s run playsound minecraft:block.bell.resonate ambient @s ~ ~ ~ 0.7 0.5`)
    titleCard(server, name, { text: '' }, { text: 'The sun was eaten an age ago.', color: 'dark_gray', italic: true }, 30, 50, 30)
  })
  server.scheduleInTicks(70, function () {
    var pl = playerNamed(server, name)
    if (pl) narrate(server, pl, 's1_prologue_rise', false)
  })
  server.scheduleInTicks(150, function () {
    areaCard(server, name, 'The Threshold', 'Where the Ashborn rise')
    cmd(server, `execute as ${name} at @s run playsound minecraft:block.beacon.ambient ambient @s ~ ~ ~ 1 0.6`)
  })
  server.scheduleInTicks(260, function () {
    cmd(server, `title ${name} actionbar ${json({ text: 'Walk toward the black sun. Roll with Left Alt.', color: 'gray' })}`)
  })
}

// ---------------------------------------------------------------- per-player checks (every 10 ticks)

function playerTick(server, p) {
  var s = state(p)
  if (s === 'pending') {
    var waited = p.persistentData.getInt('remnants_threshold_wait') + 10
    p.persistentData.putInt('remnants_threshold_wait', waited)
    if (hasOrigin(server, p) || waited >= ORIGIN_WAIT_TICKS) wake(server, p)
    return
  }
  if (s !== 'hub') return
  if (!inThreshold(p)) {                     // e.g. died and respawned elsewhere: bring them back
    var w = T.wake
    cmd(server, inDim(`tp ${p.username} ${w[0]} ${w[1]} ${w[2]} ${w[3]} 0`))
    return
  }
  var x = p.x, z = p.z
  var name = p.username
  var eligible = p.persistentData.getString('remnants_threshold_gate') !== ''   // 'fell' or 'felled'

  if (x < -28 && !p.persistentData.getBoolean('remnants_threshold_heard_gate')) {
    p.persistentData.putBoolean('remnants_threshold_heard_gate', true)
    narrate(server, p, 'threshold_gate', true)
  }
  if (x < T.gate.x - 1.5 && x > T.exit_door.x + 1 && !fight && !eligibleFelled(p)) startFight(server)
  if (fight && x > T.gate.x + 0.5 && x < T.gate.x + 3 && fight.participants.indexOf(name) < 0) {
    cmd(server, `title ${name} actionbar ${json({ text: 'The fog will not part. Someone is already fighting.', color: 'gray' })}`)
  }
  // The Ember Door in the crypt, and the one behind the arena: both open only for those who faced Odric.
  var d = T.ember_door
  if (x >= d.x1 - 0.5 && x <= d.x2 + 1.5 && z > d.z - 0.2) {
    if (eligible) passDoor(server, p)
    else cmd(server, `title ${name} actionbar ${json({ text: 'The Ember Door is cold.', color: 'gray', italic: true })}`)
  }
  var e = T.exit_door
  if (x < e.x + 1.6 && x > e.x - 1 && Math.abs(z - 0.5) < 3) {
    if (eligible && !fightHas(name)) passDoor(server, p)
    else cmd(server, `title ${name} actionbar ${json({ text: 'The Ember Door is cold. Something still keeps this gate.', color: 'gray', italic: true })}`)
  }
  if (x < T.waygate.x + 0.5 && Math.abs(z - 0.5) < 3) leave(server, p)
}

function eligibleFelled(p) { return p.persistentData.getString('remnants_threshold_gate') === 'felled' }
function fightHas(name) { return fight && fight.participants.indexOf(name) >= 0 }

function passDoor(server, p) {
  var name = p.username
  var s = T.stair_start
  cmd(server, `effect give ${name} minecraft:blindness 2 0 true`)
  cmd(server, `execute as ${name} at @s run playsound minecraft:block.respawn_anchor.set_spawn ambient @s ~ ~ ~ 0.8 0.7`)
  cmd(server, inDim(`tp ${name} ${s[0]} ${s[1]} ${s[2]} ${s[3]} 0`))
}

// The Waygate: a flash, the world, the area name.
function leave(server, p) {
  var name = p.username
  setState(p, 'leaving')
  cmd(server, `effect give ${name} minecraft:blindness 4 0 true`)
  cmd(server, `effect give ${name} minecraft:slowness 3 255 true`)
  cmd(server, `execute as ${name} at @s run playsound minecraft:block.end_portal.spawn ambient @s ~ ~ ~ 0.35 1.3`)
  titleCard(server, name, { text: '' }, { text: 'You step through the Waygate…', color: 'dark_gray', italic: true }, 10, 30, 10)
  server.scheduleInTicks(40, function () {
    var pl = playerNamed(server, name)
    if (!pl) return
    var spawn = server.overworld().getSharedSpawnPos()
    if (pl.persistentData.getBoolean('remnants_threshold_adv')) {
      pl.setGameMode(GameType.SURVIVAL)
      pl.persistentData.putBoolean('remnants_threshold_adv', false)
    }
    cmd(server, `execute in minecraft:overworld run spreadplayers ${spawn.x} ${spawn.z} 0 6 false ${name}`)
    cmd(server, `execute as ${name} at @s run spawnpoint @s ~ ~ ~`)
    setState(pl, 'done')
    grant(server, name, 'beyond')
    server.scheduleInTicks(20, function () {
      areaCard(server, name, 'The Lands Under Ash', 'Find the smoke. Find the living.')
      var again = playerNamed(server, name)
      if (again) narrate(server, again, 'threshold_beyond', true)
    })
  })
}

// ---------------------------------------------------------------- the Gatekeeper

function level(server) { return server.getLevel(DIM) }

function arenaPlayers(server) {
  var a = T.arena
  var out = []
  server.players.forEach(function (p) {
    if (!inThreshold(p) || state(p) !== 'hub') return
    var dx = p.x - a.cx, dz = p.z - a.cz
    if (dx * dx + dz * dz <= (a.r + 2) * (a.r + 2) && p.x < T.gate.x && p.isAlive()) out.push(p)
  })
  return out
}

function findBoss(server) {
  var found = null
  level(server).getEntities().forEach(function (e) { if (!found && e.tags.contains(BOSS_TAG)) found = e })
  return found
}

function sealGate(server, sealed) {
  var g = T.gate
  cmd(server, inDim(`fill ${g.x} ${g.y1} ${g.z1} ${g.x} ${g.y2} ${g.z2} ${sealed ? 'minecraft:barrier' : 'minecraft:air'} replace ${sealed ? 'minecraft:air' : 'minecraft:barrier'}`))
}

function startFight(server) {
  var players = arenaPlayers(server)
  if (players.length === 0) return
  fight = { participants: players.map(function (p) { return p.username }), checks: 0, slamIn: SLAM_EVERY, phase2: false, spawned: false, empty: 0 }
  sealGate(server, true)
  var b = T.arena.boss
  players.forEach(function (p) {
    var n = p.username
    p.persistentData.putBoolean('remnants_threshold_fought', true)
    cmd(server, `effect give ${n} minecraft:slowness 2 4 true`)
    titleCard(server, n, { text: BOSS_NAME, color: 'gold', bold: true }, { text: BOSS_TITLE, color: 'gray', italic: true }, 10, 50, 20)
    cmd(server, `execute as ${n} at @s run playsound minecraft:event.raid.horn hostile @s ~ ~ ~ 0.6 0.6`)
  })
  cmd(server, inDim(`particle minecraft:soul_fire_flame ${b[0]} ${b[1] + 1} ${b[2]} 0.6 1.5 0.6 0.05 120 force`))
  server.scheduleInTicks(30, function () { spawnBoss(server) })
}

function spawnBoss(server) {
  if (!fight) return
  var b = T.arena.boss
  var at = `execute in ${DIM} positioned ${b[0]} ${b[1]} ${b[2]} run`
  // RPG Mobs fixes his level, rank and traits; fall back to a plain summon if its command ever changes.
  cmd(server, `${at} remnants spawn minecraft:wither_skeleton 8 elite crushing,berserk`)
  cmd(server, `${at} tag @e[type=minecraft:wither_skeleton,distance=..4,limit=1,sort=nearest,tag=!${BOSS_TAG}] add ${BOSS_TAG}`)
  if (!findBoss(server)) {
    cmd(server, `${at} summon minecraft:wither_skeleton ~ ~ ~ {Tags:["${BOSS_TAG}"]}`)
  }
  var self = `@e[tag=${BOSS_TAG},limit=1]`
  var name = json(json({ text: BOSS_NAME, color: 'gold', italic: false }))
  cmd(server, inDim(`attribute ${self} minecraft:generic.scale base set 1.45`))
  cmd(server, inDim(`attribute ${self} minecraft:generic.knockback_resistance base set 0.85`))
  cmd(server, inDim(`attribute ${self} minecraft:generic.max_health modifier add remnants:odric_health 3.0 add_multiplied_total`))
  cmd(server, inDim(`attribute ${self} minecraft:generic.follow_range base set 48`))
  cmd(server, inDim(`attribute ${self} minecraft:generic.attack_damage base set ${ODRIC_ATTACK}`))
  cmd(server, inDim(`data merge entity ${self} {PersistenceRequired:1b,CanPickUpLoot:0b,CustomNameVisible:1b,CustomName:${name},` +
    `HandItems:[{id:"minecraft:netherite_sword",count:1,components:{"minecraft:attribute_modifiers":{modifiers:[]}}},{}],` +
    `ArmorItems:[{},{},{id:"minecraft:chainmail_chestplate",count:1},{id:"minecraft:netherite_helmet",count:1}],` +
    `ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f],Rotation:[-90f,0f],Health:4096.0f}`))
  var boss = findBoss(server)
  cmd(server, `bossbar add ${BOSSBAR} ${json({ text: BOSS_NAME + ', ' + BOSS_TITLE, color: 'gold' })}`)
  cmd(server, `bossbar set ${BOSSBAR} color red`)
  cmd(server, `bossbar set ${BOSSBAR} style notched_10`)
  if (boss) cmd(server, `bossbar set ${BOSSBAR} max ${Math.ceil(boss.maxHealth)}`)
  cmd(server, `bossbar set ${BOSSBAR} players ${fight.participants.join(' ') || '@a[tag=__none__]'}`)
  cmd(server, inDim(`execute positioned ${b[0]} ${b[1]} ${b[2]} run playsound minecraft:entity.wither.spawn hostile @a[distance=..40] ~ ~ ~ 0.5 0.7`))
  fight.spawned = true
}

function fightTick(server) {
  if (!fight || !fight.spawned) return
  fight.checks++
  var boss = findBoss(server)
  // Who is still in it: alive, online, inside the arena.
  var inside = arenaPlayers(server).map(function (p) { return p.username })
  var present = fight.participants.filter(function (n) { return inside.indexOf(n) >= 0 })
  if (present.length === 0) {
    // knocked against the fog for a moment, or truly gone: wait EMPTY_GRACE checks before giving up
    if (++fight.empty >= EMPTY_GRACE) resetFight(server, false)
    return
  }
  fight.empty = 0
  // the dead and the departed leave the fight; the living stay in it
  fight.participants = fight.participants.filter(function (n) {
    var pl = playerNamed(server, n)
    return pl && pl.isAlive() && inThreshold(pl)
  })
  if (!boss) return
  cmd(server, `bossbar set ${BOSSBAR} value ${Math.max(0, Math.ceil(boss.health))}`)
  cmd(server, `bossbar set ${BOSSBAR} players ${fight.participants.join(' ')}`)
  if (!fight.phase2 && boss.health <= boss.maxHealth * 0.5) {
    fight.phase2 = true
    phaseTwo(server, boss)
  }
  if (--fight.slamIn <= 0) {
    fight.slamIn = fight.phase2 ? SLAM_EVERY - 3 : SLAM_EVERY
    ashSlam(server, boss)
  }
}

// Ash Slam: a roar and a ring of smoke, then a blast around him a second later. Roll out, or roll through.
function ashSlam(server, boss) {
  var x = boss.x, y = boss.y, z = boss.z
  var at = `execute in ${DIM} positioned ${x} ${y} ${z} run`
  cmd(server, `${at} playsound minecraft:entity.ravager.roar hostile @a[distance=..40] ~ ~ ~ 0.9 0.6`)
  cmd(server, `${at} particle minecraft:large_smoke ~ ~0.2 ~ ${SLAM_RADIUS / 2} 0.1 ${SLAM_RADIUS / 2} 0.01 160 force`)
  cmd(server, `${at} effect give @e[tag=${BOSS_TAG},distance=..3] minecraft:slowness 1 6 true`)
  server.scheduleInTicks(22, function () {
    var b = findBoss(server)
    if (!b || !fight) return
    var at2 = `execute in ${DIM} positioned ${b.x} ${b.y} ${b.z} run`
    cmd(server, `${at2} particle minecraft:explosion_emitter ~ ~0.5 ~ 0 0 0 0 1 force`)
    cmd(server, `${at2} particle minecraft:soul_fire_flame ~ ~0.2 ~ ${SLAM_RADIUS / 2} 0.2 ${SLAM_RADIUS / 2} 0.08 200 force`)
    cmd(server, `${at2} playsound minecraft:entity.generic.explode hostile @a[distance=..40] ~ ~ ~ 0.8 0.6`)
    cmd(server, `execute as @e[tag=${BOSS_TAG},limit=1] at @s run damage @a[distance=..${SLAM_RADIUS},gamemode=!spectator,gamemode=!creative] ${SLAM_DAMAGE} minecraft:mob_attack by @s`)
  })
}

function phaseTwo(server, boss) {
  var at = `execute in ${DIM} positioned ${boss.x} ${boss.y} ${boss.z} run`
  fight.participants.forEach(function (n) {
    titleCard(server, n, { text: '' }, { text: 'Odric remembers his oath.', color: 'red', italic: true }, 5, 40, 15)
  })
  cmd(server, `${at} playsound minecraft:entity.wither.ambient hostile @a[distance=..40] ~ ~ ~ 1 0.5`)
  cmd(server, `${at} particle minecraft:soul ~ ~1 ~ 2 1 2 0.05 80 force`)
  for (var i = 0; i < Math.min(2, fight.participants.length + 1); i++) {
    var dz = i === 0 ? -3 : 3
    var squire = json(json({ text: 'Hollow Squire', color: 'gray', italic: false }))
    cmd(server, `${at} summon minecraft:husk ~ ~ ~${dz} {Tags:["${SQUIRE_TAG}"],PersistenceRequired:1b,CustomName:${squire},` +
      `HandItems:[{id:"minecraft:iron_sword",count:1},{}],ArmorItems:[{},{},{},{id:"minecraft:chainmail_helmet",count:1}],` +
      `ArmorDropChances:[0.0f,0.0f,0.0f,0.0f],HandDropChances:[0.0f,0.0f]}`)
  }
}

function resetFight(server, won) {
  cmd(server, inDim(`kill @e[tag=${SQUIRE_TAG}]`))
  if (!won) cmd(server, inDim(`kill @e[tag=${BOSS_TAG}]`))
  cmd(server, `bossbar remove ${BOSSBAR}`)
  sealGate(server, false)
  fight = null
}

EntityEvents.death(function (event) {
  var e = event.entity
  var server = event.server
  if (e.isPlayer()) {
    if (inThreshold(e) && fightHas(e.username) && e.persistentData.getString('remnants_threshold_gate') === '') {
      e.persistentData.putString('remnants_threshold_gate', 'fell')
      e.persistentData.putBoolean('remnants_threshold_fell_new', true)
    }
    return
  }
  if (!e.tags.contains(BOSS_TAG)) return
  var winners = fight ? fight.participants.slice() : []
  arenaPlayers(server).forEach(function (p) { if (winners.indexOf(p.username) < 0) winners.push(p.username) })
  resetFight(server, true)
  var at = `execute in ${DIM} positioned ${e.x} ${e.y} ${e.z} run`
  cmd(server, `${at} particle minecraft:soul ~ ~1 ~ 1 2 1 0.08 200 force`)
  winners.forEach(function (n) {
    var p = playerNamed(server, n)
    if (!p) return
    p.persistentData.putString('remnants_threshold_gate', 'felled')
    titleCard(server, n, { text: 'FELLED', color: 'gold', bold: true }, { text: BOSS_NAME + ', ' + BOSS_TITLE + ', may rest.', color: 'gray', italic: true }, 10, 70, 30)
    cmd(server, `execute as ${n} at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.8 0.8`)
    cmd(server, `execute as ${n} at @s run playsound minecraft:block.beacon.activate master @s ~ ~ ~ 1 0.6`)
    grant(server, n, 'gatekeeper')
    cmd(server, `give ${n} minecraft:golden_apple 2`)
    cmd(server, `give ${n} runeborn:faded_rune 3`)
    server.scheduleInTicks(60, function () {
      var pl = playerNamed(server, n)
      if (pl) narrate(server, pl, 'threshold_victory', true)
    })
  })
})

PlayerEvents.respawned(function (event) {
  var p = event.player
  var server = event.server
  if (state(p) !== 'hub') return
  // The crypt keeps its dead: remains dropped anywhere in the Threshold are carried back beside the coffins.
  server.scheduleInTicks(20, function () {
    cmd(server, inDim('tp @e[type=corpse:corpse,x=-130,y=0,z=-30,dx=118,dy=120,dz=60] -8.5 65.1 -2.5'))
  })
  var fell = p.persistentData.getBoolean('remnants_threshold_fell_new') ||
    (p.persistentData.getBoolean('remnants_threshold_fought') && p.persistentData.getString('remnants_threshold_gate') === '')
  console.info(`[Remnants] Threshold respawn: ${p.username} fell=${fell}`)
  if (!fell) return
  p.persistentData.putBoolean('remnants_threshold_fell_new', false)
  if (p.persistentData.getString('remnants_threshold_gate') === '') p.persistentData.putString('remnants_threshold_gate', 'fell')
  cmd(server, `title ${p.username} actionbar ${json({ text: 'Your remains were carried back to the crypt.', color: 'gray', italic: true })}`)
  server.scheduleInTicks(40, function () {
    var pl = playerNamed(server, p.username)
    if (!pl) return
    titleCard(server, pl.username, { text: '' }, { text: 'The Ember Door stirs.', color: 'gold', italic: true }, 20, 50, 20)
    narrate(server, pl, 'threshold_fell', true)
  })
})

// ---------------------------------------------------------------- fog and doors (particles), and the clock

function ambience(server) {
  var g = T.gate, d = T.exit_door, e = T.ember_door
  var near = false
  server.players.forEach(function (p) { if (inThreshold(p)) near = true })
  if (!near) return
  var count = fight ? 50 : 25
  cmd(server, inDim(`particle minecraft:white_ash ${g.x + 0.5} ${g.y1 + 2} 0.5 0.1 1.6 2.2 0 ${count * 3} force`))
  cmd(server, inDim(`particle minecraft:cloud ${g.x + 0.5} ${g.y1 + 2} 0.5 0.05 1.4 2 0.005 ${count} force`))
  cmd(server, inDim(`particle minecraft:soul_fire_flame ${d.x + 0.5} ${d.y1 + 1.5} 0.5 0.05 1.2 1.5 0.01 12 force`))
  cmd(server, inDim(`particle minecraft:soul_fire_flame ${(e.x1 + e.x2) / 2 + 0.5} ${e.y1 + 1} ${e.z + 0.5} 1 1 0.05 0.01 8 force`))
  cmd(server, inDim(`particle minecraft:end_rod ${T.waygate.x - 1.5} ${T.arena.boss[1] + 8} 0.5 0.1 2 1.5 0.01 6 force`))
}

ServerEvents.tick(function (event) {
  if (++counter % 10 !== 0) return
  var server = event.server
  server.players.forEach(function (p) { playerTick(server, p) })
  fightTick(server)
  if (counter % 20 === 0) ambience(server)
})

// ---------------------------------------------------------------- /threshold (ops)

ServerEvents.commandRegistry(function (event) {
  var Commands = event.commands
  var Arguments = event.arguments
  event.register(Commands.literal('threshold')
    .requires(function (s) { return s.hasPermission(2) })
    .then(Commands.literal('off').executes(function (c) {
      c.source.server.persistentData.putBoolean('remnants_threshold_off', true)
      c.source.sendSystemMessage(Text.of('New players will skip the Threshold.'))
      return 1
    }))
    .then(Commands.literal('on').executes(function (c) {
      c.source.server.persistentData.putBoolean('remnants_threshold_off', false)
      c.source.sendSystemMessage(Text.of('New players will wake in the Threshold.'))
      return 1
    }))
    .then(Commands.literal('rebuild').executes(function (c) {
      c.source.server.persistentData.putInt('remnants_threshold_built', 0)
      ensureBuilt(c.source.server)
      c.source.sendSystemMessage(Text.of('Rebuilding the Threshold.'))
      return 1
    }))
    .then(Commands.literal('skip').then(Commands.argument('player', Arguments.PLAYER.create(event)).executes(function (c) {
      var p = Arguments.PLAYER.getResult(c, 'player')
      skip(c.source.server, p)
      return 1
    })))
    .then(Commands.literal('send').then(Commands.argument('player', Arguments.PLAYER.create(event)).executes(function (c) {
      var p = Arguments.PLAYER.getResult(c, 'player')
      p.persistentData.putString('remnants_threshold_gate', '')
      wake(c.source.server, p)
      return 1
    }))))
})
})()
