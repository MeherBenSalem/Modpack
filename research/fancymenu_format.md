# FancyMenu 3.9.14 + Drippy Loading Screen 3.1.5: hand-written layout format (NeoForge 1.21.1)

Everything here was read from the bytecode of
`fancymenu_neoforge_3.9.14_MC_1.21.1.jar` and `drippyloadingscreen_neoforge_3.1.5_MC_1.21.1.jar` with `javap -c -p -constants`.
Every example block below was also parsed with FancyMenu's own `PropertiesParser` and `ExecutableBlockDeserializer`
classes, run offline. That check confirmed every key/value and that every action resolves to the expected action type
and value. The checks didn't launch Minecraft, so rendering is untested. Class/method names are quoted where the behaviour matters.

---

## 0. File-format rules (from `util/properties/PropertiesParser.deserializeSetFromFancyString`)

- The first line is `type = fancymenu_layout`. A container starts with a line whose whitespace-stripped form **ends with `{`** and
  ends with a line that **starts with `}`**.
- In a property line, the key is the part before the first `=`, with **all whitespace removed**. The value is everything after the first `=`,
  with **exactly one leading space removed** (constant `" "`). So `label = ` and `label =` both give the empty string `""`.
  A missing key gives `null`, which is not the same as an empty value. The serializer writes `"  " + key + " = " + value + "\n"`.
- **Never let a value end with `{`**: the parser would read that line as a new container. A value ending in `}` is fine,
  for example placeholders.
- Newlines inside a value are written as `%%!serialized_property_newline!%%`. The `text_v2` `source` value also accepts `%n%`.
- Resource sources (`util/resource/ResourceSourceType`): `[source:local]/path/relative/to/game/dir`, `[source:web]https://…`,
  `[source:location]namespace:path`.
- Colours (`util/rendering/DrawableColor`): `#RRGGBB`, or `#RRGGBBAA` with **alpha last**. The serializer writes
  `#%02X%02X%02X%02X` as R,G,B,A.
- **Audio file types** (`util/file/type/types/FileTypes`): only **OGG** (`audio/ogg`) and **WAV** (`audio/wav`) are registered.
  **MP3 isn't supported.** Images are png, jpg/jpeg, gif, apng, fma and afma. Video is mp4.
- Anchor names (`customization/element/anchor`): `top-left top-centered top-right mid-left mid-centered mid-right
  bottom-left bottom-centered bottom-right vanilla element`.
- Identifiers (`instance_identifier`, block, action and requirement-container ids) can be any unique token **without whitespace,
  `[`, `]`, `;` or `=`**. The examples use the same `uuid5-1761700000000` style as `tools/build_menu.py`.
- `element_type` ids, each taken from its builder's `super("…")` or `getIdentifier()`: `image`, `vanilla_button`,
  `custom_button` (the plain FancyMenu button), `text_v2`, `audio_v2`, `music_controller`, `progress_bar`.
  Drippy adds `drippy_vanilla_bar`.
- Vanilla widgets use a `vanilla_button { … }` container. Every other element uses `element { … }`.
- The common element keys at the bottom of each block are the same set your `build_menu.py` `common()` already writes. They're kept
  verbatim here.

---

## 1. `vanilla_button`: custom textures, empty label, hover and click sounds

`VanillaWidgetElementBuilder` **extends** `ButtonElementBuilder` and first calls `super.deserializeElement`, so it reads every
custom-button key below and then adds `is_hidden`.

### Example: Singleplayer as a full-image button with no text and custom sounds

```
vanilla_button {
  button_element_executable_block_identifier = ef784959-98ee-5581-a5e1-b91483bf5959-1761700000000
  [executable_block:ef784959-98ee-5581-a5e1-b91483bf5959-1761700000000][type:generic] = [executables:]
  label =
  backgroundnormal = [source:local]/config/fancymenu/assets/btn_singleplayer.png
  backgroundhovered = [source:local]/config/fancymenu/assets/btn_singleplayer_hover.png
  background_texture_inactive = [source:local]/config/fancymenu/assets/btn_singleplayer_inactive.png
  hoversound = [source:local]/config/fancymenu/assets/sounds/ui_hover.ogg
  clicksound = [source:local]/config/fancymenu/assets/sounds/ui_click.ogg
  restartbackgroundanimations = true
  nine_slice_custom_background = false
  nine_slice_border_x = 5
  nine_slice_border_y = 5
  navigatable = true
  widget_active_state_requirement_container_identifier = 5c5ca8b4-70c8-583a-a2d1-d59a7ff061f8-1761700000000
  [loading_requirement_container_meta:5c5ca8b4-70c8-583a-a2d1-d59a7ff061f8-1761700000000] = [groups:][instances:]
  is_template = false
  template_apply_width = false
  template_apply_height = false
  template_apply_posx = false
  template_apply_posy = false
  template_apply_opacity = false
  template_apply_visibility = false
  template_apply_label = false
  template_share_with = buttons
  nine_slice_slider_handle = false
  nine_slice_slider_handle_border_x = 5
  nine_slice_slider_handle_border_y = 5
  element_type = vanilla_button
  instance_identifier = mc_titlescreen_singleplayer_button
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = mid-left
  x = 108
  y = -46
  width = 200
  height = 20
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 9e81e6fb-74a7-54c6-8bdb-0a4493b094c9-1761700000000
  [loading_requirement_container_meta:9e81e6fb-74a7-54c6-8bdb-0a4493b094c9-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
  is_hidden = false
  automated_button_clicks = 0
}
```

### Relevant keys (`ButtonElementBuilder.deserializeElement` plus the `ButtonElement` constructor Properties)

| key | value | notes |
|---|---|---|
| `backgroundnormal` | resource source | image for the normal state |
| `backgroundhovered` | resource source | image for the hovered **or focused** state |
| `background_texture_inactive` | resource source | image for the inactive state (`active == false`) |
| `nine_slice_custom_background` | `true`/`false` | **Keep this `false` for a full-image texture**: see below |
| `nine_slice_border_x` / `nine_slice_border_y` | int (default 5) | used only when nine-slice is `true` |
| `transparent_background` | `true`/`false` | `true` replaces all three backgrounds with a fully transparent PNG |
| `restartbackgroundanimations` | `true`/`false` | only matters for animated textures (GIF/APNG/FMA): restart on hover |
| `label` | text | **Missing key**: the vanilla label is kept. **`label = ` (empty)**: no text. The value goes through `buildComponent`, so `&` codes become `§`, placeholders are replaced, and JSON text components (`{"text":…}`) are accepted |
| `hoverlabel` | text | label used while hovered and active. Omit it to keep `label` |
| `label_base_color` / `label_hover_color` | `#RRGGBB[AA]` | Property, default null (vanilla colour) |
| `label_scale` | float (default 1.0) | Property |
| `label_shadow` | `true`/`false` (default true) | Property |
| `underline_label_on_hover` | `true`/`false` | |
| `hoversound` | resource source (.ogg/.wav) | played on hover start (`MixinAbstractWidget.handleHoverSoundFancyMenu`) |
| `unhover_audio` | resource source (.ogg/.wav) | Property, played when the hover ends |
| `clicksound` | resource source (.ogg/.wav) | **replaces** the vanilla click: `before_playDownSound_FancyMenu` plays it and cancels the vanilla sound |
| `description` | text | tooltip |
| `navigatable` | `true`/`false` | keyboard and controller navigation |
| `is_hidden` | `true`/`false` | vanilla_button only |
| `iconnormal` / `iconhovered` / `icon_texture_inactive` | resource source | **custom_button only**: icons are applied only when the widget `instanceof ExtendedButton` |

**Is nine-slice required for a full-image texture?** No, it must be off. In
`CustomizableWidget.renderCustomBackgroundFancyMenu`, when `isNineSliceCustomBackgroundTexture_FancyMenu()` is false the code calls
`GuiGraphics.blit(tex, x, y, 0f, 0f, w, h, w, h)`. That draws the **whole image stretched to the widget's width and height**.
With nine-slice on, the image is cut into nine pieces using the border sizes. Draw the textures at the button's aspect ratio,
for example 400×40 for a 200×20 button.

**State fallback:** if the texture for the current state is `null`, `renderCustomBackgroundFancyMenu` returns `true`, so
the **vanilla sprite** is drawn for that state. `ButtonElement.updateWidgetTexture` doesn't copy the normal texture into the other states.
Set all three keys.

---

## 2. `custom_button` with actions

### Example: a "Mods" button that opens the NeoForge mod list

```
element {
  button_element_executable_block_identifier = 2a837304-8bb6-50bc-98f1-05e8f9978002-1761700000000
  [executable_action_instance:9f2be88c-c71d-5365-9123-ed663b87465f-1761700000000][action_type:opengui] = net.neoforged.neoforge.client.gui.ModListScreen
  [executable_block:2a837304-8bb6-50bc-98f1-05e8f9978002-1761700000000][type:generic] = [executables:9f2be88c-c71d-5365-9123-ed663b87465f-1761700000000;]
  label = Mods
  backgroundnormal = [source:local]/config/fancymenu/assets/btn_wide.png
  backgroundhovered = [source:local]/config/fancymenu/assets/btn_wide_hover.png
  background_texture_inactive = [source:local]/config/fancymenu/assets/btn_wide_inactive.png
  hoversound = [source:local]/config/fancymenu/assets/sounds/ui_hover.ogg
  clicksound = [source:local]/config/fancymenu/assets/sounds/ui_click.ogg
  underline_label_on_hover = false
  transparent_background = false
  restartbackgroundanimations = true
  nine_slice_custom_background = false
  nine_slice_border_x = 5
  nine_slice_border_y = 5
  label_base_color = #E8DCC8
  label_hover_color = #FFFFFF
  label_scale = 1.0
  label_shadow = true
  navigatable = true
  widget_active_state_requirement_container_identifier = 1e8e5643-5504-5688-9e00-a017a0c29cb1-1761700000000
  [loading_requirement_container_meta:1e8e5643-5504-5688-9e00-a017a0c29cb1-1761700000000] = [groups:][instances:]
  is_template = false
  template_apply_width = false
  template_apply_height = false
  template_apply_posx = false
  template_apply_posy = false
  template_apply_opacity = false
  template_apply_visibility = false
  template_apply_label = false
  template_share_with = buttons
  nine_slice_slider_handle = false
  nine_slice_slider_handle_border_x = 5
  nine_slice_slider_handle_border_y = 5
  element_type = custom_button
  instance_identifier = remnants_mods_button
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = mid-left
  x = 108
  y = 2
  width = 200
  height = 20
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 2268716b-6d76-5e00-82ec-a3774ef11c8c-1761700000000
  [loading_requirement_container_meta:2268716b-6d76-5e00-82ec-a3774ef11c8c-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}
```

### Executable format (verified in `ActionInstance.serialize`, `AbstractExecutableBlock.serialize`, `ExecutableBlockDeserializer.deserializeAll`)

- The element names its block: `button_element_executable_block_identifier = <BLOCK_ID>`
- The block line: `[executable_block:<BLOCK_ID>][type:generic] = [executables:<ACTION_ID_1>;<ACTION_ID_2>;]`.
  Ids are separated by `;`, with a trailing `;` as FancyMenu writes it. `[executables:]` means no actions.
  An optional `[appended:<BLOCK_ID>]` can follow for if/else chains.
- Each action line, in the **same** container: `[executable_action_instance:<ACTION_ID>][action_type:<ACTION_TYPE>] = <VALUE>`.
  The actions run in the order listed in `[executables:…]`.
- Other block types: `generic if else-if else while delay execute-later folder comment`.

### Action ids and values for the title-screen functions

Swap these lines into the block above, and update the `[executables:…]` list to match:

```
  [executable_action_instance:35b7b30b-03dc-5ad9-b9a6-e8d97766944c-1761700000000][action_type:opengui] = select_world_screen
  [executable_action_instance:ee26e917-98a8-5129-9bea-562f89600f7b-1761700000000][action_type:opengui] = join_multiplayer_screen
  [executable_action_instance:beef0abf-8849-57c5-9a6e-96e20cf6c81f-1761700000000][action_type:opengui] = net.neoforged.neoforge.client.gui.ModListScreen
  [executable_action_instance:d5c2b889-1ba1-55d0-964c-cda56a971327-1761700000000][action_type:opengui] = options_screen
  [executable_action_instance:c6ad0924-8732-54c7-bbbf-c2019326a3cb-1761700000000][action_type:quitgame] =
  [executable_action_instance:45f2d4c6-d19b-5158-bc6a-af643fbedc52-1761700000000][action_type:mimicbutton] = title_screen:forge_titlescreen_mods_button
```

| function | `action_type` | value | how it's resolved |
|---|---|---|---|
| Singleplayer world list | `opengui` | `select_world_screen` | universal id → `net.minecraft.client.gui.screens.worldselection.SelectWorldScreen` |
| Multiplayer | `opengui` | `join_multiplayer_screen` | universal id → `net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen` |
| Mods list (NeoForge) | `opengui` | `net.neoforged.neoforge.client.gui.ModListScreen` | no universal id, so use the full class name |
| Options | `opengui` | `options_screen` | universal id → `net.minecraft.client.gui.screens.options.OptionsScreen`. **Note the 1.21 package `screens.options`** |
| Quit | `quitgame` | empty | `QuitGameAction.hasValue() == false` and it calls `Minecraft.stop()` |
| Click a real vanilla button | `mimicbutton` | `<screen id>:<widget id>` | for example `title_screen:forge_titlescreen_mods_button`. It goes through `WidgetLocatorHandler.invokeWidgetOnClick` |

You can also use the full class names with `opengui` instead of the universal ids:
`net.minecraft.client.gui.screens.worldselection.SelectWorldScreen`,
`net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen` and
`net.minecraft.client.gui.screens.options.OptionsScreen`.

How `opengui` builds the screen (`OpenScreenAction.execute`, then `ScreenInstanceFactory.tryConstruct`):

1. A universal id is mapped to a class name (`UniversalScreenIdentifierRegistry`).
2. `OptionsScreen` has a registered provider: `new OptionsScreen(parent, Minecraft.options)`. `CreateWorldScreen` is special-cased
   to `CreateWorldScreen.openFresh`.
3. Any other class is built by reflection: first a public no-arg constructor, otherwise the first public constructor whose parameter types are all in
   `DEFAULT_PARAMETERS` (Minecraft, Screen, Options, LanguageManager, Player, String, ClientAdvancements, Component and the boxed
   primitives). **`Screen` is filled with the current screen** (`ScreenConstructionContext.live()` uses `ScreenUtils.getScreen()`), so Back/Done
   returns to the title screen.

I checked the constructors in the game's own jars
(`libraries/net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar`, which is mojmap-named, and
`libraries/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar`):

- `SelectWorldScreen(Screen)`, `JoinMultiplayerScreen(Screen)`, `OptionsScreen(Screen, Options)`, and
  `net.neoforged.neoforge.client.gui.ModListScreen(Screen)`. All four can be constructed.
- None of these packages is on FancyMenu's screen blacklist (`ScreenCustomization`).

Title-screen widget ids (`TitleScreenWidgetIdentificationContext` and `MixinTitleScreen`):
`mc_titlescreen_singleplayer_button`, `mc_titlescreen_multiplayer_button`, `forge_titlescreen_mods_button`,
`mc_titlescreen_options_button`, `mc_titlescreen_quit_button`, `mc_titlescreen_realms_button`, `mc_titlescreen_playdemo_button`,
`minecraft_logo_widget`, `minecraft_splash_widget`, `minecraft_realms_notification_icons_widget`, `minecraft_branding_widget`,
`title_screen_copyright_button`.

`mc_titlescreen_language_button` and `mc_titlescreen_accessibility_button` are matched on the keys
`narrator.button.language` and `narrator.button.accessibility`. On 1.21.1, `CommonButtons.language` and `CommonButtons.accessibility` use `options.language`
and `options.accessibility`, so **those two ids don't match on 1.21.1**. This agrees with the comment in `build_menu.py`.

---

## 3. Looping menu music

### Recommended: an `audio_v2` element, plus `music_controller` to mute vanilla menu music

```
element {
  audio_instance_0 = [source:local]/config/fancymenu/assets/music/remnants_menu_theme.ogg
  audio_instance_weight_0 = 1.0
  play_mode = normal
  looping = true
  sound_source = music
  volume = 1.0
  element_type = audio_v2
  instance_identifier = remnants_menu_music
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = top-left
  x = 0
  y = 0
  width = 100
  height = 100
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 446e84ae-451e-599c-8bb7-ac4760bd5f02-1761700000000
  [loading_requirement_container_meta:446e84ae-451e-599c-8bb7-ac4760bd5f02-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}

element {
  play_menu_music = false
  play_world_music = true
  element_type = music_controller
  instance_identifier = bf1772a0-2149-51c6-9d36-8e1a1377e056-1761700000000
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = top-left
  x = 0
  y = 0
  width = 2
  height = 2
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 8fac64a2-8c77-5a5e-9dc6-ca1a9e014f1b-1761700000000
  [loading_requirement_container_meta:8fac64a2-8c77-5a5e-9dc6-ca1a9e014f1b-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}
```

Keys (`AudioElementBuilder`, `AudioElement$AudioInstance` and the `AudioElement` constructor):

| key | value | notes |
|---|---|---|
| `element_type` | `audio_v2` | |
| `audio_instance_<N>` | resource source (.ogg/.wav) | one line per track. `N` is any suffix (FancyMenu writes 0,1,2…). Every key starting with `audio_instance_` that doesn't contain `weight` counts as a track |
| `audio_instance_weight_<N>` | float (default 1.0) | weight for shuffle mode |
| `play_mode` | `normal` \| `shuffle` | default `normal` |
| `looping` | `true`/`false` | **`true` loops the playlist**: when the last track ends, `handleNormalModeNext` goes back to index 0 with no random pause. With one track, that track repeats. `false` stops after the last track |
| `volume` | float 0.0–1.0 (default 1.0) | Property |
| `sound_source` | `master music record weather block hostile neutral player ambient voice` | `SoundSource.getName()`. Default `master`. Use `music` so the Music slider controls it |
| `instance_identifier` | unique id | **also the playback cache key**. See persistence below |

The element is only visible in the editor, so its position and size don't matter.

**Persistence** (`AudioElementBuilder.onInitOrResizeScreenCompleted`): the track keeps playing while the
next screen's layout has an element with the **same `instance_identifier`**. Otherwise it's stopped. On a screen where FancyMenu customization is off,
all element audio is stopped. So the music stops when you open Options or the mod list, unless those screens have layouts carrying the same audio element.

`music_controller` (`MusicControllerElementBuilder`) has keys `play_menu_music` and `play_world_music` (both default `true`).
While the layout is active, `MixinMusicManager` cancels the vanilla `MusicManager` tick when `play_menu_music = false`.

### Alternatives

- **Layout open/close audio** (`Layout.serialize` still writes it): a container
  `customization {` / `action = setopenaudio` / `path = [source:local]/….ogg` / `}`. `setcloseaudio` works the same way.
  It's played once by `ScreenAudioPlaybackController` (`stop()` then `play()`). **It doesn't loop.**
- **Global menu music for every menu** (`GlobalCustomizationHandler.tickMenuMusic`), set in `config/fancymenu/options.txt`:
  `S:global_menu_music_tracks = '[source:local]/config/fancymenu/assets/music/remnants_menu_theme.ogg%!source_end!%';`
  The tracks are separated by `%!source_end!%`. It plays on the `MUSIC` channel whenever no world is loaded, and while it has tracks it suppresses vanilla menu music.
  It is **not a seamless loop**: after each track it waits a random 20–600 ticks (1–30 s) before the next one.
- `B:play_vanilla_menu_music = 'false';` in `config/fancymenu/options.txt` turns vanilla menu music off globally (`MixinMusicManager.cancel_startPlaying_FancyMenu`).

---

## 4. `text_v2`

```
element {
  interactable = false
  source = ^^^PRESS ANY BUTTON^^^
  source_mode = direct
  shadow = true
  case_mode = upper
  scale = 1.5
  base_color = #E8DCC8
  text_border = 0
  line_spacing = 2
  enable_scrolling = false
  auto_line_wrapping = false
  remove_html_breaks = true
  parse_markdown = true
  element_type = text_v2
  instance_identifier = 28b419cc-02aa-596d-a6e4-c0ec5bd8f2f3-1761700000000
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = bottom-centered
  x = -150
  y = -60
  width = 300
  height = 20
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 3ff771a8-c4c3-596f-9eb5-b7727174b508-1761700000000
  [loading_requirement_container_meta:3ff771a8-c4c3-596f-9eb5-b7727174b508-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}

element {
  interactable = false
  source = Remnants S1 - Minecraft {"placeholder":"mcversion"} - NeoForge {"placeholder":"loaderver"} - {"placeholder":"totalmods"} mods
  source_mode = direct
  shadow = false
  scale = 0.75
  base_color = #B8AE9C
  text_border = 0
  line_spacing = 2
  enable_scrolling = false
  auto_line_wrapping = false
  remove_html_breaks = true
  parse_markdown = true
  element_type = text_v2
  instance_identifier = 1f7d8803-5962-5e3b-b57e-a61e2189a7b4-1761700000000
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = bottom-left
  x = 4
  y = -14
  width = 400
  height = 10
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 393aa5a4-04c6-57a6-9d86-7ddc9fe5b276-1761700000000
  [loading_requirement_container_meta:393aa5a4-04c6-57a6-9d86-7ddc9fe5b276-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}
```

Keys (`TextElementBuilder` and the `TextElement` constructor Properties):

| key | value | notes |
|---|---|---|
| `source` | text | `%n%` for a newline. Markdown, `&`/`§` formatting codes, and placeholders such as `{"placeholder":"mcversion"}` or `{"placeholder":"modversion","values":{"modid":"x"}}` all work |
| `source_mode` | `direct` \| `resource` | with `resource`, `source` is a resource source pointing to a .txt/.md file |
| `scale` | float (default 1.0) | font scale (Property) |
| `base_color` | `#RRGGBB[AA]` (default white) | text colour (Property) |
| `shadow` | `true`/`false` (default true) | |
| `case_mode` | `upper` \| `lower` | anything else, or a missing key, means normal case |
| `text_border` | int (default 2) | inner padding |
| `line_spacing` | int (default 2) | |
| `auto_line_wrapping` | `true`/`false` | |
| `enable_scrolling` | `true`/`false` (default true) | turn it off for labels |
| `interactable` | `true`/`false` | links and click events |
| `parse_markdown` | `true`/`false` | |
| `remove_html_breaks` | `true`/`false` | |

**Alignment has no key.** It's markdown, per line (`MarkdownParser`): `^^^centered^^^` and `|||right-aligned|||`. Without markers the line is left-aligned.
Centring is relative to the element's `width`. Inline colour is `%#RRGGBB%text%#%`. A lone `%` is plain text, since only `%#` and `%!!` are special.
Avoid `|` elsewhere in a line: lines with an unescaped `|` are table candidates, and they become a table if the next line is a `|---|` separator.

Useful placeholder ids: `mcversion`, `loaderver`, `loadername`, `modversion` (value `modid`), `totalmods`, `loadedmods`.

---

## 5. Drippy Loading Screen 3.1.5

- **Screen identifier:** `drippy_loading_overlay`. `DrippyLoadingScreen.registerAll` registers it as a universal id for
  `de.keksuccino.drippyloadingscreen.customization.DrippyOverlayScreen`. Use it as `identifier` in `layout-meta`.
- **Where the layouts live:** the **normal FancyMenu folder**, `config/fancymenu/customization/*.txt`. FancyMenu's
  `LayoutHandler` reads `/config/fancymenu` + `/customization`. Drippy has no layout folder of its own.
- **Drippy's own config:** `config/drippyloadingscreen/options.txt` (`MOD_DIR` + `/options.txt`, Konkrete config format) holds only
  options: `allow_universal_layouts` (default false), `wait_for_textures_in_loading` (default true, which blocks until images are loaded),
  `fade_out_loading_screen`, `early_fade_out_elements`, and the `early_loading_*` keys.
  The `early_loading_*` keys only take effect if Drippy's separate early-window module is present
  (`isEarlyLoadingModulePresent` checks the system property `drippyloadingscreen.earlywindow.session`). They don't affect the layout below.
- `DrippyOverlayScreen` force-enables its own customization. Your run's `config/fancymenu/customizablemenus.txt` already contains
  `de.keksuccino.drippyloadingscreen.customization.DrippyOverlayScreen {` / `}`. `build_menu.py` currently writes only TitleScreen there,
  so add that entry too.
- Built-in overlay widgets you can address with `vanilla_button`: **`mojang_logo`** and **`progress_bar`**. These are the
  `RendererWidget` ids in `DrippyOverlayScreen`. Hide them with `is_hidden = true`.
- Progress placeholder: **`game_loading_progress`**, or its alias `drippy_gl_percent`. It returns the integer `(int)(progress*100)`, 0–100.
- On this screen Drippy's `MixinElementBuilder` removes these element builders from the editor's add-element menu: `AudioElementBuilder`,
  `BrowserElementBuilder`, `ButtonElementBuilder` (custom and vanilla buttons), `CheckboxElementBuilder`, `CursorElementBuilder`,
  `DraggerElementBuilder`, `InputFieldElementBuilder`, `ItemElementBuilder`, `MusicControllerElementBuilder`, `NativeVideoElementBuilder`,
  `RinkuVideoElementBuilder` and `TooltipElementBuilder`. `MixinMenuBackgroundBuilder` also removes the video and browser backgrounds.
  So **don't use `audio_v2` or `music_controller` in the loading layout**. Image, `text_v2`, `progress_bar`, `drippy_vanilla_bar`, shapes and the
  image `menu_background` remain. Hand-written `vanilla_button` blocks for the overlay's own widgets still apply: they come from widget discovery,
  not that menu.
- GUI scale: Drippy calls `RenderingUtils.resetGuiScale()` and then posts FancyMenu's `InitOrResizeScreenEvent.Pre` for the overlay. That is the
  event where `ScreenCustomizationLayer` applies `setscale`/`autoscale` and rewrites `screen.width/height`. So the same `setscale 2` plus
  `autoscale 1920x1080` header as the title layout gives the same 960×540 unit space. I traced this through the code but didn't run it.

### Full loading-screen layout (for example `config/fancymenu/customization/remnants_loading_screen.txt`)

```
type = fancymenu_layout

layout-meta {
  identifier = drippy_loading_overlay
  render_custom_elements_behind_vanilla = false
  last_edited_time = 1761700000000
  is_enabled = true
  randommode = false
  randomgroup = 1
  randomonlyfirsttime = false
  layout_index = 0
  [loading_requirement_container_meta:9333b71d-0dec-5c6c-9f71-f60137285d7b-1761700000000] = [groups:][instances:]
}

customization {
  action = setscale
  scale = 2.0
}

customization {
  action = autoscale
  basewidth = 1920
  baseheight = 1080
}

menu_background {
  image_path = [source:local]/config/fancymenu/assets/remnants_loading_background.png
  slide = false
  repeat_texture = false
  parallax = false
  parallax_intensity = 0.015
  invert_parallax = false
  restart_animated_on_menu_load = false
  instance_identifier = 691dbbe4-84ea-5787-87cb-9625cace4d3d-1761700000000
  background_type = image
}

customization {
  action = backgroundoptions
  keepaspectratio = true
}

layout_action_executable_blocks {
}

element {
  source = [source:local]/config/fancymenu/assets/remnants_logo.png
  repeat_texture = false
  nine_slice_texture = false
  nine_slice_texture_border_x = 5
  nine_slice_texture_border_y = 5
  image_tint = #FFFFFF
  restart_animated_on_menu_load = false
  element_type = image
  instance_identifier = 3f18c915-5aa2-55f4-85b6-df3a64fd61f4-1761700000000
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = mid-centered
  x = -176
  y = -120
  width = 352
  height = 154
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 869e9210-74c7-506b-bfe3-5392c41ab50c-1761700000000
  [loading_requirement_container_meta:869e9210-74c7-506b-bfe3-5392c41ab50c-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}

element {
  bar_texture = [source:local]/config/fancymenu/assets/loading_bar_fill.png
  bar_nine_slice = false
  background_texture = [source:local]/config/fancymenu/assets/loading_bar_frame.png
  background_nine_slice = false
  direction = right
  progress_for_element_anchor = false
  value_mode = percentage
  progress_source = {"placeholder":"game_loading_progress"}
  smooth_filling_animation = true
  bar_color = #C9A86AFF
  background_color = #1A1714CC
  element_type = progress_bar
  instance_identifier = b5e64a12-209e-5e7a-b250-d7a52648d552-1761700000000
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = mid-centered
  x = -150
  y = 60
  width = 300
  height = 10
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 404ece99-bf4c-514c-ab1a-6bce6c0447b2-1761700000000
  [loading_requirement_container_meta:404ece99-bf4c-514c-ab1a-6bce6c0447b2-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}

element {
  interactable = false
  source = ^^^{"placeholder":"game_loading_progress"}%^^^
  source_mode = direct
  shadow = true
  scale = 1.0
  base_color = #E8DCC8
  text_border = 0
  line_spacing = 2
  enable_scrolling = false
  auto_line_wrapping = false
  remove_html_breaks = true
  parse_markdown = true
  element_type = text_v2
  instance_identifier = e9582a28-2393-5437-9d8c-d2f95537afcd-1761700000000
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = mid-centered
  x = -150
  y = 76
  width = 300
  height = 12
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = 9354998d-6e8e-5e14-89da-b55b333dc0f0-1761700000000
  [loading_requirement_container_meta:9354998d-6e8e-5e14-89da-b55b333dc0f0-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
}

vanilla_button {
  button_element_executable_block_identifier = 605e2024-9dbc-57aa-be18-4e1f1834885f-1761700000000
  [executable_block:605e2024-9dbc-57aa-be18-4e1f1834885f-1761700000000][type:generic] = [executables:]
  restartbackgroundanimations = true
  nine_slice_custom_background = false
  nine_slice_border_x = 5
  nine_slice_border_y = 5
  navigatable = true
  widget_active_state_requirement_container_identifier = 14d8a8b2-878e-55dc-9637-25810d2635a9-1761700000000
  [loading_requirement_container_meta:14d8a8b2-878e-55dc-9637-25810d2635a9-1761700000000] = [groups:][instances:]
  is_template = false
  template_apply_width = false
  template_apply_height = false
  template_apply_posx = false
  template_apply_posy = false
  template_apply_opacity = false
  template_apply_visibility = false
  template_apply_label = false
  template_share_with = buttons
  nine_slice_slider_handle = false
  nine_slice_slider_handle_border_x = 5
  nine_slice_slider_handle_border_y = 5
  element_type = vanilla_button
  instance_identifier = mojang_logo
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = vanilla
  x = 0
  y = 0
  width = 200
  height = 20
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = e1648585-533d-56d2-a46e-6f7490aa8ca1-1761700000000
  [loading_requirement_container_meta:e1648585-533d-56d2-a46e-6f7490aa8ca1-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
  is_hidden = true
  automated_button_clicks = 0
}

vanilla_button {
  button_element_executable_block_identifier = 9b99f3a9-e9f6-5602-ae8e-e0f8e4916add-1761700000000
  [executable_block:9b99f3a9-e9f6-5602-ae8e-e0f8e4916add-1761700000000][type:generic] = [executables:]
  restartbackgroundanimations = true
  nine_slice_custom_background = false
  nine_slice_border_x = 5
  nine_slice_border_y = 5
  navigatable = true
  widget_active_state_requirement_container_identifier = 89a6cf1a-5360-53a8-a4e3-7bf73efa0232-1761700000000
  [loading_requirement_container_meta:89a6cf1a-5360-53a8-a4e3-7bf73efa0232-1761700000000] = [groups:][instances:]
  is_template = false
  template_apply_width = false
  template_apply_height = false
  template_apply_posx = false
  template_apply_posy = false
  template_apply_opacity = false
  template_apply_visibility = false
  template_apply_label = false
  template_share_with = buttons
  nine_slice_slider_handle = false
  nine_slice_slider_handle_border_x = 5
  nine_slice_slider_handle_border_y = 5
  element_type = vanilla_button
  instance_identifier = progress_bar
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = vanilla
  x = 0
  y = 0
  width = 200
  height = 20
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = faf1e38a-396c-59f3-ac40-cc93706e04b2-1761700000000
  [loading_requirement_container_meta:faf1e38a-396c-59f3-ac40-cc93706e04b2-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
  is_hidden = true
  automated_button_clicks = 0
}
```

`progress_bar` keys (`ProgressBarElementBuilder` and the `ProgressBarElement` constructor):

| key | value | notes |
|---|---|---|
| `progress_source` | number, or a placeholder string | `{"placeholder":"game_loading_progress"}`. Non-numeric text is kept as manual input and resolved through placeholders on every read (`Property$ManualInputProperty.deserialize`) |
| `value_mode` | `percentage` \| `float` | percentage expects 0–100. float expects 0–1 |
| `direction` | `right left up down` | `right` fills from the left edge towards the right. `left` is anchored on the right edge. A missing key means `left`, so set it |
| `bar_texture` / `background_texture` | resource source | the bar texture is drawn at full element size and **scissored** to the progress, so it's revealed rather than stretched |
| `bar_nine_slice` / `background_nine_slice` | `true`/`false` | plus `bar_nine_slice_border_top/right/bottom/left` and `background_nine_slice_border_*` (int, default 5) |
| `bar_color` / `background_color` | `#RRGGBB[AA]` | used **only when no texture is set** |
| `smooth_filling_animation` | `true`/`false` (default true) | |
| `progress_for_element_anchor` | `true`/`false` | lets child elements anchor to the moving bar edge |

Drippy also offers a `drippy_vanilla_bar` element: the vanilla-style bar with a single key, `color = #RRGGBB[AA]`, default white.

---

## 6. Copyright and branding on the title screen

- **Branding (bottom-left version and mod-count lines):** you can hide it with `vanilla_button` `instance_identifier = minecraft_branding_widget`, `is_hidden = true`.
  On NeoForge, `MixinNeoForgeTitleScreen` **always** cancels NeoForge's own branding draws: the left lines, the lines above the copyright, and the
  warning above the logo. FancyMenu then draws the collected lines itself inside `minecraft_branding_widget`, so hiding that widget removes all of them.
  `Layout` also converts the legacy `title_screen_branding` element to this same id.

```
vanilla_button {
  button_element_executable_block_identifier = 303562a6-e456-53d6-a648-736159a43f97-1761700000000
  [executable_block:303562a6-e456-53d6-a648-736159a43f97-1761700000000][type:generic] = [executables:]
  restartbackgroundanimations = true
  nine_slice_custom_background = false
  nine_slice_border_x = 5
  nine_slice_border_y = 5
  navigatable = true
  widget_active_state_requirement_container_identifier = 067b97bb-43b4-530d-9d5c-a766c693445d-1761700000000
  [loading_requirement_container_meta:067b97bb-43b4-530d-9d5c-a766c693445d-1761700000000] = [groups:][instances:]
  is_template = false
  template_apply_width = false
  template_apply_height = false
  template_apply_posx = false
  template_apply_posy = false
  template_apply_opacity = false
  template_apply_visibility = false
  template_apply_label = false
  template_share_with = buttons
  nine_slice_slider_handle = false
  nine_slice_slider_handle_border_x = 5
  nine_slice_slider_handle_border_y = 5
  element_type = vanilla_button
  instance_identifier = minecraft_branding_widget
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 0
  auto_sizing_base_screen_height = 0
  sticky_anchor = false
  anchor_point = vanilla
  x = 0
  y = 0
  width = 200
  height = 20
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = fe8ff3c2-391b-55ac-ad96-7770ec375943-1761700000000
  [loading_requirement_container_meta:fe8ff3c2-391b-55ac-ad96-7770ec375943-1761700000000] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
  is_hidden = true
  automated_button_clicks = 0
}
```

- **"Copyright Mojang AB":** it's the `vanilla_button` `title_screen_copyright_button`, and **FancyMenu deliberately prevents hiding it**.
  The checks are in `VanillaWidgetElement`:
  - `isHidden()` returns false for it, `setHidden()` forces false, and `updateWidgetVisibility()` calls `setHiddenFancyMenu(false)`.
  - `getBaseOpacity()` doesn't go below `0.4`.
  - `ButtonElement.getAbsoluteWidth()/getAbsoluteHeight()` don't go below `60`×`6`.
  - `getAbsoluteX()/getAbsoluteY()` keep it fully on screen. `VanillaWidgetEditorElement.handleCopyrightButtonPositionRestrictions` does the same in the editor.

  You **can** move, recolour or re-anchor it, but `is_hidden = true` is ignored. I found no layout option or global option in 3.9.14 that hides it. The
  `label` key isn't covered by these checks, but the code clearly intends to keep the notice visible, so I'd keep it readable.

---

## Appendix: classes read

- FancyMenu: `ButtonElementBuilder`, `ButtonElement`, `VanillaWidgetElementBuilder`, `VanillaWidgetElement`, `CustomizableWidget`,
  `MixinAbstractWidget`, `MixinAbstractButton`, `ActionInstance`, `AbstractExecutableBlock`, `GenericExecutableBlock`,
  `ExecutableBlockDeserializer`, the actions under `customization/action/actions/*` (all ids dumped), `OpenScreenAction`,
  `ScreenInstanceFactory`, `ScreenIdentifierHandler`, `UniversalScreenIdentifierRegistry`, `MimicButtonAction`, `WidgetLocatorHandler`,
  `TitleScreenWidgetIdentificationContext`, `MixinTitleScreen`, `MixinNeoForgeTitleScreen`, `AudioElementBuilder`, `AudioElement` (and
  `$AudioInstance`, `$PlayMode`), `MusicControllerElementBuilder`, `MixinMusicManager`, `GlobalCustomizationHandler`, `ScreenAudioPlaybackController`,
  `Layout`, `ScreenCustomizationLayer`, `TextElementBuilder`, `TextElement`, `MarkdownParser`, `ProgressBarElementBuilder`, `ProgressBarElement`,
  `PropertiesParser`, `PropertyContainer`, `Property$ManualInputProperty`, `DrawableColor`, `FileTypes`, `ResourceSourceType`, `PlaceholderParser`,
  `DeserializedPlaceholderString`, and the placeholder classes.
- Drippy: `DrippyLoadingScreen`, `DrippyOverlayScreen`, `Options`, `DrippyEvents`, `DrippyUtils`, `GameLoadingProgressPercentPlaceholder`,
  `VanillaBarElementBuilder`, `MixinLoadingOverlay`, `MixinElementBuilder`, `MixinMenuBackgroundBuilder`, `MixinImageElement`, `MixinImageMenuBackground`.
- Offline parse check: `tools/ParseCheck.java` in the scratchpad, with the example files in `fmtest/`. It ran against the extracted FancyMenu classes plus the game's
  srg client jar, Konkrete, log4j-api, commons-lang3 and gson.
