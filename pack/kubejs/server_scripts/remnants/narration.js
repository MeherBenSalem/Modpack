// The Keeper's voice. Lines live in startup_scripts/remnants_narration_lines.js (generated from the quests by
// tools/build_quests.py; `global` can only be assigned in startup scripts); the
// recordings are kubejs/assets/remnants/sounds/vo/<line>.ogg (tools/build_voice.py), played on the "voice"
// sound slider so players can turn the Keeper down without losing music.
//
// A narrated quest plays its line when it completes, for every online member of the team that completed it.
// Core RPG - Quests Engine runs each narrated quest's completion command, `remnants_vo completed <team> <quest>`
// (written by tools/build_quests.py), and the command below plays the lines.
// Story beats (Sovereign kills) also print the line in chat; the "♪ Listen" tales don't, because the player is
// reading the same words in the quest book. Some quests also have an unlock line (global.REMNANTS_UNLOCKS): the
// Keeper speaks when the quest becomes available, i.e. when its last dependency completes.
//
// Lines queue per player: two quests finishing together play one after the other instead of cutting each other
// off (each line's length is in global.REMNANTS_DURATIONS, written by tools/build_voice.py).

var SPEAKER_NAMES = {
  keeper: { name: 'The Keeper', colour: 'gold', text: 'white' },
  whisper: { name: '???', colour: 'dark_purple', text: 'light_purple' }
}

// Play `line` to `player`. chat: also print it. Server scripts share one scope, so threshold.js calls this too.
function remnantsNarrate(server, player, line, chat) {
  var l = global.REMNANTS_LINES[line]
  if (!l) return
  var who = SPEAKER_NAMES[l.speaker] || SPEAKER_NAMES.keeper
  var name = player.username
  server.runCommandSilent(`stopsound ${name} voice`)
  server.runCommandSilent(`execute as ${name} at @s run playsound remnants:vo.${line} voice @s ~ ~ ~ 1 1 1`)
  if (chat) {
    l.text.forEach(function (para, i) {
      var parts = [{ text: i === 0 ? '' : '  ', color: who.colour }]
      if (i === 0) parts.push({ text: who.name + ': ', color: who.colour, bold: true })
      parts.push({ text: para, color: who.text, italic: true })
      server.runCommandSilent(`tellraw ${name} ${JSON.stringify(parts)}`)
    })
  } else {
    server.runCommandSilent(`title ${name} actionbar ${JSON.stringify({ text: '♪ ' + who.name + ' speaks', color: who.colour, italic: true })}`)
  }
}

var REMNANTS_VO_END = {}   // player name -> server tick when their queued lines finish

// Queue `line` for `player`: it starts as soon as the line before it has ended.
function remnantsSay(server, player, line, chat) {
  if (!global.REMNANTS_LINES[line]) return
  var name = player.username
  var now = server.getTickCount()
  var start = Math.max(now, REMNANTS_VO_END[name] || 0)
  var seconds = (global.REMNANTS_DURATIONS || {})[line] || 10
  REMNANTS_VO_END[name] = start + Math.ceil(seconds * 20) + 20
  if (start <= now) {
    remnantsNarrate(server, player, line, chat)
    return
  }
  server.scheduleInTicks(start - now, function () {
    var p = server.getPlayerList().getPlayerByName(name)
    if (p) remnantsNarrate(server, p, line, chat)
  })
}

var CoreQuests = Java.loadClass('dev.nightbeam.corerpg.quests.server.ServerQuests')
var JavaUUID = Java.loadClass('java.util.UUID')

// Online members of a Core RPG team, by the team's id ({team} in a completion command).
function remnantsTeamMembers(server, teamId) {
  var quests = CoreQuests.getOrNull()
  if (!quests) return { members: [], progress: null }
  var team = null
  try {
    team = quests.teams().get(JavaUUID.fromString(teamId))
  } catch (e) {
    team = null
  }
  if (!team) return { members: [], progress: null }
  var list = team.onlineMembers(server)
  var members = []
  for (var i = 0; i < list.size(); i++) members.push(list.get(i))
  return { members: members, progress: quests.progress(team) }
}

// A quest completed: its own line first, then any quest it was the last missing dependency for.
function remnantsQuestCompleted(server, teamId, questId) {
  var team = remnantsTeamMembers(server, teamId)
  if (!team.members.length) return 0
  var n = global.REMNANTS_NARRATION[questId]
  if (n) {
    team.members.forEach(function (p) {
      remnantsSay(server, p, n.line, n.chat)
    })
  }
  ;(global.REMNANTS_UNLOCKS[questId] || []).forEach(function (u) {
    var ready = u.deps.every(function (d) {
      return team.progress.isQuestCompleted(d)
    })
    if (!ready) return
    team.members.forEach(function (p) {
      remnantsSay(server, p, u.line, true)
    })
  })
  return 1
}

ServerEvents.commandRegistry(function (event) {
  var Commands = event.commands
  var Arguments = event.arguments
  event.register(Commands.literal('remnants_vo').requires(function (s) { return s.hasPermission(2) })
    .then(Commands.literal('completed')
      .then(Commands.argument('team', Arguments.WORD.create(event))
        .then(Commands.argument('quest', Arguments.GREEDY_STRING.create(event)).executes(function (ctx) {
          try {
            return remnantsQuestCompleted(ctx.source.server, String(Arguments.WORD.getResult(ctx, 'team')),
              String(Arguments.GREEDY_STRING.getResult(ctx, 'quest')).trim())
          } catch (e) {
            console.error('remnants_vo completed failed: ' + e)
            return 0
          }
        }))))
    .then(Commands.literal('play')
      .then(Commands.argument('player', Arguments.PLAYER.create(event))
        .then(Commands.argument('line', Arguments.WORD.create(event)).executes(function (ctx) {
          var line = String(Arguments.WORD.getResult(ctx, 'line'))
          if (!global.REMNANTS_LINES[line]) return 0
          remnantsSay(ctx.source.server, Arguments.PLAYER.getResult(ctx, 'player'), line, true)
          return 1
        })))))
})
