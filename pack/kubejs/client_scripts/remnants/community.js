// The NightBeam Community Server and the pack's sponsor (Apex Hosting), on the client only. The server pack never
// carries client scripts or assets (tools/build_pack.py CLIENT_ONLY), so a dedicated server is not touched.
//
// 1. The Multiplayer list gets a "NightBeam Community Server" entry ONCE per install. Shipping servers.dat in the
//    pack's overrides would replace the player's own list on every update, so the entry is added through the game's
//    own ServerList instead: load the player's list, append the entry only if that address is not in it, save. A
//    marker (local/remnants/community_server.json, outside everything the pack ships) records that the address was
//    offered, so a player who deletes the entry does not get it back on the next launch or the next pack update.
//    A new address in a later pack version is offered once again.
// 2. A "Need a server?" button on the title screen (drawn in the menu's own style, bottom right) opens the order
//    screen of Apex's own mod, Apex Hosting Partner Link (since beta 13, at Apex's request): the player picks a
//    plan in game and lands on Apex's checkout with this pack prefilled (config/apexhosting-partner-link.properties
//    holds the affiliate id and the pack's name on their side). That mod also adds its own "Looking for a server?"
//    row to the Multiplayer list, so the pack's button there is only drawn when the mod is missing; without the
//    mod both buttons open the sponsor's page through Minecraft's own link confirmation, as in beta 12.
//    The sprites come from the supplied banner (art/sponsors/, cropped by art/render.cjs, copied by
//    tools/build_menu.py).
// Everything is wrapped in try/catch: an error thrown from a screen event crashes the client.

var COMMUNITY_NAME = 'NightBeam Community Server'
var COMMUNITY_ADDRESS = 'sv6af1d94aa636b.apexmc.co:1376'
var SPONSOR_URL = 'https://apexhost.gg/NightBeam'
var COMMUNITY_MARKER = 'local/remnants/community_server.json'

var PARTNER_LINK_MOD = 'apexhosting_partner_link'
var PARTNER_LINK_API = 'com.apexhosting.partnerlink.ApexPartnerLinkApi'

var CommunityTitleScreen = Java.loadClass('net.minecraft.client.gui.screens.TitleScreen')
var CommunityMultiplayerScreen = Java.loadClass('net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen')
var communityOffered = false

NativeEvents.onEvent(Java.loadClass('net.neoforged.neoforge.client.event.ScreenEvent$Init$Post'), function (event) {
  try {
    var screen = event.getScreen()
    if (screen instanceof CommunityTitleScreen) {
      offerCommunityServer()
      event.addListener(titleSponsorButton(screen))
    } else if (screen instanceof CommunityMultiplayerScreen && !Platform.isLoaded(PARTNER_LINK_MOD)) {
      event.addListener(multiplayerSponsorButton(screen))
    }
  } catch (e) {
    console.error('[Remnants] community server / sponsor button: ' + e)
  }
})

// Once per launch at most, and only until the marker says this address was offered.
function offerCommunityServer() {
  if (communityOffered) return
  communityOffered = true
  var marker = JsonIO.read(COMMUNITY_MARKER)
  if (marker && String(marker.address) === COMMUNITY_ADDRESS) return
  var ServerList = Java.loadClass('net.minecraft.client.multiplayer.ServerList')
  var ServerData = Java.loadClass('net.minecraft.client.multiplayer.ServerData')
  var ServerType = Java.loadClass('net.minecraft.client.multiplayer.ServerData$Type')
  var list = new ServerList(Client)
  list.load()
  var present = false
  for (var i = 0; i < list.size(); i++) {
    if (String(list.get(i).ip).toLowerCase() === COMMUNITY_ADDRESS.toLowerCase()) present = true
  }
  if (!present) {
    list.add(new ServerData(COMMUNITY_NAME, COMMUNITY_ADDRESS, ServerType.OTHER), false)
    list.save()
  }
  JsonIO.write(COMMUNITY_MARKER, { address: COMMUNITY_ADDRESS, added: !present })
  console.info('[Remnants] community server ' + (present ? 'was already in the server list' : 'added to the server list') +
    ' (' + list.size() + ' entries)')
}

function sponsorPress(screen) {
  var ConfirmLinkScreen = Java.loadClass('net.minecraft.client.gui.screens.ConfirmLinkScreen')
  return function (button) {
    try {
      if (Platform.isLoaded(PARTNER_LINK_MOD)) {
        Client.setScreen(Java.loadClass(PARTNER_LINK_API).createConfiguratorScreen(screen))
        return
      }
    } catch (e) {
      console.error('[Remnants] Apex order screen, opening the link instead: ' + e)
    }
    try {
      ConfirmLinkScreen.confirmLinkNow(screen, SPONSOR_URL)
    } catch (e) {
      console.error('[Remnants] sponsor link: ' + e)
    }
  }
}

function sponsorTooltip() {
  var Tooltip = Java.loadClass('net.minecraft.client.gui.components.Tooltip')
  if (Platform.isLoaded(PARTNER_LINK_MOD)) {
    return Tooltip.create(Text.of('Apex Hosting sponsors this pack. Pick a server here and it comes with Remnants already installed.'))
  }
  return Tooltip.create(Text.of('Apex Hosting sponsors this pack. Opens apexhost.gg/NightBeam in your browser (25% off a new server with the code APEX25).'))
}

function sponsorSprite(name) {
  return Java.loadClass('net.minecraft.resources.ResourceLocation').fromNamespaceAndPath('remnants', 'sponsor/' + name)
}

// Title screen: 184x30 units, bottom right, above the copyright line. The whole entry is one image, like the menu's
// own entries (art/out/menu/btn_server_*.png at 4x).
function titleSponsorButton(screen) {
  var ImageButton = Java.loadClass('net.minecraft.client.gui.components.ImageButton')
  var WidgetSprites = Java.loadClass('net.minecraft.client.gui.components.WidgetSprites')
  var sprites = new WidgetSprites(sponsorSprite('need_a_server'), sponsorSprite('need_a_server_hover'))
  var button = new ImageButton(screen.width - 184 - 6, screen.height - 30 - 14, 184, 30, sprites, sponsorPress(screen),
    Text.of('Need a server? Sponsored by Apex Hosting'))
  button.setTooltip(sponsorTooltip())
  return button
}

// Multiplayer screen: a vanilla button with the Apex mark, top right, clear of the centred title. On a narrow screen
// (GUI scale 4 at 1280x720, the default window at scale 3) only the 20x20 mark fits; the tooltip says what it is.
function multiplayerSponsorButton(screen) {
  var SpriteIconButton = Java.loadClass('net.minecraft.client.gui.components.SpriteIconButton')
  var wide = screen.width >= 360
  var width = wide ? 124 : 20
  var button = SpriteIconButton.builder(Text.of('Need a server?'), sponsorPress(screen), !wide)
    .size(width, 20).sprite(sponsorSprite('apex_icon'), 16, 16).build()
  button.setPosition(screen.width - width - 6, 6)
  button.setTooltip(sponsorTooltip())
  return button
}
