// Last Light: the village around your first Ember Shrine gains faces as the story moves. Quest rewards call
// `/lastlight arrive <npc> {p}`; each NPC arrives once per world, next to the player who earned them.
// They are named, invulnerable villagers with fixed trades (no extra mod needed, and they keep working if
// Easy NPC is removed).
//
//   /lastlight eclipse                 show the Long Eclipse bar (anyone)
//   /lastlight arrive <npc> <player>   bring an NPC to a player (ops; used by quests)
//   /lastlight spawnat <npc> <pos>     place an NPC anywhere (ops; for map makers and tests)
//   /lastlight echoes <on|off>         toggle Echoes of the Fallen for this world (ops)

function lastLightTrade(buy, sell, buyB) {
  const stack = s => `{id:"${s[0]}",count:${s[1]}}`
  return `{buy:${stack(buy)},${buyB ? `buyB:${stack(buyB)},` : ''}sell:${stack(sell)},` +
    'maxUses:2147483647,rewardExp:0b,xp:0,priceMultiplier:0.0f}'
}

const LAST_LIGHT_NPCS = {
  keeper: {
    name: 'The Keeper of Last Light', color: 'gold', profession: 'cleric',
    line: '"I kept the flame. Now keep me company."',
    trades: [
      [['minecraft:gold_ingot', 4], ['minecraft:blaze_powder', 1]],
      [['minecraft:emerald', 6], ['runeborn:faded_rune', 1]],
      [['remnant_mobs:remnant_shard', 12], ['runeborn:sunseed', 1], ['minecraft:gold_block', 2]]
    ]
  },
  captain: {
    name: 'Maren, Captain of the Ashen Company', color: 'yellow', profession: 'weaponsmith',
    line: '"Gold up front. Graves are extra."',
    trades: [
      [['minecraft:gold_ingot', 6], ['better_with_gold:golden_fish', 1]],
      [['minecraft:gold_ingot', 20], ['better_with_gold:warbanner', 1]]
    ]
  },
  smith: {
    name: 'The Smith Under Ash', color: 'gray', profession: 'toolsmith',
    line: '"Bring me what the dead leave behind. I\'ll make it sing."',
    trades: [
      [['minecraft:iron_ingot', 4], ['runeborn:tempering_stone_2', 2], ['minecraft:emerald', 1]],
      [['minecraft:diamond', 2], ['runeborn:tempering_stone_4', 1]],
      [['remnant_mobs:remnant_shard', 8], ['runeborn:blank_whetstone', 1]]
    ]
  },
  huntmaster: {
    name: 'Ilse, the Huntmaster', color: 'red', profession: 'butcher',
    line: '"Every rank has a weakness. Every Remnant has a name. Learn both."',
    trades: [
      [['remnant_mobs:remnant_shard', 6], ['remnant_mobs:hunters_lens', 1]],
      [['remnant_mobs:remnant_shard', 12], ['remnant_mobs:brand_of_challenge', 1]],
      [['remnant_mobs:remnant_shard', 16], ['runeborn:radiant_rune', 1]]
    ]
  },
  archivist: {
    name: 'Oren, the Archivist', color: 'aqua', profession: 'librarian',
    line: '"Every ruin has a before. I collect befores."',
    trades: [
      [['minecraft:emerald', 8], ['explorerscompass:explorerscompass', 1]],
      [['minecraft:emerald', 6], ['naturescompass:naturescompass', 1]],
      [['minecraft:amethyst_shard', 4], ['tbos:memory_key', 1], ['minecraft:ender_pearl', 1]]
    ]
  }
}

function lastLightSummon(server, key, dim, x, y, z) {
  const npc = LAST_LIGHT_NPCS[key]
  const name = JSON.stringify(JSON.stringify({ text: npc.name, color: npc.color, italic: false }))
  const offers = npc.trades.map(t => lastLightTrade(t[0], t[1], t[2])).join(',')
  server.runCommandSilent(`execute in ${dim} run summon minecraft:villager ${x} ${y} ${z} {CustomName:${name},` +
    'CustomNameVisible:1b,NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,' +
    `Tags:["lastlight_npc","lastlight_${key}"],` +
    `VillagerData:{profession:"minecraft:${npc.profession}",level:5,type:"minecraft:plains"},` +
    `Offers:{Recipes:[${offers}]}}`)
}

function lastLightArrive(server, key, player) {
  const npc = LAST_LIGHT_NPCS[key]
  if (!npc) return 0
  const flag = `lastlight_arrived_${key}`
  if (server.persistentData.getBoolean(flag)) {
    player.tell(Text.gray(`${npc.name} is already at Last Light.`))
    return 1
  }
  server.persistentData.putBoolean(flag, true)
  const a = player.yRot * Math.PI / 180
  const x = (player.x - Math.sin(a) * 2).toFixed(2)
  const z = (player.z + Math.cos(a) * 2).toFixed(2)
  lastLightSummon(server, key, String(player.level.dimension), x, player.y.toFixed(2), z)
  server.runCommandSilent(`tellraw @a [{"text":"${npc.name}","color":"${npc.color}"},` +
    `{"text":" has come to Last Light. ","color":"gray"},{"text":${JSON.stringify(npc.line)},"color":"gray","italic":true}]`)
  return 1
}

ServerEvents.commandRegistry(event => {
  const { commands: Commands, arguments: Arguments } = event
  const npcArg = () => Commands.argument('npc', Arguments.WORD.create(event))
    .suggests((ctx, builder) => {
      Object.keys(LAST_LIGHT_NPCS).forEach(k => builder.suggest(k))
      return builder.buildFuture()
    })

  event.register(Commands.literal('lastlight')
    .then(Commands.literal('eclipse').executes(ctx => {
      try {
        const player = ctx.source.player
        eclipseShowBar(ctx.source.server, player ? player.username : '@a', 15)
        return 1
      } catch (e) {
        console.error(`lastlight eclipse failed: ${e}`)
        return 0
      }
    }))
    .then(Commands.literal('arrive').requires(s => s.hasPermission(2))
      .then(npcArg().then(Commands.argument('player', Arguments.PLAYER.create(event)).executes(ctx =>
        lastLightArrive(ctx.source.server, Arguments.WORD.getResult(ctx, 'npc'), Arguments.PLAYER.getResult(ctx, 'player'))))))
    .then(Commands.literal('spawnat').requires(s => s.hasPermission(2))
      .then(npcArg().then(Commands.argument('pos', Arguments.BLOCK_POS.create(event)).executes(ctx => {
        const key = Arguments.WORD.getResult(ctx, 'npc')
        if (!LAST_LIGHT_NPCS[key]) return 0
        const pos = Arguments.BLOCK_POS.getResult(ctx, 'pos')
        lastLightSummon(ctx.source.server, key, String(ctx.source.level.dimension), pos.x + 0.5, pos.y, pos.z + 0.5)
        return 1
      }))))
    .then(Commands.literal('testecho').requires(s => s.hasPermission(2))
      .then(Commands.argument('pos', Arguments.BLOCK_POS.create(event)).executes(ctx => {
        try {
          const pos = Arguments.BLOCK_POS.getResult(ctx, 'pos')
          const echo = echoRaise(ctx.source.server, ctx.source.level, pos.x + 0.5, pos.y, pos.z + 0.5, 'Test',
            `${ECHO_TAG}_test`, null)
          return echo ? 1 : 0
        } catch (e) {
          console.error(`lastlight testecho failed: ${e}`)
          return 0
        }
      })))
    .then(Commands.literal('echoes').requires(s => s.hasPermission(2))
      .then(Commands.literal('on').executes(ctx => {
        ctx.source.server.persistentData.putBoolean('remnants_echoes_off', false)
        return 1
      }))
      .then(Commands.literal('off').executes(ctx => {
        ctx.source.server.persistentData.putBoolean('remnants_echoes_off', true)
        return 1
      }))))
})
