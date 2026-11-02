// What you lost and how to get it back, told right after you respawn (players asked; nothing in game said it).
//
// Two things wait where you fell: your items, in your corpse (the Corpse mod: right-click it; it turns to bones but stays until emptied), and
// your runes, in the bloodstain Runeborn leaves (walk within ~2 blocks of it; its glow shows within 96 blocks and the
// minimap marks it). The pack's Echo of the Fallen (echo.js) stands on the bloodstain: kill it, then step in.
// Die again before you get there and those runes are gone (Runeborn's rule); the corpse stays.
//
// The first three deaths get the whole explanation; after that, one line with the place. The Threshold and the
// Fractured Archive have their own death rules and messages, so they are skipped.

(function () {
  var SKIP = ['remnants:threshold', 'tbos:fractured_archive']
  var FULL_GUIDES = 3
  var DIM_NAMES = {
    'minecraft:overworld': 'the Lands Under Ash', 'minecraft:the_nether': 'the Nether', 'minecraft:the_end': 'the End',
    'remnant_bosses:eclipsed_realm': 'the Eclipsed Realm', 'deeperdarker:otherside': 'the Otherside'
  }

  function say(server, name, parts) {
    server.runCommandSilent(`tellraw ${name} ${JSON.stringify(parts)}`)
  }

  EntityEvents.death('minecraft:player', function (event) {
    var p = event.entity
    var dim = String(p.level.dimension)
    if (SKIP.indexOf(dim) >= 0) return
    var d = p.persistentData
    d.putBoolean('remnants_guide_pending', true)
    d.putString('remnants_guide_dim', dim)
    d.putInt('remnants_guide_x', Math.floor(p.x))
    d.putInt('remnants_guide_y', Math.floor(p.y))
    d.putInt('remnants_guide_z', Math.floor(p.z))
    d.putInt('remnants_guide_deaths', d.getInt('remnants_guide_deaths') + 1)
  })

  PlayerEvents.respawned(function (event) {
    var p = event.player
    var d = p.persistentData
    if (!d.getBoolean('remnants_guide_pending')) return
    d.putBoolean('remnants_guide_pending', false)
    var server = event.server
    var name = p.username
    var dim = d.getString('remnants_guide_dim')
    var where = `${d.getInt('remnants_guide_x')} ${d.getInt('remnants_guide_y')} ${d.getInt('remnants_guide_z')}`
    var place = DIM_NAMES[dim] || dim
    var full = d.getInt('remnants_guide_deaths') <= FULL_GUIDES
    // Delay a moment so it lands after the death screen closes and Runeborn's own banner fades.
    server.scheduleInTicks(40, function () {
      say(server, name, [{ text: '✦ ', color: 'dark_red' }, { text: 'You fell at ', color: 'gray' },
        { text: where, color: 'white', bold: true }, { text: ` in ${place}.`, color: 'gray' }])
      if (full) {
        say(server, name, [{ text: '  Your items ', color: 'gold' },
          { text: 'wait in your corpse there. Right-click it to take them back; it stays until you empty it. ', color: 'gray' },
          { text: 'Ctrl+U', color: 'white' }, { text: ' lists your last deaths and what you carried.', color: 'gray' }])
        say(server, name, [{ text: '  Your runes ', color: 'gold' },
          { text: 'lie in the ', color: 'gray' }, { text: 'bloodstain', color: 'dark_red' },
          { text: ' beside it (red on your minimap; it glows within 96 blocks). ', color: 'gray' },
          { text: 'Your Echo', color: 'dark_red' },
          { text: ' guards it: kill it, then step into the bloodstain to take them back.', color: 'gray' }])
        say(server, name, [{ text: '  Die again before you reach it and those runes are gone. The corpse stays.',
          color: 'dark_gray', italic: true }])
      } else {
        say(server, name, [{ text: '  Corpse: your items. Bloodstain: your runes (kill your Echo, then step in). ',
          color: 'gray' }, { text: 'Ctrl+U', color: 'white' }, { text: ' for your deaths.', color: 'gray' }])
      }
    })
  })
})()
