// Area names: when an Ashborn walks into a new kind of land, its name fades in, the way the old maps named it.
// Biomes are matched by id keywords (vanilla, Terralith and the rest share the vocabulary), first match wins.
// A name shows after the player has been in it for a few seconds (no flicker on borders), and not again for
// REGION_REPEAT_TICKS unless they've been somewhere else in between.

(function () {
var REGION_CHECK = 40              // ticks between checks
var REGION_SETTLE = 2              // checks in the new region before its name shows
var REGION_REPEAT_TICKS = 6000     // the same name won't show again for 5 minutes

// [dimension or '*', keywords, name]
var REGIONS = [
  ['minecraft:the_nether', ['soul_sand'], 'The Valley of Ash-Souls'],
  ['minecraft:the_nether', ['crimson'], 'The Crimson Pyre'],
  ['minecraft:the_nether', ['warped'], 'The Cold Fire'],
  ['minecraft:the_nether', ['basalt', 'delta'], 'The Cinder Deltas'],
  ['minecraft:the_nether', [''], 'The Ashlands'],
  ['minecraft:the_end', ['the_end'], 'The Last Shore'],
  ['minecraft:the_end', [''], 'The Starless Reach'],
  ['deeperdarker:otherside', [''], 'The Otherside'],
  ['*', ['deep_dark'], 'The Deep'],
  ['*', ['lush_cave', 'underground_jungle'], 'The Underbloom'],
  ['*', ['dripstone', 'cave'], 'The Fanged Dark'],
  ['*', ['mushroom'], 'The Rotting Isles'],
  ['*', ['deep_ocean', 'deep_frozen', 'deep_cold', 'deep_lukewarm'], 'The Drowned Sky'],
  ['*', ['frozen_ocean', 'cold_ocean'], 'The Grey Waters'],
  ['*', ['ocean'], 'The Drowned Coast'],
  ['*', ['beach', 'shore', 'coast'], 'The Last Coast'],
  ['*', ['river'], 'The Grey River'],
  ['*', ['swamp', 'mangrove', 'bayou', 'marsh'], 'The Weeping Mire'],
  ['*', ['dark_forest'], 'The Hollow Wood'],
  ['*', ['cherry', 'blossom'], 'The Blossom Ruin'],
  ['*', ['jungle', 'rainforest'], 'The Drowned Green'],
  ['*', ['badlands', 'mesa', 'canyon'], 'The Scarred Reach'],
  ['*', ['desert', 'dune'], 'The Sunless Sands'],
  ['*', ['savanna', 'steppe', 'shrubland'], 'The Dusk Steppe'],
  ['*', ['peak', 'summit', 'slope', 'mountain', 'alpine', 'highland', 'cliff'], 'The Broken Crowns'],
  ['*', ['snow', 'frozen', 'ice', 'glacier', 'tundra', 'frost'], 'The Rime Veil'],
  ['*', ['taiga', 'pine', 'spruce', 'boreal'], 'The Pinewatch'],
  ['*', ['birch'], 'The White Wood'],
  ['*', ['forest', 'wood', 'grove', 'orchard'], 'The Grey Wood'],
  ['*', ['meadow', 'plains', 'field', 'prairie', 'valley', 'hills'], 'The Ashen Fields'],
]
var SKIP_DIMENSIONS = ['remnants:threshold', 'remnant_bosses:eclipsed_realm', 'tbos:fractured_archive']

function regionFor(dim, biome) {
  for (var i = 0; i < REGIONS.length; i++) {
    var r = REGIONS[i]
    if (r[0] !== '*' && r[0] !== dim) continue
    for (var k = 0; k < r[1].length; k++) {
      if (biome.indexOf(r[1][k]) >= 0) return r[2]
    }
  }
  return null
}

var ticks = 0
ServerEvents.tick(function (event) {
  if (++ticks % REGION_CHECK !== 0) return
  var server = event.server
  server.players.forEach(function (p) {
    try {
      var dim = String(p.level.dimension)
      if (SKIP_DIMENSIONS.indexOf(dim) >= 0) return
      var st = p.persistentData.getString('remnants_threshold')
      if (st === 'pending' || st === 'hub' || st === 'leaving') return
      var biome = String(p.level.getBiome(p.blockPosition()).getRegisteredName())
      var name = regionFor(dim, biome)
      if (!name) return
      var data = p.persistentData
      if (data.getString('remnants_region_seen') !== name) {
        // a candidate: it must hold for REGION_SETTLE checks
        if (data.getString('remnants_region_next') === name) {
          data.putInt('remnants_region_hold', data.getInt('remnants_region_hold') + 1)
        } else {
          data.putString('remnants_region_next', name)
          data.putInt('remnants_region_hold', 1)
        }
        if (data.getInt('remnants_region_hold') < REGION_SETTLE) return
        var key = 'remnants_region_at_' + name.replace(/[^A-Za-z]/g, '')
        var last = data.getLong(key)
        var now = server.overworld().getGameTime()
        data.putString('remnants_region_seen', name)
        if (last > 0 && now - last < REGION_REPEAT_TICKS) return
        data.putLong(key, now)
        var n = p.username
        server.runCommandSilent(`title ${n} times 25 55 30`)
        server.runCommandSilent(`title ${n} subtitle ${JSON.stringify({ text: name, color: '#E8D5A3' })}`)
        server.runCommandSilent(`title ${n} title ${JSON.stringify({ text: '' })}`)
        server.runCommandSilent(`execute as ${n} at @s run playsound minecraft:block.amethyst_block.resonate ambient @s ~ ~ ~ 0.6 0.7`)
      }
    } catch (e) {
      // a biome without a registered name, or a player mid-teleport: try again next check
    }
  })
})
})()
