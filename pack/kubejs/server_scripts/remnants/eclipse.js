// The Long Eclipse: one world-wide bar for the eight Sovereigns. The first time each one falls on this world,
// an ember is rekindled for everyone: a title, a sound, and a permanent heart ("Emberblessed") for every player,
// including players who join later. Detected through advancements because Runeborn's Sovereigns are vanilla mobs.

const ECLIPSE_BAR = 'remnants:long_eclipse'
const ECLIPSE_KEY = 'remnants_s1_embers'
const ECLIPSE_SOVEREIGNS = {
  'runeborn:feats/fell_dusk_rider': 'The Dusk Rider',
  'runeborn:feats/fell_varghast': 'Varghast the Grafted',
  'runeborn:feats/fell_sylvara': 'Sylvara, Frost Matron',
  'runeborn:feats/fell_kaelthar': 'Kaelthar the Stormcaller',
  'runeborn:feats/fell_ysolde': 'Ysolde, the Crimson Bloom',
  'runeborn:feats/fell_morgrath': 'Morgrath, Ash Sovereign',
  'runeborn:feats/fell_vaelorn': 'Vaelorn, the Wyrm-Ravager',
  'remnant_bosses:realm/remnant_felled': 'The Hollow Sovereign'
}
const ECLIPSE_TOTAL = Object.keys(ECLIPSE_SOVEREIGNS).length

function eclipseLit(server) {
  const raw = server.persistentData.getString(ECLIPSE_KEY)
  return raw ? raw.split(',') : []
}

function eclipseTitle(n) {
  if (n >= ECLIPSE_TOTAL) return '{"text":"First Light","color":"gold","bold":true}'
  return `{"text":"The Long Eclipse: ${n} / ${ECLIPSE_TOTAL} embers rekindled","color":"gold"}`
}

function eclipseRefreshBar(server) {
  const n = eclipseLit(server).length
  server.runCommandSilent(`bossbar add ${ECLIPSE_BAR} ""`)
  server.runCommandSilent(`bossbar set ${ECLIPSE_BAR} max ${ECLIPSE_TOTAL}`)
  server.runCommandSilent(`bossbar set ${ECLIPSE_BAR} value ${n}`)
  server.runCommandSilent(`bossbar set ${ECLIPSE_BAR} color ${n >= ECLIPSE_TOTAL ? 'yellow' : 'purple'}`)
  server.runCommandSilent(`bossbar set ${ECLIPSE_BAR} style notched_10`)
  server.runCommandSilent(`bossbar set ${ECLIPSE_BAR} name ${eclipseTitle(n)}`)
}

// Show the bar to a player (or @a) for a while, then hide it again so it doesn't sit on top of boss fights.
function eclipseShowBar(server, who, seconds) {
  eclipseRefreshBar(server)
  server.runCommandSilent(`bossbar set ${ECLIPSE_BAR} players ${who}`)
  server.scheduleInTicks(seconds * 20, () => server.runCommandSilent(`bossbar set ${ECLIPSE_BAR} players`))
}

// One +2 max-health modifier per rekindled ember. Adding an existing modifier fails quietly, so this is idempotent.
function eclipseBless(server, playerName, count) {
  for (let i = 1; i <= count; i++) {
    server.runCommandSilent(
      `attribute ${playerName} minecraft:generic.max_health modifier add remnants:emberblessed_${i} 2 add_value`)
  }
}

ServerEvents.loaded(event => eclipseRefreshBar(event.server))

PlayerEvents.loggedIn(event => {
  const server = event.server
  const name = event.player.username
  const n = eclipseLit(server).length
  eclipseBless(server, name, n)
  server.scheduleInTicks(100, () => eclipseShowBar(server, name, 12))
})

PlayerEvents.advancement(event => {
  const id = String(event.advancement.id)
  const sovereign = ECLIPSE_SOVEREIGNS[id]
  if (!sovereign) return
  const server = event.server
  const lit = eclipseLit(server)
  if (lit.includes(id)) return
  lit.push(id)
  server.persistentData.putString(ECLIPSE_KEY, lit.join(','))
  const n = lit.length
  const done = n >= ECLIPSE_TOTAL
  server.runCommandSilent('title @a times 20 80 30')
  server.runCommandSilent(done
    ? 'title @a title {"text":"FIRST LIGHT","color":"gold","bold":true}'
    : 'title @a title {"text":"An Ember Returns","color":"gold"}')
  server.runCommandSilent(`title @a subtitle {"text":"${sovereign} has fallen. ${n} / ${ECLIPSE_TOTAL}","color":"gray"}`)
  server.runCommandSilent('execute as @a at @s run playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 1 0.6')
  server.runCommandSilent(`tellraw @a [{"text":"✦ ","color":"gold"},{"text":"${event.player.username}","color":"yellow"},` +
    `{"text":" rekindled an ember. Every Ashborn on this world is ","color":"gray"},{"text":"Emberblessed","color":"gold"},` +
    `{"text":": +1 heart, for good.","color":"gray"}]`)
  server.players.forEach(p => eclipseBless(server, p.username, n))
  eclipseShowBar(server, '@a', 20)
  if (done) {
    server.scheduleInTicks(160, () => {
      server.runCommandSilent('tellraw @a {"text":"\\"Rest, Ashborn. The sun remembers you.\\"","color":"gold","italic":true}')
    })
    server.scheduleInTicks(400, () => {
      server.runCommandSilent('tellraw @a {"text":"Seven crowns, one hollow. But who broke the sun?","color":"dark_purple","italic":true}')
    })
  }
})
