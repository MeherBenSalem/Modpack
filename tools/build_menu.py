#!/usr/bin/env python3
"""Write the pack's FancyMenu title screen and Drippy loading screen (pack/config/fancymenu/) from art/out/.

  node art/render.cjs <in-game-shot.png> && python3 tools/build_menu.py

Title screen (UI scale 2 at 1920x1080, auto-scaled so every window gets the same 960x540 units): the dark plate with
the logo (menu_background_dark.png), and the five vanilla buttons re-skinned as centred, text-only entries
(art/out/menu/btn_<entry>_<normal|hover>.png) with a soft chime on hover and a struck bell on click. Keeping the
vanilla buttons keeps their behaviour. Realms, the vanilla logo, the splash text and the version lines are hidden;
FancyMenu won't hide the copyright line. The 20x20 icons (language, accessibility, Create, Supplementaries) sit in
the bottom-left corner, placed by pack/kubejs/client_scripts/remnants/title_menu.js: FancyMenu can't name the
1.21.1 language and accessibility buttons.

Loading screen: the same plate, a thin gold progress bar and the percentage (Drippy Loading Screen layouts are
FancyMenu layouts for the screen drippy_loading_overlay). Format: FancyMenu 3 layout files; the key reference is
in the commit that added this (FancyMenu 3.9.14 bytecode).
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


def vanilla(ident, anchor="vanilla", x=0, y=0, w=200, h=20, hidden=False, skin=None):
    """A vanilla widget. skin: an art key -> full-image textures (normal/hover), no label, the pack's UI sounds."""
    block = uid(ident + "/block")
    active = uid(ident + "/active")
    look = ""
    if skin:
        a = "[source:local]/config/fancymenu/assets"
        look = (f"  label =\n"
                f"  backgroundnormal = {a}/menu/btn_{skin}_normal.png\n"
                f"  backgroundhovered = {a}/menu/btn_{skin}_hover.png\n"
                f"  background_texture_inactive = {a}/menu/btn_{skin}_normal.png\n"
                f"  hoversound = {a}/sounds/ui_hover.ogg\n"
                f"  clicksound = {a}/sounds/ui_click.ogg\n")
    return f"""vanilla_button {{
  button_element_executable_block_identifier = {block}
  [executable_block:{block}][type:generic] = [executables:]
{look}  restartbackgroundanimations = true
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


def header(identifier, background, behind):
    bg = uid(identifier + "/background")
    meta_req = uid(identifier + "/meta")
    return f"""type = fancymenu_layout

layout-meta {{
  identifier = {identifier}
  render_custom_elements_behind_vanilla = {"true" if behind else "false"}
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
  image_path = [source:local]/config/fancymenu/assets/{background}
  slide = false
  repeat_texture = false
  parallax = false
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

"""


ENTRIES = [("mc_titlescreen_singleplayer_button", "singleplayer"), ("mc_titlescreen_multiplayer_button", "multiplayer"),
           ("forge_titlescreen_mods_button", "mods"), ("mc_titlescreen_options_button", "options"),
           ("mc_titlescreen_quit_button", "quit")]


def layout():
    parts = [header("title_screen", "remnants_menu_background_dark.png", True)]
    # Text-only entries, centred under the logo (logo is part of the background plate). 220x22 units each.
    for i, (ident, skin) in enumerate(ENTRIES):
        parts.append(vanilla(ident, "mid-centered", -110, 50 + i * 24, 220, 22, skin=skin))
    for hidden in ("mc_titlescreen_realms_button", "minecraft_realms_notification_icons_widget",
                   "minecraft_logo_widget", "minecraft_splash_widget", "minecraft_branding_widget"):
        parts.append(vanilla(hidden, hidden=True))
    return "\n".join(parts)


def text(seed, source, anchor, x, y, w, h, colour="#E8DCC8", scale=1.0):
    return f"""element {{
  interactable = false
  source = {source}
  source_mode = direct
  shadow = true
  scale = {scale}
  base_color = {colour}
  text_border = 0
  line_spacing = 2
  enable_scrolling = false
  auto_line_wrapping = false
  remove_html_breaks = true
  parse_markdown = true
  element_type = text_v2
  instance_identifier = {uid(seed)}
{common(seed, anchor, x, y, w, h)}}}
"""


def progress_bar(seed, anchor, x, y, w, h):
    a = "[source:local]/config/fancymenu/assets"
    return f"""element {{
  bar_texture = {a}/loading_bar_fill.png
  bar_nine_slice = false
  background_texture = {a}/loading_bar_frame.png
  background_nine_slice = false
  direction = right
  progress_for_element_anchor = false
  value_mode = percentage
  progress_source = {{"placeholder":"game_loading_progress"}}
  smooth_filling_animation = true
  bar_color = #C9A86AFF
  background_color = #1A1714CC
  element_type = progress_bar
  instance_identifier = {uid(seed)}
{common(seed, anchor, x, y, w, h)}}}
"""


def loading_layout():
    parts = [header("drippy_loading_overlay", "remnants_menu_background_dark.png", False)]
    parts.append(progress_bar("loading/bar", "mid-centered", -150, 62, 300, 10))
    parts.append(text("loading/percent", '^^^{"placeholder":"game_loading_progress"}%^^^', "mid-centered", -150, 76, 300, 12))
    parts.append(text("loading/lore", "^^^The sun was eaten an age ago. Something is waking.^^^", "mid-centered",
                      -200, 100, 400, 12, colour="#8C8273"))
    parts.append(vanilla("mojang_logo", hidden=True))
    parts.append(vanilla("progress_bar", hidden=True))
    return "\n".join(parts)


def main():
    out = ROOT / "art" / "out"
    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    (ASSETS / "menu").mkdir(parents=True)
    (ASSETS / "sounds").mkdir()
    shutil.copy2(out / "menu_background_dark.png", ASSETS / "remnants_menu_background_dark.png")
    for f in ("loading_bar_frame.png", "loading_bar_fill.png"):
        shutil.copy2(out / f, ASSETS / f)
    for f in (out / "menu").glob("*.png"):
        shutil.copy2(f, ASSETS / "menu" / f.name)
    for f in (out / "sounds").glob("*.ogg"):
        shutil.copy2(f, ASSETS / "sounds" / f.name)
    custom = FM / "customization"
    if custom.exists():
        shutil.rmtree(custom)
    custom.mkdir(parents=True)
    (custom / "remnants_title_screen.txt").write_text(layout())
    (custom / "remnants_loading_screen.txt").write_text(loading_layout())
    (FM / "customizablemenus.txt").write_text(
        "type = customizablemenus\n\nnet.minecraft.client.gui.screens.TitleScreen {\n}\n\n"
        "de.keksuccino.drippyloadingscreen.customization.DrippyOverlayScreen {\n}\n")
    print("wrote pack/config/fancymenu/customization/remnants_title_screen.txt, remnants_loading_screen.txt and assets")


if __name__ == "__main__":
    main()
