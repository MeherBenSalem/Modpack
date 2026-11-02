#!/usr/bin/env python3
"""Compile src/stat_locks.yaml into RPG Stats' configs: items_lock.json, blocks_lock.json, levelup_rewards.json.

  python3 tools/build_stat_locks.py        # writes pack/config/ras/*.json; exits non-zero on an unknown id

Every item and block id is checked against the mod jars (item models, lang keys), the same way
tools/build_progression.py checks the Ember Forge. An item may appear only once.
"""
import importlib.util
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "src" / "stat_locks.yaml"
OUT = ROOT / "pack" / "config" / "ras"


def known_ids():
    spec = importlib.util.spec_from_file_location("bp", ROOT / "tools" / "build_progression.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Jars().known_items()


def main():
    spec = yaml.safe_load(SPEC.read_text())
    known = known_ids()
    errors, seen = [], set()
    attrs = spec["attributes"]
    items = []
    for attr, levels in spec["items"].items():
        for level, ids in sorted(levels.items()):
            for i in ids:
                if i not in known:
                    errors.append(f"unknown item {i} ({attr} {level})")
                if i in seen:
                    errors.append(f"{i} is locked twice")
                seen.add(i)
                items.append(f"[item]{i}[itemEnd][attribute]{attrs[attr]}[attributeEnd][level]{level}[levelEnd]")
    blocks = []
    for level, ids in sorted(spec["blocks"].items()):
        for b in ids:
            if b not in known:
                errors.append(f"unknown block {b} (level {level})")
            blocks.append(f"[block]{b}[blockEnd][level]{level}[levelEnd]")
    r = spec["levelup_rewards"]
    rewards = []
    for level in range(1, r["max_level"] + 1):
        runes = r["every_level"]["count_per_10_levels"] * (level // 10 + 1)
        rewards.append(f"[level]{level}[levelEnd]give @p {r['every_level']['item']} {runes}")
        if level % 5 == 0:
            t = r["every_5"]["item_tiers"]
            rewards.append(f"[level]{level}[levelEnd]give @p {t[min(len(t) - 1, level // 13)]} 1")
        if level % 10 == 0:
            t = r["every_10"]["item_tiers"]
            rewards.append(f"[level]{level}[levelEnd]give @p {t[min(len(t) - 1, level // 11)]} 1")
    for key in ("every_5", "every_10"):
        for i in r[key]["item_tiers"]:
            if i not in known:
                errors.append(f"unknown reward item {i}")
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "items_lock.json").write_text(json.dumps({"enabled": True, "show_tooltip": True, "items_list": items},
                                                    indent=2) + "\n")
    (OUT / "blocks_lock.json").write_text(json.dumps({"enabled": True, "show_feedback": True, "blocks_list": blocks},
                                                     indent=2) + "\n")
    (OUT / "levelup_rewards.json").write_text(json.dumps({"enabled": True, "rewards": rewards}, indent=2) + "\n")
    print(f"{len(items)} item locks, {len(blocks)} block locks, {len(rewards)} level-up rewards -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
