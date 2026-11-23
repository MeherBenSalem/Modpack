// Swap the broken Ashen Codex for the working one when a player logs in.
//
// Up to 1.0.0-beta.14 the first quest gave patchouli:guide_book for the book remnants:ashen_codex, whose book.json sat
// in kubejs/data where Patchouli never looks, so the book read "Invalid book". The book now lives in the game
// directory's patchouli_books/ folder (see tools/build_data.py), where Patchouli names it patchouli:ashen_codex.
// Players who already claimed the old reward still carry the dead book; this gives them the new one in its place.
// Only the player's own inventory is checked (not chests or ender chests).

(function () {
  var OLD = 'patchouli:guide_book[patchouli:book="remnants:ashen_codex"]'
  var NEW = 'patchouli:guide_book[patchouli:book="patchouli:ashen_codex"]'
  var TAG = 'remnants_old_codex'

  PlayerEvents.loggedIn(function (event) {
    var server = event.server
    var who = `execute as ${event.player.username}`
    server.runCommandSilent(`${who} if items entity @s container.* ${OLD} run tag @s add ${TAG}`)
    server.runCommandSilent(`${who} if items entity @s weapon.offhand ${OLD} run tag @s add ${TAG}`)
    // Give first, then clear, so a failed give never leaves the player with no book.
    server.runCommandSilent(`${who} if entity @s[tag=${TAG}] run give @s ${NEW}`)
    server.runCommandSilent(`${who} if entity @s[tag=${TAG}] run clear @s ${OLD}`)
    server.runCommandSilent(`tag ${event.player.username} remove ${TAG}`)
  })
})()
