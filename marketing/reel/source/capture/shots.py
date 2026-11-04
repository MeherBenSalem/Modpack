#!/usr/bin/env python3
"""Stages and records every shot of the beta 9 reel on the real client and server (both on the slowed clock).

  python3 shots.py gear                 # once after a (re)join: the Ashborn's kit and staging rules
  python3 shots.py <shot> [<shot>...]   # record shots into $REEL/raw/<shot>.mkv

Every duration below is in game seconds (the rig multiplies by SLOW). Everything on screen is the pack running:
the Threshold and its wake, fog gate and Ser Odric come from threshold.js (`/threshold send`), the Sovereign from its
Sigil, the Echo from a real death (echo.js), ranked monsters from RPG Mobs' own spawn command, the Ember Shrine is
placed and kindled by hand, and the region card is regions.js reacting to the player walking into a new land.
The player is driven with real key presses and mouse moves (Shoulder Surfing's camera, Better Combat swings,
Runeborn's dodge roll and Ember Flask).

Stages: the Threshold arena (frozen at dusk, the black sun to the west), a flat plains field in the Overworld at
(888, 65, -1385) facing west into the sunset (the pack's sun is eclipsed), and the Ashen Wastes of the Eclipsed Realm
at (-63.5, 69, -479.5) facing south toward its black sun (never north: the realm's great tree stays out of frame).
"""
import math
import random
import sys
import threading
import time

from rig import P, Rig

TH = 'remnants:threshold'
OW = 'minecraft:overworld'
ER = 'remnant_bosses:eclipsed_realm'
FIELD = (888.5, 65.0, -1385.5)
REALM = (-63.5, 69.0, -479.5)
DUSK = 12700          # the eclipsed sun just above the western horizon
random.seed(3)


def kit(r):
    """Iron and chain under the Ashen 16x look, the Knight-Errant's Errant Longsword and an Ember Flask."""
    r.cmd(f'clear {P}', f'effect clear {P}', f'gamemode survival {P}',
          f'item replace entity {P} armor.head with minecraft:iron_helmet',
          f'item replace entity {P} armor.chest with minecraft:iron_chestplate',
          f'item replace entity {P} armor.legs with minecraft:chainmail_leggings',
          f'item replace entity {P} armor.feet with minecraft:iron_boots',
          f'item replace entity {P} hotbar.0 with runeborn:errant_longsword',
          f'item replace entity {P} hotbar.1 with runeborn:ember_flask',
          f'effect give {P} minecraft:regeneration infinite 6 true',
          f'effect give {P} minecraft:saturation infinite 0 true',
          f'attribute {P} minecraft:generic.knockback_resistance base set 1')
    r.key('1')


def gear(r):
    r.cmd('gamerule doMobSpawning false', 'gamerule doDaylightCycle false', 'gamerule doWeatherCycle false',
          'gamerule showDeathMessages false', 'gamerule announceAdvancements false', 'gamerule doImmediateRespawn true',
          'gamerule sendCommandFeedback false', 'gamerule keepInventory true', 'gamerule doInsomnia false',
          'gamerule doPatrolSpawning false', 'gamerule doTraderSpawning false', 'weather clear', 'difficulty normal',
          f'gamemode survival {P}')
    kit(r)


def leave(r):
    """Done with the Threshold: marks it passed (threshold.js otherwise brings a 'hub' player back to the crypt) and
    waits out the advancement toasts that grants."""
    r.cmd(f'threshold skip {P}')
    r.tp(OW, FIELD[0], FIELD[1], FIELD[2], 90, 0)
    time.sleep(240)


def clear_near(r, radius=48):
    r.me(f'kill @e[type=!minecraft:player,type=!minecraft:item_frame,type=!minecraft:painting,distance=..{radius}]')
    r.cmd('kill @e[type=minecraft:item]', 'kill @e[type=minecraft:experience_orb]')


def at_field(r, dx=0.0, dz=0.0, yaw=90.0, pitch=0.0, tod=DUSK):
    r.cmd(f'time set {tod}', 'weather clear')
    r.tp(OW, FIELD[0] + dx, FIELD[1], FIELD[2] + dz, yaw, pitch)


def settle(r, game_s=2.0, real_min=25):
    """Lets chunks, particles and the camera's teleport transition settle before a capture, then makes sure the
    Ashborn is really where the shot was staged (a Threshold 'hub' state or a respawn can move them)."""
    time.sleep(max(real_min, 0))
    r.g(game_s)
    want = getattr(r, 'want_dim', None)
    if want:
        got = r.cmd(f'data get entity {P} Dimension')
        if want not in got:
            raise RuntimeError(f'staged in {want} but the Ashborn is in {got.strip()}')


# ------------------------------------------------------------------ the fight driver
class Fighter:
    """Fights `target` like a player would: the camera stays on it (a tracking thread), the Ashborn closes in,
    swings in Better Combat combos, side-rolls on a rhythm and sips the Ember Flask when told to."""

    def __init__(self, r, target, reach=3.2):
        self.r, self.target, self.reach = r, target, reach
        self.stop = threading.Event()
        self.tracker = threading.Thread(target=self._track, daemon=True)

    def _track(self):
        while not self.stop.is_set():
            d = self.r.aim_delta(self.target, aim_h=1.0)
            if d:
                dp = max(-14 - self.r.pitch, min(10 - self.r.pitch, d[1] * 0.35))
                self.r.turn(d[0] * 0.45, dp, 0.18, steps=6)
            else:
                self.r.g(0.18)

    def dist(self):
        me, t = self.r.pos(), self.r.pos(self.target)
        if not me or not t:
            return None
        return math.hypot(t[0] - me[0], t[2] - me[2])

    def roll(self, side):
        k = {'left': 'a', 'right': 'd', 'back': 's'}[side]
        self.r.x('keydown', k)
        self.r.g(0.05)
        self.r.key('Alt_L')
        self.r.g(0.45)
        self.r.x('keyup', k)

    def flask(self):
        self.r.key('2')
        self.r.g(0.1)
        self.r.x('mousedown', '3')
        self.r.g(1.6)
        self.r.x('mouseup', '3')
        self.r.key('1')
        self.r.g(0.2)

    def run(self, seconds, roll_every=2.4, flask_at=None, swing_gap=0.42):
        self.tracker.start()
        t0 = time.time()
        walking = False
        next_roll = roll_every * 0.8
        flasked = flask_at is None
        side = 'left'
        try:
            while (time.time() - t0) / self.r_slow() < seconds:
                el = (time.time() - t0) / self.r_slow()
                if not flasked and el >= flask_at:
                    if walking:
                        self.r.x('keyup', 'w')
                        walking = False
                    self.roll('back')
                    self.flask()
                    flasked = True
                    continue
                d = self.dist()
                if d is None:
                    self.r.g(0.2)
                    continue
                if el >= next_roll and d < 6:
                    if walking:
                        self.r.x('keyup', 'w')
                        walking = False
                    self.roll(side)
                    side = 'right' if side == 'left' else 'left'
                    next_roll = el + roll_every * random.uniform(0.85, 1.2)
                    continue
                if d > self.reach:
                    if not walking:
                        self.r.x('keydown', 'w')
                        walking = True
                    self.r.g(0.12)
                else:
                    if walking:
                        self.r.x('keyup', 'w')
                        walking = False
                    self.r.click(1)
                    self.r.g(swing_gap)
        finally:
            for k in ('w', 'a', 's', 'd'):
                self.r.x('keyup', k)
            self.stop.set()
            self.tracker.join(timeout=30)

    def r_slow(self):
        from rig import SLOW
        return SLOW


# ------------------------------------------------------------------ shots
def sun_hero(r):
    """The Threshold arena at its frozen dusk: the Ashborn walks toward the black sun."""
    r.hud(False)
    r.tp(TH, -44.5, 65, 0.5, 90, -3)
    settle(r)
    r.cap('sun_hero', 7.5)
    r.g(1.0)
    r.x('keydown', 'w')
    threading.Thread(target=r.turn, args=(-5, -2, 5.0), daemon=True).start()
    r.g(3.2)
    r.x('keyup', 'w')
    r.wait_cap()


def sun_stand(r):
    """The Ashborn standing in the arena, facing the black sun; the camera drifts around them (title card bed)."""
    r.hud(False)
    r.tp(TH, -52.5, 65, 0.5, 96, -6)
    settle(r)
    r.cap('sun_stand', 7.0)
    r.turn(-12, 2, 6.5)
    r.wait_cap()


def ow_peak(r):
    """A cliff over the ashen savanna in the Overworld: the eclipsed sun low in the west; the camera pans so the
    Ashborn's helm crosses its disc."""
    r.hud(False)
    r.cmd('time set 12300')
    r.tp(OW, -157.5, 168, -163.5, 104, -6)
    settle(r, real_min=60)
    r.cap('ow_peak', 6.5)
    r.turn(-16, 0, 6.0)
    r.wait_cap()


def realm_sky(r):
    """The Eclipsed Realm: tilt up from the Ashborn to the black sun hanging over it (facing south)."""
    r.hud(False)
    r.tp(ER, REALM[0] + 1.5, REALM[1], REALM[2] - 2.0, 0, 4)
    time.sleep(40)
    r.me('kill @e[type=!minecraft:player,distance=..80]')
    settle(r, 6.0, real_min=30)       # the realm's biome banner fades before the take
    r.cap('realm_sky', 6.0)
    r.g(0.6)
    r.turn(3, -30, 5.0)
    r.wait_cap()


def ranked_setup(r):
    clear_near(r)
    kit(r)
    r.cmd(f'attribute {P} minecraft:generic.knockback_resistance base set 1')
    at_field(r, yaw=90, pitch=-2, tod=13000)
    r.hud(True)
    settle(r, real_min=40)
    # the Champion comes for the Ashborn; an Elite and a named Remnant hold back at the treeline, plates up
    spawns = [('minecraft:zombie', 14, 'champion', 0.0, 10.0, False), ('minecraft:skeleton', 9, 'elite', -5.0, 15.0, True),
              ('minecraft:husk', 23, 'remnant', 5.0, 16.0, True)]
    for kind, lvl, rank, side, dist, still in spawns:
        r.me(f'remnants spawn {kind} {lvl} {rank}')
        sel = f'@e[type={kind},limit=1,sort=nearest,distance=..3]'
        r.cmd(f'execute as {P} at {P} rotated 90 0 run tp {sel} ^{side} ^ ^{dist} facing entity {P}')
        if still:
            r.cmd(f'execute as {P} at {P} run data merge entity @e[type={kind},limit=1,sort=nearest] {{NoAI:1b}}')
    r.cmd(f'execute as {P} at {P} run effect give @e[type=!minecraft:player,distance=..30] minecraft:fire_resistance 600 0 true')


def ranked(r):
    """Ranked RPG Mobs at dusk out of the sunset, their level and rank plates up (HUD on)."""
    ranked_setup(r)
    r.cap('ranked', 6.0)
    r.turn(0, -2, 5.5)
    r.wait_cap()


def ranked_fight(r):
    """One on one with the Champion, plates up: swings, rolls (HUD on)."""
    ranked_setup(r)
    f = Fighter(r, '@e[type=minecraft:zombie,limit=1,sort=nearest]')
    r.cap('ranked_fight', 10.5)
    f.run(10.0, roll_every=2.6)
    r.wait_cap()


def wake(r):
    """/threshold send: black, the bell, 'The sun was eaten an age ago.', the crypt, the area card (HUD on)."""
    r.hud(True)
    r.cmd(f'effect clear {P}', f'gamemode survival {P}')
    r.tp(TH, -3.5, 65, 0.5, 90, 8)
    settle(r, real_min=30)
    r.cap('wake', 11.0)
    r.cmd(f'threshold send {P}')
    r.g(10.5)
    r.wait_cap()
    kit(r)


def fog(r):
    """Through the fog gate into the arena: Ser Odric rises under the black sun (HUD off, then the fight)."""
    r.hud(False)
    r.tp(TH, -36.5, 65, 0.5, 90, -2)
    settle(r, real_min=30)
    r.cap('fog', 7.0)
    r.g(0.6)
    r.x('keydown', 'w')
    r.g(2.4)
    r.x('keyup', 'w')
    r.g(3.5)
    r.wait_cap()


def odric_fight(r, name='odric_fight', hud=True, seconds=13.0, flask_at=7.5):
    """Ser Odric, Gatekeeper of the Threshold: over the shoulder, swings, rolls and a flask (boss bar up)."""
    r.hud(hud)
    f = Fighter(r, '@e[tag=remnants_gatekeeper,limit=1]', reach=3.6)
    r.cap(name, seconds + 0.5)
    f.run(seconds, roll_every=2.2, flask_at=flask_at)
    r.wait_cap()


def warden(r):
    """The Gravebound Warden of the Eclipsed Realm, under the black sun (boss bar up)."""
    r.cmd(f'execute in {ER} run kill @e[type=remnants:gravebound_warden]', f'execute in {ER} run kill @e[type=remnants:ossukage]',
          f'execute in {ER} run kill @e[type=remnants:hollow_sovereign]')
    clear_near(r)
    kit(r)
    r.hud(True)
    r.tp(ER, REALM[0], REALM[1], REALM[2], 0, -6)
    settle(r, real_min=40)
    r.cmd(f'execute as {P} at {P} rotated 0 0 run summon remnants:gravebound_warden ^ ^ ^11')
    r.g(1.0)
    f = Fighter(r, '@e[type=remnants:gravebound_warden,limit=1]', reach=4.0)
    r.cap('warden', 13.5)
    f.run(13.0, roll_every=2.0, flask_at=None)
    r.wait_cap()


def warden_field(r):
    """The Gravebound Warden (Remnant Bosses) on open ground at dusk, the eclipsed sun behind it (boss bar up).
    Leftover bosses are moved out of the world, not killed, so no 'Remnant felled' banner lands in the shot."""
    for t in ('remnants:gravebound_warden', 'remnants:ossukage', 'remnants:hollow_sovereign'):
        r.cmd(f'execute in {OW} as @e[type={t}] run tp @s ~ -120 ~')
    clear_near(r)
    kit(r)
    at_field(r, dx=-4, yaw=90, pitch=-4, tod=12900)
    r.hud(True)
    settle(r, real_min=40)
    r.cmd(f'execute as {P} at {P} rotated 90 0 run summon remnants:gravebound_warden ^ ^ ^12')
    r.g(1.0)
    f = Fighter(r, '@e[type=remnants:gravebound_warden,limit=1,sort=nearest]', reach=4.0)
    r.cap('warden_field', 13.5)
    f.run(13.0, roll_every=2.0, flask_at=None)
    r.wait_cap()


def echo_fall(r):
    """The Ashborn falls on the field (a real death); the Echo rises where they fell."""
    clear_near(r)
    kit(r)
    r.cmd(f'effect clear {P}', f'spawnpoint {P} {int(FIELD[0]) + 9} 65 {int(FIELD[2])}')
    at_field(r, yaw=90, pitch=0, tod=DUSK)
    r.hud(True)
    settle(r, real_min=30)
    r.cmd(f'kill {P}')
    r.g(2.5)


def echo(r):
    """Back to where you fell: 'Echo of Ashborn' wears your armour and holds your light. Then the fight."""
    r.hud(True)
    r.cmd(f'effect give {P} minecraft:regeneration infinite 6 true')
    r.tp(OW, FIELD[0] + 9, FIELD[1], FIELD[2] + 0.5, 90, 2)
    settle(r, real_min=20)
    target = '@e[tag=remnants_echo,limit=1,sort=nearest]'
    f = Fighter(r, target, reach=3.0)
    r.cap('echo', 13.0)
    r.g(1.2)
    f.run(11.5, roll_every=2.5)
    r.wait_cap()


def shrine(r):
    """An Ember Shrine placed on the field and kindled by hand (HUD on: the shrine names itself)."""
    clear_near(r)
    kit(r)
    r.cmd(f'item replace entity {P} hotbar.2 with runeborn:ember_shrine')
    at_field(r, dx=-2, yaw=90, pitch=38, tod=DUSK)
    r.hud(True)
    settle(r, real_min=30)
    r.key('3')
    r.g(0.3)
    r.cap('shrine', 7.0)
    r.g(0.6)
    r.click(3)          # place it
    r.g(1.2)
    r.click(3)          # kindle it
    r.g(1.0)
    threading.Thread(target=r.turn, args=(0, -26, 3.5), daemon=True).start()
    r.g(3.6)
    r.wait_cap()
    r.key('Escape')
    r.key('1')


def shrine2(r):
    """An Ember Shrine placed on the field: it kindles as it is set down. One click only (a second one opens the
    shrine's menu); the camera rises from the flame to the Ashborn and the dusk (HUD off)."""
    clear_near(r)
    kit(r)
    r.cmd(f'item replace entity {P} hotbar.2 with runeborn:ember_shrine')
    at_field(r, dx=-6, dz=3, yaw=96, pitch=42, tod=12850)
    r.hud(False)
    settle(r, real_min=30)
    r.key('3')
    r.g(0.3)
    r.cap('shrine2', 6.0)
    r.g(0.5)
    r.click(3)
    r.g(0.6)
    r.key('1')
    r.turn(-14, -40, 4.2)
    r.wait_cap()


def shrine3(r):
    """The Ember Shrines kindled on the field (by shrine and shrine2) burning at dusk: the Ashborn walks up to them,
    the sunset behind (HUD off)."""
    clear_near(r)
    kit(r)
    r.cmd(f'time set 12850')
    r.tp(OW, 890.5, 64, -1384.0, 92, 6)
    r.hud(False)
    settle(r, real_min=30)
    r.focus()
    r.cap('shrine3', 6.5)
    r.g(0.3)
    r.x('keydown', 'w')
    threading.Thread(target=r.turn, args=(-8, -4, 4.5), daemon=True).start()
    r.g(1.5)
    r.x('keyup', 'w')
    r.g(4.2)
    r.wait_cap()


def region(r):
    """Out of the Grey Wood onto open ground: regions.js fades in 'The Ashen Fields' (HUD on). The Ashborn first
    stands in the forest at (910, -1350) long enough for regions.js to register the Grey Wood and its card to fade,
    then steps onto the field and walks west into the sunset."""
    clear_near(r)
    r.hud(True)
    r.cmd(f'time set {DUSK}')
    r.tp(OW, 910.5, 66, -1350.5, 90, 0)
    time.sleep(30)
    r.g(11)
    r.tp(OW, FIELD[0] + 6, FIELD[1], FIELD[2], 90, -2)
    r.focus()
    r.cap('region', 9.0)
    r.x('keydown', 'w')
    r.g(8.5)
    r.x('keyup', 'w')
    r.wait_cap()


def region2(r):
    """Out of the White Wood into land this Ashborn has never walked: regions.js fades in 'The Broken Crowns' (HUD on)
    (Terralith's forested highlands; the birch-to-highland edge runs along z = -880 at x = 1080)."""
    r.hud(True)
    r.cmd(f'time set {DUSK}', f'effect give {P} minecraft:slow_falling 5 0 true')
    r.tp(OW, 1080.5, 90, -889.5, 0, 0)
    settle(r, 3.0, real_min=40)
    r.focus()
    r.cap('region2', 11.0)
    r.x('keydown', 'w')
    for _ in range(12):            # auto-jump is off in the pack: hop the odd step like a player would
        r.g(0.8)
        r.key('space')
    r.x('keyup', 'w')
    r.wait_cap()


def dusk_rider(r):
    """A Sovereign: the Dusk Rider, called by its Sigil on open ground at dusk (Runeborn), boss bar up (HUD on)."""
    for t in ('remnants:gravebound_warden',):
        r.cmd(f'execute in {OW} as @e[type={t}] at @s run tp @s ~ -120 ~')
    clear_near(r, 64)
    kit(r)
    r.cmd(f'item replace entity {P} hotbar.2 with runeborn:sigil_dusk_rider')
    at_field(r, dx=-6, dz=-2, yaw=90, pitch=-4, tod=12700)
    r.hud(True)
    settle(r, real_min=40)
    r.key('3')
    r.g(0.3)
    r.cap('dusk_rider', 14.0)
    r.g(0.4)
    r.click(3)                      # hold up the Sigil
    r.g(0.6)
    r.key('1')
    r.g(1.2)
    f = Fighter(r, '@e[type=minecraft:skeleton,limit=1,sort=nearest]', reach=3.6)
    f.run(11.0, roll_every=2.2)
    r.wait_cap()


SHOTS = {f.__name__: f for f in (gear, kit, leave, sun_hero, sun_stand, ow_peak, realm_sky, ranked, ranked_fight, wake, fog,
                                 odric_fight, warden, warden_field, echo_fall, echo, shrine, shrine2, shrine3, region, region2, dusk_rider)}

if __name__ == '__main__':
    rig = Rig()
    rig.focus()
    for s in sys.argv[1:]:
        print(f'--- {s}', flush=True)
        SHOTS[s](rig)
        print(f'    done {s}', flush=True)
