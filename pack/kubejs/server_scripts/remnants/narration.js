// The Keeper's voice. Lines live in startup_scripts/remnants_narration_lines.js (generated from the quests by
// tools/build_quests.py; `global` can only be assigned in startup scripts); the
// recordings are kubejs/assets/remnants/sounds/vo/<line>.ogg (tools/build_voice.py), played on the "voice"
// sound slider so players can turn the Keeper down without losing music.
//
// A narrated quest plays its line when it completes, for every online member of the team that completed it.
// Story beats (Sovereign kills) also print the line in chat; the "♪ Listen" tales don't, because the player is
// reading the same words in the quest book.

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

Object.keys(global.REMNANTS_NARRATION).forEach(function (questId) {
  var n = global.REMNANTS_NARRATION[questId]
  FTBQuestsEvents.completed(questId, function (event) {
    event.getOnlineMembers().forEach(function (p) {
      remnantsNarrate(event.server, p, n.line, n.chat)
    })
  })
})
