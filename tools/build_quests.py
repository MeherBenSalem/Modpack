#!/usr/bin/env python3
"""Compile the readable quest sources in src/quests/*.yaml into FTB Quests files (FTB Quests 2101, NeoForge 1.21.1).

  python3 modpack/tools/build_quests.py            # writes pack/config/ftbquests/quests/
  python3 modpack/tools/build_quests.py --check    # also validates ids against research/registry/*.json

A chapter file looks like:

  chapter: act1_embers          # file name and id seed; never rename once released (ids derive from it)
  group: main                   # a key from src/quests/groups.yaml
  order: 1
  title: "&6Act I: Embers"
  subtitle: "Light the first shrine."
  icon: minecraft:campfire
  quests:
    - key: first_shrine         # unique inside the chapter; ids derive from chapter + key
      title: "The First Ember"
      subtitle: "A fire the dark respects"
      desc: |
        Paragraphs separated by blank lines. Formatting codes like &6 work.
      icon: minecraft:campfire
      pos: [0, 0]               # optional; quests without pos are laid out by dependency depth
      shape: hexagon            # optional
      size: 1.5                 # optional
      deps: [wake, prologue/choose_origin]   # same-chapter keys or chapter/key
      optional: false
      hide_until_deps: false
      repeatable: false
      tasks:   [{item: minecraft:campfire, count: 1}, {tag: minecraft:logs, count: 16},
                {kill: minecraft:zombie, count: 5}, {dimension: ...},
                {structure: ...}, {biome: ...}, {advancement: ...}, {observe: ...}, {checkmark: "Read me"},
                {xp_levels: 10}, {stat: minecraft:mob_kills, value: 100}]
      rewards: [{item: minecraft:bread, count: 4}, {xp: 100}, {xp_levels: 3}, {table: hunters_cache},
                {choice: origin_kits}, {loot: ember_cache}, {command: "/title @p ...", as_player: false}]

Reward tables live in src/quests/reward_tables.yaml and src/quests/reward_tables/*.yaml
(key -> {title, icon, loot_size, rewards: [{item, count, weight}]}).
Item values may also be {id: ..., count: ..., components: {...}} for named or enchanted items.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "quests"
OUT = ROOT / "pack" / "config" / "ftbquests" / "quests"
REGISTRY = ROOT / "research" / "registry"


class L(int):
    pass


class D(float):
    pass


class F(float):
    pass


def qid(*parts):
    """Stable 16-hex id from a seed; first digit 0-7 so it stays a positive long like FTB's own ids."""
    h = hashlib.sha1(("remnants-s1:" + "/".join(map(str, parts))).encode()).hexdigest().upper()[:16]
    return "%X" % (int(h[0], 16) & 7) + h[1:]


KEY_OK = re.compile(r"^[A-Za-z0-9_.+-]+$")  # SNBT's unquoted-key alphabet


def snbt(v, ind=0):
    t = "\t"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, L):
        return f"{int(v)}L"
    if isinstance(v, D):
        return f"{float(v)}d"
    if isinstance(v, F):
        return f"{float(v)}f"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return f"{v}d"
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        if not v:
            return "[ ]"
        if all(isinstance(x, str) for x in v) and sum(len(x) for x in v) < 80:
            return "[" + ", ".join(snbt(x) for x in v) + "]"
        return "[\n" + "".join(t * (ind + 1) + snbt(x, ind + 1) + "\n" for x in v) + t * ind + "]"
    if isinstance(v, dict):
        if not v:
            return "{ }"
        rows = []
        for k in sorted(v):
            key = k if KEY_OK.match(k) else json.dumps(k)
            rows.append(t * (ind + 1) + f"{key}: {snbt(v[k], ind + 1)}")
        return "{\n" + "\n".join(rows) + "\n" + t * ind + "}"
    raise TypeError(f"can't write {v!r}")


def item_stack(spec, count=1):
    if isinstance(spec, str):
        return {"count": count, "id": spec}
    out = {"count": spec.get("count", count), "id": spec["id"]}
    if spec.get("components"):
        out["components"] = spec["components"]
    return out


def lang_lines(text):
    if not text:
        return []
    lines = [ln.rstrip() for ln in text.strip("\n").split("\n")]
    return [ln for ln in lines]


class Compiler:
    def __init__(self):
        self.lang = {}            # file name -> {key: value}
        self.used_ids = set()
        self.quest_ids = {}       # "chapter/key" -> id
        self.tables = {}          # key -> id
        self.refs = []            # (where, kind, value) for --check

    def new_id(self, *parts):
        i = qid(*parts)
        if i in self.used_ids:
            sys.exit(f"id collision for {'/'.join(map(str, parts))}")
        self.used_ids.add(i)
        return i

    def put(self, file, key, value):
        if value in (None, "", []):
            return
        self.lang.setdefault(file, {})[key] = value

    # ---- tasks and rewards ----
    def task(self, chapter, qkey, n, t):
        tid = self.new_id(chapter, qkey, "task", n)
        where = f"{chapter}/{qkey} task {n}"
        out = {"id": tid}
        if "item" in t:
            out.update(type="item", item=item_stack(t["item"]))
            if t.get("count", 1) != 1:
                out["count"] = L(t["count"])
            if t.get("consume"):
                out["consume_items"] = "true"
            self.refs.append((where, "item", t["item"] if isinstance(t["item"], str) else t["item"]["id"]))
        elif "tag" in t:  # any item in an item tag, through FTB Filter System's smart filter
            out.update(type="item", item={"count": 1, "id": "ftbfiltersystem:smart_filter", "components": {
                "ftbfiltersystem:filter": f"ftbfiltersystem:item_tag({t['tag']})"}})
            if t.get("count", 1) != 1:
                out["count"] = L(t["count"])
        elif "kill" in t:
            out.update(type="kill", entity=t["kill"], value=L(t.get("count", 1)))
            self.refs.append((where, "entity", t["kill"]))
        elif "dimension" in t:
            out.update(type="dimension", dimension=t["dimension"])
            self.refs.append((where, "dimension", t["dimension"]))
        elif "structure" in t:
            out.update(type="structure", structure=t["structure"])
            self.refs.append((where, "structure", t["structure"]))
        elif "biome" in t:
            out.update(type="biome", biome=t["biome"])
        elif "advancement" in t:
            out.update(type="advancement", advancement=t["advancement"], criterion=t.get("criterion", ""))
            self.refs.append((where, "advancement", t["advancement"]))
        elif "observe" in t:
            out.update(type="observation", observe_type=t.get("observe_type", 0), timer=L(t.get("timer", 0)),
                       to_observe=t["observe"])
        elif "checkmark" in t:
            out.update(type="checkmark")
        elif "xp_levels" in t:
            out.update(type="xp", value=L(t["xp_levels"]), points=False)
        elif "stat" in t:
            out.update(type="stat", stat=t["stat"], value=t.get("value", 1))
        else:
            sys.exit(f"{where}: unknown task {t}")
        title = t.get("title") or (t["checkmark"] if isinstance(t.get("checkmark"), str) else None)
        self.put(self.cur_lang, f"task.{tid}.title", title)
        return out

    def reward(self, chapter, qkey, n, r):
        rid = self.new_id(chapter, qkey, "reward", n)
        out = {"id": rid}
        if "item" in r:
            out.update(type="item", item=item_stack(r["item"]))
            if r.get("count", 1) != 1:
                out["count"] = r["count"]
            self.refs.append((f"{chapter}/{qkey} reward {n}", "item",
                              r["item"] if isinstance(r["item"], str) else r["item"]["id"]))
        elif "xp" in r:
            out.update(type="xp", xp=r["xp"])
        elif "xp_levels" in r:
            out.update(type="xp_levels", xp_levels=r["xp_levels"])
        elif any(k in r for k in ("table", "choice", "loot")):
            kind = "random" if "table" in r else ("choice" if "choice" in r else "loot")
            key = r.get("table") or r.get("choice") or r.get("loot")
            if key not in self.tables:
                sys.exit(f"{chapter}/{qkey}: unknown reward table {key}")
            out.update(type=kind, table_id=L(int(self.tables[key], 16)))
        elif "command" in r:
            out.update(type="command", command=r["command"], permission_level=r.get("permission_level", 2),
                       elevate_perms=True, silent=r.get("silent", True))
            if r.get("icon"):
                out["icon"] = {"id": r["icon"]}
        else:
            sys.exit(f"{chapter}/{qkey}: unknown reward {r}")
        if r.get("title"):
            self.put(self.cur_lang, f"reward.{rid}.title", r["title"])
        if r.get("team"):
            out["team_reward"] = True
        return out

    # ---- layout ----
    @staticmethod
    def layout(quests):
        """Quests without pos: column = dependency depth inside the chapter, rows spread around 0."""
        keys = {q["key"] for q in quests}
        depth = {}

        def d(q):
            if q["key"] in depth:
                return depth[q["key"]]
            local = [x for x in q.get("deps", []) if "/" not in x and x in keys]
            depth[q["key"]] = 0 if not local else 1 + max(d(by_key[x]) for x in local)
            return depth[q["key"]]

        by_key = {q["key"]: q for q in quests}
        for q in quests:
            d(q)
        columns = {}
        for q in quests:
            if "pos" not in q:
                columns.setdefault(depth[q["key"]], []).append(q)
        for col, qs in columns.items():
            n = len(qs)
            for i, q in enumerate(qs):
                q["pos"] = [col * 2.0, (i - (n - 1) / 2) * 1.75]

    # ---- chapters ----
    def chapter(self, doc, groups):
        ch = doc["chapter"]
        cid = self.new_id("chapter", ch)
        self.cur_lang = f"chapters/{ch}"
        self.put(self.cur_lang, f"chapter.{cid}.title", doc["title"])
        self.put(self.cur_lang, f"chapter.{cid}.chapter_subtitle", lang_lines(doc.get("subtitle", "")))
        quests = doc["quests"]
        self.layout(quests)
        out_q = []
        for q in quests:
            k = q["key"]
            qid_ = self.quest_ids[f"{ch}/{k}"]
            deps = []
            for dkey in q.get("deps", []):
                full = dkey if "/" in dkey else f"{ch}/{dkey}"
                if full not in self.quest_ids:
                    sys.exit(f"{ch}/{k}: unknown dependency {dkey}")
                deps.append(self.quest_ids[full])
            entry = {"id": qid_, "x": D(q["pos"][0]), "y": D(q["pos"][1]),
                     "tasks": [self.task(ch, k, i, t) for i, t in enumerate(q.get("tasks") or [{"checkmark": True}])],
                     "rewards": [self.reward(ch, k, i, r) for i, r in enumerate(q.get("rewards", []))]}
            if deps:
                entry["dependencies"] = deps
            if q.get("icon"):
                entry["icon"] = {"id": q["icon"]}
            for src, dst in (("shape", "shape"), ("size", "size")):
                if q.get(src) is not None:
                    entry[dst] = D(q[src]) if dst == "size" else q[src]
            if q.get("optional"):
                entry["optional"] = True
            if q.get("hide_until_deps"):
                entry["hide_until_deps_complete"] = True
            if q.get("repeatable"):
                entry["can_repeat"] = True
            if q.get("min_deps"):
                entry["min_required_dependencies"] = q["min_deps"]
            if q.get("hide_dependency_lines"):
                entry["hide_dependency_lines"] = True
            self.put(self.cur_lang, f"quest.{qid_}.title", q["title"])
            self.put(self.cur_lang, f"quest.{qid_}.quest_subtitle", q.get("subtitle"))
            self.put(self.cur_lang, f"quest.{qid_}.quest_desc", lang_lines(q.get("desc", "")))
            out_q.append(entry)
        chapter = {"default_hide_dependency_lines": False, "default_quest_shape": doc.get("shape", ""),
                   "filename": ch, "group": groups[doc["group"]], "icon": {"id": doc["icon"]}, "id": cid,
                   "images": [], "order_index": doc.get("order", 0), "quest_links": [], "quests": out_q}
        if doc.get("progression_mode"):
            chapter["progression_mode"] = doc["progression_mode"]
        return ch, chapter

    def run(self):
        meta = yaml.safe_load((SRC / "groups.yaml").read_text())
        groups = {}
        for i, g in enumerate(meta["groups"]):
            groups[g["key"]] = self.new_id("group", g["key"])
        tables_src = yaml.safe_load((SRC / "reward_tables.yaml").read_text()) or {}
        for extra in sorted(SRC.glob("reward_tables/*.yaml")):  # one file per chapter author
            for key, table in (yaml.safe_load(extra.read_text()) or {}).items():
                if key in tables_src:
                    sys.exit(f"{extra.name}: reward table {key} already defined")
                tables_src[key] = table
        for key in tables_src:
            self.tables[key] = self.new_id("table", key)

        docs = []
        for f in sorted(SRC.glob("chapters/*.yaml")):
            doc = yaml.safe_load(f.read_text())
            if not doc:
                continue
            seen = set()
            for q in doc["quests"]:
                if q["key"] in seen:
                    sys.exit(f"{f.name}: duplicate quest key {q['key']}")
                seen.add(q["key"])
                self.quest_ids[f"{doc['chapter']}/{q['key']}"] = self.new_id("quest", doc["chapter"], q["key"])
            docs.append(doc)

        if OUT.exists():
            shutil.rmtree(OUT)
        (OUT / "chapters").mkdir(parents=True)
        (OUT / "reward_tables").mkdir()
        (OUT / "lang" / "en_us" / "chapters").mkdir(parents=True)

        data = {"default_autoclaim_rewards": "disabled", "default_consume_items": False,
                "default_quest_disable_jei": False, "default_quest_shape": "circle", "default_reward_team": False,
                "detection_delay": 20, "disable_gui": False, "drop_loot_crates": False,
                "emergency_items_cooldown": 300, "grid_scale": D(0.5), "icon": {"id": meta["icon"]},
                "lock_message": "", "loot_crate_no_drop": {"boss": 0, "monster": 600, "passive": 4000},
                "pause_game": False, "progression_mode": "flexible", "show_lock_icons": True, "version": 13}
        (OUT / "data.snbt").write_text(snbt(data) + "\n")
        self.put("file", "file.0000000000000001.title", meta["title"])
        (OUT / "chapter_groups.snbt").write_text(snbt({"chapter_groups": [{"id": groups[g["key"]]}
                                                                          for g in meta["groups"]]}) + "\n")
        for g in meta["groups"]:
            self.put("chapter_group", f"chapter_group.{groups[g['key']]}.title", g["title"])

        self.cur_lang = "reward_table"
        for order, (key, t) in enumerate(tables_src.items()):
            tid = self.tables[key]
            rewards = []
            for n, r in enumerate(t["rewards"]):
                e = {"id": self.new_id("table", key, n), "item": item_stack(r["item"])}
                if r.get("count", 1) != 1:
                    e["count"] = r["count"]
                if r.get("weight") is not None:
                    e["weight"] = F(r["weight"])
                rewards.append(e)
                self.refs.append((f"table {key}", "item", r["item"] if isinstance(r["item"], str) else r["item"]["id"]))
            table = {"id": tid, "loot_size": t.get("loot_size", 1), "order_index": order, "rewards": rewards}
            if t.get("icon"):
                table["icon"] = {"id": t["icon"]}
            (OUT / "reward_tables" / f"{key}.snbt").write_text(snbt(table) + "\n")
            self.put("reward_table", f"reward_table.{tid}.title", t["title"])

        n_quests = 0
        for doc in docs:
            name, chapter = self.chapter(doc, groups)
            (OUT / "chapters" / f"{name}.snbt").write_text(snbt(chapter) + "\n")
            n_quests += len(chapter["quests"])

        for file, entries in self.lang.items():
            p = OUT / "lang" / "en_us" / f"{file}.snbt"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(snbt(entries) + "\n")
        return len(docs), n_quests, len(self.tables)


def check(refs):
    """Every item/entity/dimension/structure id must exist in a registry dump or be a vanilla id."""
    known = set()
    for f in REGISTRY.glob("*.json"):
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and all(isinstance(v, str) for v in data.values()):
            for k in data:  # a lang file: item.modid.name -> modid:name
                parts = k.split(".")
                if len(parts) >= 3 and parts[0] in ("item", "block", "entity", "biome"):
                    known.add(f"{parts[1]}:{'.'.join(parts[2:])}")
        elif isinstance(data, dict) and "ids" in data:
            known.update(data["ids"])
    bad = [(w, k, v) for w, k, v in refs if not v.startswith(("minecraft:", "#")) and v not in known]
    for w, k, v in bad:
        print(f"UNKNOWN {k} {v}  ({w})")
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", help="write somewhere else (e.g. a scratch dir) instead of pack/config/ftbquests/quests")
    args = ap.parse_args()
    if args.out:
        global OUT
        OUT = Path(args.out)
    c = Compiler()
    chapters, quests, tables = c.run()
    print(f"{chapters} chapters, {quests} quests, {tables} reward tables -> {OUT}")
    if args.check and not check(c.refs):
        sys.exit(1)


if __name__ == "__main__":
    main()
