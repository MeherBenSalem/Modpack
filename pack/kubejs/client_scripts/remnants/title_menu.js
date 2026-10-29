// The title screen's small icon buttons (language, accessibility, and mods' 20x20 shortcuts such as Create's and
// Supplementaries') in one row in the bottom-left corner, where the hidden version lines used to be. FancyMenu 3.9.14
// can't name the 1.21.1 language and accessibility buttons (it looks for the 1.20 keys), so its layout can't move
// them; this keeps them tidy at any window size. The menu itself is tools/build_menu.py.
// Wrapped in try/catch: an error thrown from a screen event crashes the client.
var ICON_MARGIN = 6
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
  var y = screen.height - 20 - ICON_MARGIN
  var names = []
  for (var i = 0; i < icons.length; i++) {
    icons[i].setPosition(ICON_MARGIN + i * 24, y)
    names.push(String(icons[i]).split('@')[0] + ' "' + icons[i].getMessage().getString() + '"')
  }
  if (!logged) {
    logged = true
    console.info('[Remnants] title-screen icons lined up: ' + names.join(', '))
  }
}
