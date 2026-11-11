// The world starts quiet and fills up as the story is told (beta 13).
//
// Before this, the night was as crowded for an Ashborn on their first evening as for one who had felled four
// Sovereigns: Minecraft keeps about 70 monsters around every player whatever the pack adds, and Born in Chaos alone
// adds 45 kinds to that pool, flies and armoured knights included. Three rules now apply to NATURAL spawns only
// (spawners, structures, bosses' minions, raids, eggs and commands are never touched):
//
// 1. A local cap. No new monster rises while PACE_CAPS[stage] monsters already stand within PACE_RANGE blocks of
//    the nearest player (PACE_HEIGHT up and down). The stage is that player's own story: a shrine kindled, then one
//    step per Sovereign felled. From four Sovereigns on there is no cap. In a party the furthest player counts.
// 2. The heavy hitters wait their turn: PACE_TIERS lists monsters that only rise for players of a given stage.
// 3. Flies (corpse flies, gadflies, swarmers) rise one time in PACE_FLY_ODDS, and never more than PACE_FLY_CAP near
//    a player: they used to be a constant cloud.
//
// Monster levels and ranks are RPG Mobs' business (config/remnant_mobs/); this file only decides how many.

var PACE_RANGE = 72
var PACE_HEIGHT = 40
var PACE_CAPS = [7, 10, 13, 16, 20]             // stage 0..4; a stage past the end of the list is uncapped
var PACE_RECOUNT_TICKS = 40
var PACE_STAGE_TICKS = 600
var PACE_FLY_ODDS = 6
var PACE_FLY_CAP = 2

var PACE_STAGES = ['runeborn:feats/kindle', 'runeborn:feats/fell_dusk_rider', 'runeborn:feats/fell_varghast',
  'runeborn:feats/fell_sylvara', 'runeborn:feats/fell_kaelthar', 'runeborn:feats/fell_ysolde',
  'runeborn:feats/fell_morgrath', 'runeborn:feats/fell_vaelorn']

var PACE_FLIES = { 'born_in_chaos_v1:corpse_fly': true, 'born_in_chaos_v1:bloody_gadfly': true, 'born_in_chaos_v1:swarmer': true }

// Minimum stage for a monster to rise by itself. 1 = an Ember Shrine kindled, 2 = the Dusk Rider felled.
var PACE_TIERS = {
  'born_in_chaos_v1:zombie_bruiser': 1, 'born_in_chaos_v1:siamese_skeletons': 1, 'born_in_chaos_v1:mother_spider': 1,
  'born_in_chaos_v1:dread_hound': 1, 'born_in_chaos_v1:skeleton_demoman': 1, 'born_in_chaos_v1:bonescaller': 1,
  'born_in_chaos_v1:zombie_clown': 1, 'born_in_chaos_v1:door_knight': 1, 'born_in_chaos_v1:phantom_creeper': 1,
  'born_in_chaos_v1:dark_vortex': 1, 'born_in_chaos_v1:pumpkin_bruiser': 1,
  'born_in_chaos_v1:fallen_chaos_knight': 2, 'born_in_chaos_v1:nightmare_stalker': 2, 'born_in_chaos_v1:lifestealer': 2,
  'born_in_chaos_v1:missioner': 2, 'born_in_chaos_v1:dire_hound_leader': 2, 'born_in_chaos_v1:skeleton_thrasher': 2,
  'born_in_chaos_v1:supreme_bonescaller': 2, 'born_in_chaos_v1:sir_pumpkinhead': 2, 'born_in_chaos_v1:krampus': 2,
  'born_in_chaos_v1:spiritof_chaos': 2,
  'mutantmonsters:mutant_zombie': 2, 'mutantmonsters:mutant_skeleton': 2, 'mutantmonsters:mutant_creeper': 2,
  'mutantmonsters:mutant_enderman': 3
}

var paceStages = {}      // player uuid -> { at: tick, stage: n }
var paceCounts = {}      // player uuid -> { at: tick, monsters: n, flies: n }

function paceStage(player, tick) {
  var key = String(player.uuid)
  var cached = paceStages[key]
  if (cached && tick - cached.at < PACE_STAGE_TICKS) return cached.stage
  var stage = 0
  for (var i = 0; i < PACE_STAGES.length; i++) {
    if (player.isAdvancementDone(PACE_STAGES[i])) stage++
  }
  paceStages[key] = { at: tick, stage: stage }
  return stage
}

// Monsters and flies around a player, recounted every two seconds and kept up to date in between.
function paceCount(player, level, tick) {
  var key = String(player.uuid)
  var cached = paceCounts[key]
  if (cached && tick - cached.at < PACE_RECOUNT_TICKS) return cached
  var monsters = 0
  var flies = 0
  var box = AABB.of(player.x - PACE_RANGE, player.y - PACE_HEIGHT, player.z - PACE_RANGE,
    player.x + PACE_RANGE, player.y + PACE_HEIGHT, player.z + PACE_RANGE)
  level.getEntitiesWithin(box).forEach(function (e) {
    if (!e.isLiving() || !e.isMonster()) return
    monsters++
    if (PACE_FLIES[String(e.type)]) flies++
  })
  cached = { at: tick, monsters: monsters, flies: flies }
  paceCounts[key] = cached
  return cached
}

// True when this spawn should not happen.
function paceDenies(event) {
  if (String(event.type) !== 'NATURAL') return false
  var entity = event.entity
  if (!entity.isMonster()) return false
  var level = event.level
  var id = String(entity.type)
  var tick = level.server.tickCount
  var stage = 0
  var crowd = null
  var players = level.players
  for (var i = 0; i < players.size(); i++) {
    var p = players.get(i)
    if (p.isSpectator()) continue
    if (Math.abs(p.x - event.x) > PACE_RANGE || Math.abs(p.z - event.z) > PACE_RANGE || Math.abs(p.y - event.y) > PACE_HEIGHT) continue
    var s = paceStage(p, tick)
    if (!crowd || s >= stage) {
      stage = s
      crowd = paceCount(p, level, tick)
    }
  }
  // Nobody close enough to see it rise: Minecraft's own cap is the only limit, as before.
  if (!crowd) return false
  if ((PACE_TIERS[id] || 0) > stage) return true
  if (PACE_FLIES[id]) {
    if (crowd.flies >= PACE_FLY_CAP || Math.random() * PACE_FLY_ODDS >= 1) return true
  }
  if (stage < PACE_CAPS.length && crowd.monsters >= PACE_CAPS[stage]) return true
  if (PACE_FLIES[id]) crowd.flies++
  crowd.monsters++
  return false
}

// event.cancel() leaves the handler by throwing, so it must stay outside the try: an error in the rule above lets
// the spawn through and is logged, it never breaks spawning.
EntityEvents.checkSpawn(function (event) {
  var deny = false
  try {
    deny = paceDenies(event)
  } catch (e) {
    console.error('[Remnants] pacing: ' + e)
  }
  if (deny) event.cancel()
})
