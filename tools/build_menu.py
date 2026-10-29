#!/usr/bin/env python3
"""Write the pack's FancyMenu title screen (pack/config/fancymenu/) from the art in art/out/.

  node art/render.cjs <in-game-shot.png> && python3 tools/build_menu.py

Layout (UI scale 2 at 1920x1080, auto-scaled so every window size gets the same 960x540 units): the in-game shot as
background, the logo top-left, and the vanilla buttons in a column under it (Singleplayer, Multiplayer, Mods, then
Options and Quit side by side). The 20x20 icons (language, accessibility, Supplementaries' config) sit in a row below,
placed by pack/kubejs/client_scripts/remnants/title_menu.js. Realms, the vanilla logo and the splash text are hidden.
Format: FancyMenu 3 layout files.
"""
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FM = ROOT / "pack" / "config" / "fancymenu"
ASSETS = FM / "assets"


def uid(seed):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"remnants-s1/{seed}")) + "-1761700000000"


def common(seed, anchor, x, y, w, h):
    req = uid(seed + "/req")
    return f"""  appearance_delay = no_delay
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
  anchor_point = {anchor}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = {req}
  [loading_requirement_container_meta:{req}] = [groups:][instances:]
  enable_parallax = false
  parallax_intensity_v2 = 0.5
  invert_parallax = false
  animated_offset_x = 0
  animated_offset_y = 0
  load_once_per_session = false
  in_editor_color = #FFC800FF
  layer_hidden_in_editor = false
"""


def image(seed, src, anchor, x, y, w, h):
    return f"""element {{
  source = [source:local]/config/fancymenu/assets/{src}
  repeat_texture = false
  nine_slice_texture = false
  nine_slice_texture_border_x = 5
  nine_slice_texture_border_y = 5
  image_tint = #FFFFFF
  restart_animated_on_menu_load = false
  element_type = image
  instance_identifier = {uid(seed)}
{common(seed, anchor, x, y, w, h)}}}
"""


def vanilla(ident, anchor="vanilla", x=0, y=0, w=200, h=20, hidden=False):
    block = uid(ident + "/block")
    active = uid(ident + "/active")
    return f"""vanilla_button {{
  button_element_executable_block_identifier = {block}
  [executable_block:{block}][type:generic] = [executables:]
  restartbackgroundanimations = true
  nine_slice_custom_background = false
  nine_slice_border_x = 5
  nine_slice_border_y = 5
  navigatable = true
  widget_active_state_requirement_container_identifier = {active}
  [loading_requirement_container_meta:{active}] = [groups:][instances:]
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
  instance_identifier = {ident}
{common(ident, anchor, x, y, w, h)}  is_hidden = {"true" if hidden else "false"}
  automated_button_clicks = 0
}}
"""


def layout():
    bg = uid("background")
    meta_req = uid("meta")
    parts = [f"""type = fancymenu_layout

layout-meta {{
  identifier = title_screen
  render_custom_elements_behind_vanilla = true
  last_edited_time = 1761700000000
  is_enabled = true
  randommode = false
  randomgroup = 1
  randomonlyfirsttime = false
  layout_index = 0
  [loading_requirement_container_meta:{meta_req}] = [groups:][instances:]
}}

customization {{
  action = setscale
  scale = 2.0
}}

customization {{
  action = autoscale
  basewidth = 1920
  baseheight = 1080
}}

menu_background {{
  image_path = [source:local]/config/fancymenu/assets/remnants_menu_background.png
  slide = false
  repeat_texture = false
  parallax = false
  parallax_intensity = 0.015
  invert_parallax = false
  restart_animated_on_menu_load = false
  instance_identifier = {bg}
  background_type = image
}}

customization {{
  action = backgroundoptions
  keepaspectratio = true
}}

layout_action_executable_blocks {{
}}

"""]
    # Logo 1600x700 shown at 352x154 units, top-left.
    parts.append(image("logo", "remnants_logo.png", "top-left", 32, 30, 352, 154))
    # Button column centred under the logo (logo centre x = 208).
    col_x, top = 108, -46
    parts.append(vanilla("mc_titlescreen_singleplayer_button", "mid-left", col_x, top, 200, 20))
    parts.append(vanilla("mc_titlescreen_multiplayer_button", "mid-left", col_x, top + 24, 200, 20))
    parts.append(vanilla("forge_titlescreen_mods_button", "mid-left", col_x, top + 48, 200, 20))
    parts.append(vanilla("mc_titlescreen_options_button", "mid-left", col_x, top + 72, 98, 20))
    parts.append(vanilla("mc_titlescreen_quit_button", "mid-left", col_x + 102, top + 72, 98, 20))
    # The 20x20 icons (language, accessibility, mod shortcuts) go in a row under these, moved by
    # pack/kubejs/client_scripts/remnants/title_menu.js: FancyMenu can't name them on 1.21.1.
    for hidden in ("mc_titlescreen_realms_button", "minecraft_realms_notification_icons_widget",
                   "minecraft_logo_widget", "minecraft_splash_widget"):
        parts.append(vanilla(hidden, hidden=True))
    return "\n".join(parts)


def main():
    out = ROOT / "art" / "out"
    ASSETS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out / "logo.png", ASSETS / "remnants_logo.png")
    shutil.copy2(out / "menu_background.png", ASSETS / "remnants_menu_background.png")
    (FM / "customization").mkdir(parents=True, exist_ok=True)
    (FM / "customization" / "remnants_title_screen.txt").write_text(layout())
    (FM / "customizablemenus.txt").write_text(
        "type = customizablemenus\n\nnet.minecraft.client.gui.screens.TitleScreen {\n}\n")
    print("wrote pack/config/fancymenu/customization/remnants_title_screen.txt and assets")


if __name__ == "__main__":
    main()
