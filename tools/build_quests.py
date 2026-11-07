#!/usr/bin/env python3
"""Compile the readable quest sources in src/quests/*.yaml into a Core RPG - Quests Engine book (1.21.1).

  python3 tools/build_quests.py            # writes pack/config/corerpg_quests/book/
  python3 tools/build_quests.py --check    # also validates ids against research/registry/*.json

The book is plain JSON (book.json, chapters/<chapter>.json, reward_tables/<table>.json). Ids are readable and
stable: a chapter is its file name, a quest is "<chapter>/<key>", a task "<chapter>/<key>/task<n>", a reward
"<chapter>/<key>/reward<n>", a reward table "tables/<key>". Never rename a chapter or a quest key once released:
progress is saved against these ids.

A chapter file looks like:

  chapter: act1_embers          # file name and id
  group: main                   # a key from src/quests/groups.yaml
  order: 1
  title: "&6Act I: Embers"
  subtitle: "Light the first shrine."
  icon: minecraft:campfire
  shape: hexagon                # optional: the chapter's default quest shape
  quests:
    - key: first_shrine         # unique inside the chapter
      title: "The First Ember"
      subtitle: "A fire the dark respects"
      desc: |
        Paragraphs separated by blank lines. Formatting codes like &6 work.
      keeper: |                 # optional: the Keeper's spoken lines, shown in italics above desc
        Plain text, paragraphs separated by blank lines.
      whisper: |                # optional: the same for the unknown voice of the epilogue
      voice: true               # narrate keeper/whisper: listed in src/voice/lines.yaml and played by KubeJS
                                # when the quest completes (subtitles go to chat unless a task is a checkmark)
      unlock: |                 # optional: the Keeper's line when the quest becomes available (its last
                                # dependency completes); voiced and printed in chat, not shown in the book
      icon: minecraft:campfire
      pos: [0, 0]               # optional; quests without pos are laid out by dependency depth
      shape: hexagon            # optional
      size: 1.5                 # optional
      deps: [wake, prologue/choose_origin]   # same-chapter keys or chapter/key
      min_deps: 1               # optional: unlock once this many dependencies are done
      optional: false
      hide_until_deps: false
      hide_dependency_lines: false
      repeatable: false
      tasks:   [{item: minecraft:campfire, count: 1, consume: false}, {tag: minecraft:logs, count: 16},
                {filter: "any(runeborn:emberbrand, #c:swords)", count: 1},
                {kill: minecraft:zombie, count: 5}, {dimension: ...}, {structure: ...}, {biome: ...},
                {advancement: ..., criterion: ...}, {observe: ..., observe_type: 0|1, timer: ticks},
                {checkmark: "Read me"}, {xp_levels: 10}, {stat: minecraft:bell_ring, value: 100}]
      rewards: [{item: minecraft:bread, count: 4}, {xp: 100}, {xp_levels: 3}, {table: hunters_cache},
                {choice: origin_kits}, {command: "/lastlight arrive huntmaster {p}"}]

Reward tables live in src/quests/reward_tables.yaml and src/quests/reward_tables/*.yaml
(key -> {title, icon, loot_size, rewards: [{item, count, weight}]}).
Item values may also be {id: ..., count: ..., components: {...}} for named or enchanted items.

Narration: quests with a voiced line, and the dependencies of quests with an unlock line, get a completion command
("remnants_vo completed <team> <quest>") that kubejs/server_scripts/remnants/narration.js handles.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "quests"
OUT = ROOT / "pack" / "config" / "corerpg_quests" / "book"
OLD_FTB = ROOT / "pack" / "config" / "ftbquests"
VOICE_SRC = ROOT / "src" / "voice"
# startup script: KubeJS 2101 only lets startup scripts assign to `global`; server scripts read it
NARRATION_JS = ROOT / "pack" / "kubejs" / "startup_scripts" / "remnants_narration_lines.js"
REGISTRY = ROOT / "research" / "registry"
NARRATION_COMMAND = "remnants_vo completed {team} {quest}"
# advancement id -> {"key": translation key} or {"text": ...}; written by tools/dump_advancement_titles.py
_ADV = REGISTRY / "advancement_titles.json"
ADV_TITLES = json.loads(_ADV.read_text()) if _ADV.exists() else {}

ID_OK = re.compile(r"^[a-z0-9_./-]{1,64}$")
SHAPES = {"circle", "square", "rsquare", "diamond", "pentagon", "hexagon", "octagon", "heart", "gear", "shield",
          "star", "none", ""}


def item_value(spec):
    """An item id, or the vanilla item stack object for named/enchanted items (count lives on the task)."""
    if isinstance(spec, str):
        return spec
    out = {"id": spec["id"]}
    if spec.get("components"):
        out["components"] = spec["components"]
    return out if len(out) > 1 else spec["id"]


def item_id(spec):
    return spec if isinstance(spec, str) else spec["id"]


def item_count(spec, outer):
    if outer is not None:
        return outer
    return 1 if isinstance(spec, str) else spec.get("count", 1)


PLACE_NAMES = {"#minecraft:village": "a village", "minecraft:the_nether": "the Nether", "minecraft:the_end": "the End",
               "minecraft:overworld": "the Overworld", "deeperdarker:otherside": "the Otherside",
               "remnant_bosses:eclipsed_realm": "the Eclipsed Realm", "minecraft:ancient_city": "an Ancient City",
               "betteroceanmonuments:ocean_monument": "an Ocean Monument", "betterfortresses:fortress": "a Nether Fortress",
               "betterstrongholds:stronghold": "a Stronghold", "remnant_bosses:grace_shrine": "a Grace Shrine",
               "remnant_bosses:hollow_citadel": "the Hollow Citadel",
               "remnant_bosses:gravebound_catacombs": "the Gravebound Catacombs",
               "remnant_bosses:forgotten_observatory": "the Forgotten Observatory"}


def place_name(rid):
    """'betterstrongholds:stronghold' -> 'Stronghold'; tags and vanilla dimensions read naturally."""
    if rid in PLACE_NAMES:
        return PLACE_NAMES[rid]
    path = rid.lstrip("#").split(":")[-1].split("/")[-1]
    return " ".join(w if w in ("of", "the", "and") else w.capitalize() for w in path.split("_"))


def lang_lines(text):
    if not text:
        return []
    return [ln.rstrip() for ln in text.strip("\n").split("\n")]


SPEAKERS = {  # yaml field -> (header, text colour)
    "keeper": ("&6The Keeper", "&f&o"),
    "whisper": ("&5&k|||&r &5A voice from nowhere &k|||", "&d&o"),
}


def spoken(field, text, voiced):
    """The italic, quoted speech block that opens a quest's description."""
    header, colour = SPEAKERS[field]
    paras = [" ".join(p.split()) for p in text.strip().split("\n\n") if p.strip()]
    lines = [header + ("&r &e♪" if voiced else "&r")]
    for i, para in enumerate(paras):
        quote_open = '"' if i == 0 else ""
        quote_close = '"' if i == len(paras) - 1 else ""
        lines += ["", f"{colour}{quote_open}{para}{quote_close}&r"]
    return lines


def spoken_text(text):
    return "\n\n".join(" ".join(p.split()) for p in text.strip().split("\n\n") if p.strip())


def number(v):
    """Whole numbers as ints so the JSON stays tidy."""
    f = float(v)
    return int(f) if f.is_integer() else f


class Compiler:
    def __init__(self):
        self.used_ids = set()
        self.quest_ids = {}       # "chapter/key" -> id
        self.tables = {}          # key -> id
        self.refs = []            # (where, kind, value) for --check
        self.voice = []           # narrated lines: {line, quest, speaker, text, chat}
        self.unlocks = []         # lines spoken when a quest becomes available: {line, quest, deps, text}

    def new_id(self, value):
        if not ID_OK.match(value):
            sys.exit(f"invalid id {value!r}: use a-z 0-9 _ - . / (at most 64 characters)")
        if value in self.used_ids:
            sys.exit(f"id collision for {value}")
        self.used_ids.add(value)
        return value

    @staticmethod
    def text(where, value):
        """Core RPG reads '&' + a code as formatting; keep a bare '&' out of the book ("Hearth and Harvest")."""
        for line in (value if isinstance(value, list) else [value]):
            bad = re.search(r"&(?![0-9a-fk-orA-FK-OR])", line or "")
            if bad:
                sys.exit(f"{where}: '&' that isn't a formatting code: {line[max(0, bad.start() - 20):bad.end() + 20]!r}")
        return value

    # ---- tasks and rewards ----
    def task(self, qid, n, t):
        out = {"id": self.new_id(f"{qid}/task{n}")}
        where = f"{qid} task {n}"
        if "item" in t:
            out.update(type="item", item=item_value(t["item"]))
            count = item_count(t["item"], t.get("count"))
            if count != 1:
                out["count"] = count
            if t.get("consume"):
                out["consume_items"] = "true"
            self.refs.append((where, "item", item_id(t["item"])))
        elif "filter" in t:  # a Core RPG filter expression, e.g. "any(runeborn:emberbrand, #c:swords)"
            out.update(type="item", filter=t["filter"])
            if t.get("count", 1) != 1:
                out["count"] = t["count"]
            if t.get("consume"):
                out["consume_items"] = "true"
            for atom in re.findall(r"(?<![#@\w])([a-z0-9_.-]+:[a-z0-9_./-]+)", t["filter"]):
                self.refs.append((where, "item", atom))
        elif "tag" in t:  # any item in an item tag, through a filter expression
            out.update(type="item", filter=f"#{t['tag']}")
            if t.get("count", 1) != 1:
                out["count"] = t["count"]
            if t.get("consume"):
                out["consume_items"] = "true"
        elif "kill" in t:
            out.update(type="kill", entity=t["kill"])
            if t.get("count", 1) != 1:
                out["value"] = t["count"]
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
            out.update(type="advancement", advancement=t["advancement"])
            if t.get("criterion"):
                out["criterion"] = t["criterion"]
            self.refs.append((where, "advancement", t["advancement"]))
        elif "observe" in t:
            entity = t.get("observe_type", 0) in (1, "entity")
            out.update(type="observation", target="entity" if entity else "block")
            out["entity" if entity else "block"] = t["observe"]
            if t.get("timer"):
                out["ticks"] = max(1, int(t["timer"]))
        elif "checkmark" in t:
            out.update(type="checkmark")
        elif "xp_levels" in t:
            out.update(type="xp", value=t["xp_levels"])
        elif "stat" in t:
            out.update(type="stat", stat=t["stat"])
            if t.get("value", 1) != 1:
                out["value"] = t["value"]
        else:
            sys.exit(f"{where}: unknown task {t}")
        title = t.get("title") or (t["checkmark"] if isinstance(t.get("checkmark"), str) else None)
        if title:
            out["title"] = self.text(where, title)
        elif "structure" in t or "dimension" in t:
            # Structures and dimensions have no translated names, so name them from the id.
            out["title"] = ("Find " if "structure" in t else "Enter ") + place_name(t.get("structure") or t["dimension"])
        elif "advancement" in t and t["advancement"] in ADV_TITLES:
            # The advancement's own name (clients only know the advancements they can already see).
            known = ADV_TITLES[t["advancement"]]
            out["title"] = f"lang:{known['key']}" if "key" in known else known["text"]
        if t.get("optional"):
            out["optional_task"] = True
        return out

    def reward(self, qid, n, r):
        out = {"id": self.new_id(f"{qid}/reward{n}")}
        where = f"{qid} reward {n}"
        if "item" in r:
            out.update(type="item", item=item_value(r["item"]))
            count = item_count(r["item"], r.get("count"))
            if count != 1:
                out["count"] = count
            self.refs.append((where, "item", item_id(r["item"])))
        elif "xp" in r:
            out.update(type="xp", xp=r["xp"])
        elif "xp_levels" in r:
            out.update(type="xp_levels", levels=r["xp_levels"])
        elif any(k in r for k in ("table", "choice", "loot")):
            if "loot" in r:
                sys.exit(f"{where}: loot crate rewards are not used by this pack; use table: or choice:")
            kind = "random" if "table" in r else "choice"
            key = r.get("table") or r.get("choice")
            if key not in self.tables:
                sys.exit(f"{where}: unknown reward table {key}")
            out.update(type=kind, table=self.tables[key])
        elif "command" in r:
            out.update(type="command", command=r["command"])
            if r.get("permission_level", 2) != 2:
                out["permission_level"] = r["permission_level"]
            if not r.get("silent", True):
                out["silent"] = False
        else:
            sys.exit(f"{where}: unknown reward {r}")
        if r.get("title"):
            out["title"] = self.text(where, r["title"])
        if r.get("icon"):
            out["icon"] = r["icon"]
        if r.get("team"):
            out["team_reward"] = "true"
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
        out = {"id": ch, "title": self.text(ch, doc["title"]), "icon": doc["icon"], "group": groups[doc["group"]]}
        if doc.get("subtitle"):
            out["subtitle"] = self.text(ch, lang_lines(doc["subtitle"]))
        if doc.get("shape"):
            if doc["shape"] not in SHAPES:
                sys.exit(f"{ch}: unknown shape {doc['shape']}")
            out["default_quest_shape"] = doc["shape"]
        if doc.get("progression_mode"):
            out["progression_mode"] = doc["progression_mode"]
        quests = doc["quests"]
        self.layout(quests)
        out_q = []
        for q in quests:
            k = q["key"]
            qid = self.quest_ids[f"{ch}/{k}"]
            deps = []
            for dkey in q.get("deps", []):
                full = dkey if "/" in dkey else f"{ch}/{dkey}"
                if full not in self.quest_ids:
                    sys.exit(f"{qid}: unknown dependency {dkey}")
                deps.append(self.quest_ids[full])
            entry = {"id": qid, "title": self.text(qid, q["title"])}
            if q.get("subtitle"):
                entry["subtitle"] = self.text(qid, q["subtitle"])
            if q.get("icon"):
                entry["icon"] = q["icon"]
                self.refs.append((qid, "icon", q["icon"]))
            entry["x"], entry["y"] = number(q["pos"][0]), number(q["pos"][1])
            if q.get("shape"):
                if q["shape"] not in SHAPES:
                    sys.exit(f"{qid}: unknown shape {q['shape']}")
                entry["shape"] = q["shape"]
            if q.get("size") is not None:
                entry["size"] = number(q["size"])
            if deps:
                entry["dependencies"] = deps
            if q.get("min_deps"):
                entry["min_required_dependencies"] = q["min_deps"]
            if q.get("optional"):
                entry["optional"] = True
            if q.get("hide_until_deps"):
                entry["hide_until_deps_complete"] = "true"
            if q.get("repeatable"):
                entry["repeatable"] = True
            if q.get("hide_dependency_lines"):
                entry["hide_dependency_lines"] = "true"

            desc = []
            for field in SPEAKERS:
                if q.get(field):
                    desc += spoken(field, q[field], bool(q.get("voice")))
                    if q.get("voice"):
                        tasks = q.get("tasks") or [{"checkmark": True}]
                        self.voice.append({"line": f"{ch}_{k}", "quest": qid, "speaker": field,
                                           "text": spoken_text(q[field]),
                                           "chat": not any("checkmark" in t for t in tasks)})
            if q.get("voice") and not desc:
                sys.exit(f"{qid}: voice: true needs a keeper or whisper text")
            if q.get("unlock"):
                if not deps:
                    sys.exit(f"{qid}: unlock needs deps (it plays when the last one completes)")
                self.unlocks.append({"line": f"{ch}_{k}_unlock", "quest": qid, "deps": deps,
                                     "text": spoken_text(q["unlock"])})
            body = lang_lines(q.get("desc", ""))
            if desc and body:
                desc.append("")
            if desc + body:
                entry["description"] = self.text(qid, desc + body)
            entry["tasks"] = [self.task(qid, i, t) for i, t in enumerate(q.get("tasks") or [{"checkmark": True}])]
            entry["rewards"] = [self.reward(qid, i, r) for i, r in enumerate(q.get("rewards", []))]
            out_q.append(entry)
        out["quests"] = out_q
        return ch, out

    def run(self):
        meta = yaml.safe_load((SRC / "groups.yaml").read_text())
        groups = {g["key"]: self.new_id(f"groups/{g['key']}") for g in meta["groups"]}
        tables_src = yaml.safe_load((SRC / "reward_tables.yaml").read_text()) or {}
        for extra in sorted(SRC.glob("reward_tables/*.yaml")):  # one file per chapter author
            for key, table in (yaml.safe_load(extra.read_text()) or {}).items():
                if key in tables_src:
                    sys.exit(f"{extra.name}: reward table {key} already defined")
                tables_src[key] = table
        for key in tables_src:
            self.tables[key] = self.new_id(f"tables/{key}")

        docs = []
        for f in sorted(SRC.glob("chapters/*.yaml")):
            doc = yaml.safe_load(f.read_text())
            if not doc:
                continue
            self.new_id(doc["chapter"])
            for q in doc["quests"]:
                full = f"{doc['chapter']}/{q['key']}"
                if full in self.quest_ids:
                    sys.exit(f"{f.name}: duplicate quest key {q['key']}")
                self.quest_ids[full] = self.new_id(full)
            docs.append(doc)
        docs.sort(key=lambda d: (list(groups).index(d["group"]), d.get("order", 0), d["chapter"]))

        if OUT.exists():
            shutil.rmtree(OUT)
        (OUT / "chapters").mkdir(parents=True)
        (OUT / "reward_tables").mkdir()
        if OLD_FTB and OLD_FTB.exists():  # the pack used FTB Quests until 1.0.0-beta.11
            shutil.rmtree(OLD_FTB)

        def write(path, data):
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

        for order, (key, t) in enumerate(tables_src.items()):
            tid = self.tables[key]
            entries = []
            for n, r in enumerate(t["rewards"]):
                e = {"id": self.new_id(f"{tid}/{n}"), "type": "item", "item": item_value(r["item"])}
                count = item_count(r["item"], r.get("count"))
                if count != 1:
                    e["count"] = count
                e["weight"] = number(r.get("weight", 1))
                entries.append(e)
                self.refs.append((f"table {key}", "item", item_id(r["item"])))
            table = {"id": tid, "title": self.text(tid, t["title"])}
            if t.get("icon"):
                table["icon"] = t["icon"]
            if t.get("loot_size", 1) != 1:
                table["rolls"] = t["loot_size"]
            table["entries"] = entries
            write(OUT / "reward_tables" / f"{tid.replace('/', '~')}.json", table)

        n_quests = 0
        chapters = []
        for doc in docs:
            name, chapter = self.chapter(doc, groups)
            chapters.append((name, chapter))
            n_quests += len(chapter["quests"])
        # Narration hooks, now that every voiced line and unlock is known.
        hooked = {v["quest"] for v in self.voice} | {d for u in self.unlocks for d in u["deps"]}
        for name, chapter in chapters:
            for q in chapter["quests"]:
                if q["id"] in hooked:
                    q["completion_command"] = NARRATION_COMMAND
            write(OUT / "chapters" / f"{name}.json", chapter)

        book = {"title": self.text("book", meta["title"]), "icon": meta["icon"],
                "lock_message": "&7Finish the quests that lead here first.",
                "progression_mode": "flexible", "default_quest_shape": "circle", "detection_delay": 20,
                "emergency_items_cooldown": 300, "loot_crate_drops": False,
                "groups": [{"id": groups[g["key"]], "title": self.text(g["key"], g["title"])} for g in meta["groups"]],
                "chapter_order": [name for name, _ in chapters]}
        write(OUT / "book.json", book)
        self.write_voice()
        return len(docs), n_quests, len(self.tables)

    def write_voice(self):
        """src/voice/lines.yaml is the recording script; narration_lines.js tells KubeJS what to play.

        Lines come from the quests (keeper/whisper + voice: true) and from src/voice/extra_lines.yaml (the
        Threshold's cinematics)."""
        script = {v["line"]: {"speaker": v["speaker"], "text": v["text"]} for v in self.voice}
        script.update({u["line"]: {"speaker": "keeper", "text": u["text"]} for u in self.unlocks})
        extra = yaml.safe_load((VOICE_SRC / "extra_lines.yaml").read_text()) if (VOICE_SRC / "extra_lines.yaml").exists() else {}
        for line, e in (extra or {}).items():
            if line in script:
                sys.exit(f"extra_lines.yaml: {line} is also a quest line")
            script[line] = {"speaker": e["speaker"], "text": spoken_text(e["text"])}
        VOICE_SRC.mkdir(parents=True, exist_ok=True)
        (VOICE_SRC / "lines.yaml").write_text(
            "# Generated by tools/build_quests.py from the quests' keeper/whisper text and extra_lines.yaml.\n"
            "# Record each line as src/voice/raw/<line>.mp3, then run tools/build_voice.py.\n"
            + yaml.safe_dump(script, sort_keys=False, allow_unicode=True, width=1000))
        lines = {k: {"speaker": v["speaker"], "text": v["text"].split("\n\n")} for k, v in script.items()}
        quests = {v["quest"]: {"line": v["line"], "chat": v["chat"]} for v in self.voice}
        unlocks = {}   # dependency quest id -> the quests it may unlock, with all their dependencies
        for u in self.unlocks:
            for d in u["deps"]:
                unlocks.setdefault(d, []).append({"quest": u["quest"], "deps": u["deps"], "line": u["line"]})
        NARRATION_JS.parent.mkdir(parents=True, exist_ok=True)
        NARRATION_JS.write_text(
            "// priority: 100\n"
            "// Generated by tools/build_quests.py. Do not edit; edit src/quests/ or src/voice/extra_lines.yaml.\n"
            "global.REMNANTS_LINES = " + json.dumps(lines, indent=2, ensure_ascii=False) + "\n"
            "global.REMNANTS_NARRATION = " + json.dumps(quests, indent=2) + "\n"
            "global.REMNANTS_UNLOCKS = " + json.dumps(unlocks, indent=2) + "\n")

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
    # the pack's own items (KubeJS, named in kubejs/assets/<ns>/lang/en_us.json)
    for f in (ROOT / "pack" / "kubejs" / "assets").glob("*/lang/en_us.json"):
        for k in json.loads(f.read_text()):
            parts = k.split(".")
            if len(parts) == 3 and parts[0] in ("item", "block"):
                known.add(f"{parts[1]}:{parts[2]}")
    # the pack's own datapack (KubeJS): advancements, dimensions, functions it defines
    for f in (ROOT / "pack" / "kubejs" / "data").glob("*/*/**/*.json"):
        ns, kind = f.relative_to(ROOT / "pack" / "kubejs" / "data").parts[:2]
        rel = f.relative_to(ROOT / "pack" / "kubejs" / "data" / ns / kind).with_suffix("")
        known.add(f"{ns}:{rel.as_posix()}")
    bad = [(w, k, v) for w, k, v in refs if not v.startswith(("minecraft:", "#")) and v not in known]
    for w, k, v in bad:
        print(f"UNKNOWN {k} {v}  ({w})")
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", help="write somewhere else (e.g. a scratch dir) instead of pack/config/corerpg_quests/book")
    args = ap.parse_args()
    if args.out:
        global OUT, OLD_FTB
        OUT = Path(args.out)
        OLD_FTB = None
    c = Compiler()
    chapters, quests, tables = c.run()
    print(f"{chapters} chapters, {quests} quests, {tables} reward tables -> {OUT}")
    if args.check and not check(c.refs):
        sys.exit(1)


if __name__ == "__main__":
    main()
