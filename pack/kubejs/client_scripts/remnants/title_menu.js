// The title screen's small icon buttons (language, accessibility, any mod's 20x20 shortcut) in one row under the
// pack's button column. FancyMenu 3.9.14 can't name the 1.21.1 language and accessibility buttons (it looks for the
// 1.20 keys), so its layout can't move them; this keeps them with the menu at any window size.
// Must match tools/build_menu.py: column at x=108, 200 wide, first row at height/2 - 46, rows 24 apart.
// Wrapped in try/catch: an error thrown from a screen event crashes the client.
var COL_X = 108, COL_W = 200, ICON_ROW = -46 + 96
var TitleScreen = Java.loadClass('net.minecraft.client.gui.screens.TitleScreen')
var logged = false

NativeEvents.onEvent(Java.loadClass('net.neoforged.neoforge.client.event.ScreenEvent$Init$Post'), function (event) {
  try {
    if (event.getScreen() instanceof TitleScreen) lineUpIcons(event)
  } catch (e) {
    console.error('[Remnants] title-screen icons: ' + e)
  }
})

function lineUpIcons(event) {
  var screen = event.getScreen()
  var icons = []
  event.getListenersList().forEach(function (w) {
    if (w.getWidth && w.getWidth() == 20 && w.getHeight() == 20) icons.push(w)
  })
  icons.sort(function (a, b) { return a.getX() - b.getX() || a.getY() - b.getY() })
  var total = icons.length * 20 + Math.max(0, icons.length - 1) * 4
  var x = COL_X + Math.floor((COL_W - total) / 2)
  var y = Math.floor(screen.height / 2) + ICON_ROW
  var names = []
  for (var i = 0; i < icons.length; i++) {
    icons[i].setPosition(x + i * 24, y)
    names.push(String(icons[i]).split('@')[0] + ' "' + icons[i].getMessage().getString() + '"')
  }
  if (!logged) {
    logged = true
    console.info('[Remnants] title-screen icons lined up: ' + names.join(', '))
  }
}
