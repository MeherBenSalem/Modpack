// The Keeper's voice. Lines live in startup_scripts/remnants_narration_lines.js (generated from the quests by
// tools/build_quests.py; `global` can only be assigned in startup scripts); the
// recordings are kubejs/assets/remnants/sounds/vo/<line>.ogg (tools/build_voice.py), played on the "voice"
// sound slider so players can turn the Keeper down without losing music.
//
// A narrated quest plays its line when it completes, for every online member of the team that completed it.
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

Object.keys(global.REMNANTS_NARRATION).forEach(function (questId) {
  var n = global.REMNANTS_NARRATION[questId]
  FTBQuestsEvents.completed(questId, function (event) {
    event.getOnlineMembers().forEach(function (p) {
      remnantsSay(event.server, p, n.line, n.chat)
    })
  })
})

// Quests by their hex id, read once from the quest file (ids are 64-bit, too wide for a JS number).
var REMNANTS_QUESTS = null
function remnantsQuest(file, code) {
  if (!REMNANTS_QUESTS) {
    REMNANTS_QUESTS = {}
    var chapters = file.getAllChapters()
    for (var i = 0; i < chapters.size(); i++) {
      var quests = chapters.get(i).getQuests()
      for (var j = 0; j < quests.size(); j++) REMNANTS_QUESTS[String(quests.get(j).getCodeString())] = quests.get(j)
    }
  }
  return REMNANTS_QUESTS[code]
}

// Unlock lines run after the dependency's own line (handlers fire in the order they were registered).
Object.keys(global.REMNANTS_UNLOCKS).forEach(function (depId) {
  FTBQuestsEvents.completed(depId, function (event) {
    var data = event.getData()
    global.REMNANTS_UNLOCKS[depId].forEach(function (u) {
      var ready = u.deps.every(function (d) {
        var q = remnantsQuest(data.getFile(), d)
        return q != null && data.isCompleted(q)
      })
      if (!ready) return
      event.getOnlineMembers().forEach(function (p) {
        remnantsSay(event.server, p, u.line, true)
      })
    })
  })
})
