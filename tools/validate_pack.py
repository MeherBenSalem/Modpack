#!/usr/bin/env python3
"""Validate the quests, the Ember Forge and the progression against what the game really registers.

  python3 tools/validate_pack.py                 # exit 1 if any check fails
  python3 tools/validate_pack.py --json out.json # also write the findings as JSON
  python3 tools/validate_pack.py --why create:brass_ingot    # how (or why not) an item can be obtained, and from when
  python3 tools/validate_pack.py --write-doc     # rewrite the generated tables in design/PROGRESSION_GRAPH.md

Reads src/quests/, src/progression.yaml, src/validation.yaml and research/registry/live/ (the game's own ids, tags,
recipes and loot tables, dumped from a running server by tools/dump_live.py: run that after every mod update).
Nothing is booted here, so it runs in seconds and in CI.

Checks
  book        the compiled book (pack/config/corerpg_quests/book), the narration script and src/voice/lines.yaml are
              what tools/build_quests.py makes from src/quests today
  graph       every dependency exists, no quest depends on itself or sits in a cycle, min_deps is satisfiable, and
              no required quest waits on an optional one
  ids         every item, entity, advancement, structure, biome and dimension a task, reward, icon or reward table
              names is registered (tags must exist and have members); reward commands exist
  obtainable  every item a task asks the player to hold or hand in can be obtained in survival: a recipe whose
              ingredients can be obtained, a loot table, a block the world generates, or an entry in
              src/validation.yaml (things the game hands out in code, each with its reason)
  forge       every recipe the pack adds or rebuilds (remnants:*) has registered, obtainable ingredients, and every
              custom item can be made
  stages      every item a quest asks for exists by that quest's part of the story (src/progression.yaml `stages`:
              a quest in Act I must not ask for something only the Nether has), counting what a recipe can make
              earlier and what required earlier quests hand out
  gates       src/progression.yaml `gates`: every gated recipe's ingredients can be had no later than the quest that
              needs its output, nothing is gated behind itself, and nothing needs an optional quest's reward
  fragments   by the end of every stage, required main-line quests have paid at least the declared share of the
              Sovereign Fragments the gates have asked for so far
  doc         the generated tables in design/PROGRESSION_GRAPH.md match this data (--write-doc rewrites them)
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "research" / "registry" / "live"
QUESTS = ROOT / "src" / "quests"
RULES = ROOT / "src" / "validation.yaml"
PROGRESSION = ROOT / "src" / "progression.yaml"
DOC = ROOT / "design" / "PROGRESSION_GRAPH.md"
ATOM = re.compile(r"(#?)([a-z0-9_.-]+:[a-z0-9_./-]+)")


class Report:
    def __init__(self):
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)
        self.stats = {}

    def error(self, check, text):
        self.errors[check].append(text)

    def warn(self, check, text):
        self.warnings[check].append(text)

    def print(self, checks):
        for check in checks:
            errs, warns = self.errors.get(check, []), self.warnings.get(check, [])
            state = "FAIL" if errs else "ok"
            print(f"[{state:4}] {check:10} {self.stats.get(check, '')}")
            for e in errs:
                print(f"         ERROR {e}")
            for w in warns:
                print(f"         warn  {w}")
        n = sum(len(v) for v in self.errors.values())
        w = sum(len(v) for v in self.warnings.values())
        print(f"{n} error(s), {w} warning(s)")
        return n


class Live:
    def __init__(self):
        if not (LIVE / "ids.json").exists():
            sys.exit("research/registry/live/ is missing: run tools/build_pack.py --export && tools/dump_live.py")
        self.ids = {k: set(v) for k, v in json.loads((LIVE / "ids.json").read_text()).items()}
        self.tags = json.loads((LIVE / "tags.json").read_text())
        self.recipes = json.loads((LIVE / "recipes.json").read_text())
        loot = json.loads((LIVE / "loot.json").read_text())
        self.natural = set(loot.pop("natural_blocks", []))
        self.loot = loot

    def tag_items(self, tag):
        return self.tags["item"].get(tag, [])


def load_chapters():
    docs = []
    for f in sorted(QUESTS.glob("chapters/*.yaml")):
        doc = yaml.safe_load(f.read_text())
        if doc:
            doc["_file"] = f.name
            docs.append(doc)
    return docs


def load_tables():
    tables = yaml.safe_load((QUESTS / "reward_tables.yaml").read_text()) or {}
    for extra in sorted(QUESTS.glob("reward_tables/*.yaml")):
        tables.update(yaml.safe_load(extra.read_text()) or {})
    return tables


def quest_index(docs):
    """'chapter/key' -> quest dict (with _id, _chapter, _group, _deps as full ids)."""
    index = {}
    for doc in docs:
        for q in doc["quests"]:
            qid = f"{doc['chapter']}/{q['key']}"
            q["_id"], q["_chapter"], q["_group"] = qid, doc["chapter"], doc["group"]
            q["_deps"] = [d if "/" in d else f"{doc['chapter']}/{d}" for d in q.get("deps", [])]
            index[qid] = q
    return index


def item_id(spec):
    return spec if isinstance(spec, str) else spec["id"]


# ---------------------------------------------------------------- book in sync
def check_book(rep):
    sys.path.insert(0, str(ROOT / "tools"))
    import build_quests
    book = build_quests.OUT
    side = [build_quests.NARRATION_JS, build_quests.VOICE_SRC / "lines.yaml"]
    before = {p: p.read_bytes() if p.exists() else None for p in side}
    with tempfile.TemporaryDirectory() as tmp:
        build_quests.OUT, build_quests.OLD_FTB = Path(tmp) / "book", None
        try:
            chapters, quests, tables = build_quests.Compiler().run()
        finally:
            build_quests.OUT = book
        fresh = {p.relative_to(Path(tmp) / "book").as_posix(): p.read_bytes()
                 for p in (Path(tmp) / "book").rglob("*") if p.is_file()}
    shipped = {p.relative_to(book).as_posix(): p.read_bytes() for p in book.rglob("*") if p.is_file()}
    for name in sorted(set(fresh) | set(shipped)):
        if name not in shipped:
            rep.error("book", f"{name} is missing from the compiled book: run tools/build_quests.py")
        elif name not in fresh:
            rep.error("book", f"{name} is in the compiled book but no source makes it: run tools/build_quests.py")
        elif fresh[name] != shipped[name]:
            rep.error("book", f"{name} differs from its source: run tools/build_quests.py")
    for p in side:
        after = p.read_bytes() if p.exists() else None
        if after != before[p]:
            rep.error("book", f"{p.relative_to(ROOT)} was out of date: run tools/build_quests.py")
            if before[p] is None:
                p.unlink()
            else:
                p.write_bytes(before[p])        # a check must not change the tree
    rep.stats["book"] = f"{chapters} chapters, {quests} quests, {tables} reward tables"


# ---------------------------------------------------------------- quest graph
def check_graph(rep, index):
    for qid, q in index.items():
        for d in q["_deps"]:
            if d not in index:
                rep.error("graph", f"{qid}: unknown dependency {d}")
            elif d == qid:
                rep.error("graph", f"{qid}: depends on itself")
        if q.get("min_deps") and q["min_deps"] > len(q["_deps"]):
            rep.error("graph", f"{qid}: min_deps {q['min_deps']} but only {len(q['_deps'])} dependencies")
        need = q.get("min_deps") or len(q["_deps"])
        optional = [d for d in q["_deps"] if d in index and index[d].get("optional")]
        if not q.get("optional") and optional and len(q["_deps"]) - len(optional) < need:
            rep.error("graph", f"{qid}: a required quest that waits on optional {', '.join(optional)}")
    # cycles: iterative DFS with colours
    state, edges = {}, {qid: [d for d in q["_deps"] if d in index] for qid, q in index.items()}
    for start in index:
        if state.get(start):
            continue
        stack = [(start, iter(edges[start]))]
        state[start] = 1
        path = [start]
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
                path.pop()
            elif state.get(nxt) == 1:
                rep.error("graph", "dependency cycle: " + " -> ".join(path[path.index(nxt):] + [nxt]))
            elif not state.get(nxt):
                state[nxt] = 1
                stack.append((nxt, iter(edges[nxt])))
                path.append(nxt)
    rep.stats["graph"] = f"{len(index)} quests, {sum(len(v) for v in edges.values())} dependencies"


def ancestors(index, qid, memo):
    if qid not in memo:
        out = set()
        for d in index[qid]["_deps"]:
            if d in index:
                out.add(d)
                out |= ancestors(index, d, memo)
        memo[qid] = out
    return memo[qid]


# ---------------------------------------------------------------- ids
def check_ids(rep, live, docs, tables):
    n = 0

    def known(where, kind, value):
        nonlocal n
        n += 1
        if value.startswith("#"):
            members = live.tags.get(kind, {}).get(value[1:])
            if not members:
                rep.error("ids", f"{where}: {kind} tag {value} does not exist or is empty")
        elif value not in live.ids.get(kind, ()):
            rep.error("ids", f"{where}: unknown {kind} {value}")

    def atoms(where, expr):
        for tag, value in ATOM.findall(expr):
            known(where, "item", tag + value)

    for doc in docs:
        ch = doc["chapter"]
        known(f"{ch} (chapter icon)", "item", doc["icon"])
        for q in doc["quests"]:
            qid = f"{ch}/{q['key']}"
            if q.get("icon"):
                known(f"{qid} icon", "item", q["icon"])
            for i, t in enumerate(q.get("tasks") or []):
                where = f"{qid} task {i}"
                if "item" in t:
                    known(where, "item", item_id(t["item"]))
                elif "filter" in t:
                    atoms(where, t["filter"])
                elif "tag" in t:
                    known(where, "item", "#" + t["tag"])
                elif "kill" in t:
                    known(where, "entity_type", t["kill"])
                elif "dimension" in t:
                    known(where, "dimension", t["dimension"])
                elif "structure" in t:
                    known(where, "structure", t["structure"])
                elif "biome" in t:
                    known(where, "biome", t["biome"])
                elif "advancement" in t:
                    known(where, "advancement", t["advancement"])
                elif "observe" in t:
                    entity = t.get("observe_type", 0) in (1, "entity")
                    known(where, "entity_type" if entity else "block", t["observe"])
            for i, r in enumerate(q.get("rewards") or []):
                where = f"{qid} reward {i}"
                if "item" in r:
                    known(where, "item", item_id(r["item"]))
                elif "command" in r:
                    root = r["command"].lstrip("/").split()[0]
                    n += 1
                    if root not in live.ids["command"]:
                        rep.error("ids", f"{where}: unknown command /{root}")
                elif "table" in r or "choice" in r:
                    key = r.get("table") or r.get("choice")
                    if key not in tables:
                        rep.error("ids", f"{where}: unknown reward table {key}")
                if r.get("icon"):
                    known(f"{where} icon", "item", r["icon"])
    for key, t in tables.items():
        if t.get("icon"):
            known(f"table {key} icon", "item", t["icon"])
        for r in t["rewards"]:
            known(f"table {key}", "item", item_id(r["item"]))
    rep.stats["ids"] = f"{n} references"


# ---------------------------------------------------------------- obtainable
class Stages:
    """The story's parts (src/progression.yaml `stages`) and which one a quest or a raw material belongs to."""

    def __init__(self, spec, index):
        spec = spec or {}
        self.names = spec.get("names") or ["Start"]
        self.opens = spec.get("opens") or []
        self.index = index
        self._anc = {}
        self.exact, self.prefix = {}, []
        for stage, items in (spec.get("first_found") or {}).items():
            for item in items:
                if item.endswith("*"):
                    self.prefix.append((item[:-1], int(stage)))
                else:
                    self.exact[item] = int(stage)

    def of_base(self, item):
        if item in self.exact:
            return self.exact[item]
        return max((st for pre, st in self.prefix if item.startswith(pre)), default=0)

    def ancestors(self, qid):
        return ancestors(self.index, qid, self._anc)

    def of_quest(self, qid):
        anc = self.ancestors(qid)
        return max((n + 1 for n, opener in enumerate(self.opens) if opener in anc), default=0)

    def provided(self, qid):
        """Items that required quests before this one hand out as rewards."""
        out = set()
        for a in self.ancestors(qid):
            q = self.index[a]
            if q.get("optional"):
                continue
            for r in q.get("rewards") or []:
                if "item" in r:
                    out.add(item_id(r["item"]))
        return out


class Obtain:
    """Which items a survival player can get, how (the first way found) and from which stage of the story."""

    def __init__(self, live, rules, stages=None):
        self.live = live
        self.how, self.stage = {}, {}
        self.stages = stages
        base = {}                                  # item -> how the world hands it out
        for group in rules.get("granted") or []:
            for item in group["items"]:
                base[item] = "src/validation.yaml: " + " ".join(group["reason"].split())
        crafted = {o for r in live.recipes.values() for o in r["o"]}
        self.pending = defaultdict(set)            # craftable block -> what its loot table drops
        for tid in live.loot:
            ns, path = tid.split(":", 1)
            items = self.table_items(tid, set())
            if path.startswith("blocks/"):
                block = f"{ns}:{path[7:]}"
                if block in live.natural or block not in crafted:
                    why = "generated by the world" if block in live.natural else "a block no recipe makes"
                    for i in items:
                        base.setdefault(i, f"loot {tid} ({why})")
                else:
                    self.pending[block] |= items
            else:
                for i in items:
                    base.setdefault(i, f"loot {tid}")
        self.makers = defaultdict(list)
        for rid, r in live.recipes.items():
            for o in r["o"]:
                self.makers[o].append(rid)
        last = len(stages.names) - 1 if stages else 0
        for now in range(last + 1):
            for item, how in base.items():
                if item not in self.how and (stages.of_base(item) if stages else 0) <= now:
                    self.how[item], self.stage[item] = how, now
            self.close(now)

    def table_items(self, tid, seen):
        if tid in seen or tid not in self.live.loot:
            return set()
        seen.add(tid)
        entry = self.live.loot[tid]
        items = set(entry["i"])
        for tag in entry["t"]:
            items |= set(self.live.tag_items(tag))
        for ref in entry["r"]:
            items |= self.table_items(ref, seen)
        return items

    def has(self, alt, by=None, extra=()):
        """Can this ingredient ('mod:item' or '#tag') be had, optionally by stage `by` or from `extra` items?"""
        members = self.live.tag_items(alt[1:]) if alt.startswith("#") else [alt]
        return any(i in extra or (i in self.how and (by is None or self.stage[i] <= by)) for i in members)

    def close(self, now):
        changed = True
        while changed:
            changed = False
            for rid, r in self.live.recipes.items():
                if not r["o"] or all(o in self.how for o in r["o"]):
                    continue
                if all(any(self.has(a) for a in alts) for alts in r["i"]):
                    for o in r["o"]:
                        if o not in self.how:
                            self.how[o], self.stage[o] = f"recipe {rid}", now
                            changed = True
            for block, items in self.pending.items():
                if block in self.how:
                    for i in items:
                        if i not in self.how:
                            self.how[i], self.stage[i] = f"loot of {block}", now
                            changed = True

    def makeable(self, alt, by, extra, depth=0, seen=None):
        """has(), but also through recipes fed by `extra` (what earlier required quests handed out)."""
        if self.has(alt, by, extra):
            return True
        if depth > 5 or not extra:
            return False
        seen = seen or set()
        members = self.live.tag_items(alt[1:]) if alt.startswith("#") else [alt]
        for item in members:
            if item in seen:
                continue
            seen.add(item)
            for rid in self.makers.get(item, []):
                if all(any(self.makeable(a, by, extra, depth + 1, seen) for a in alts)
                       for alts in self.live.recipes[rid]["i"]):
                    return True
        return False

    def lacking(self, alts, by, extra):
        """Readable reason an ingredient is not available by stage `by`."""
        out = []
        for a in alts:
            members = self.live.tag_items(a[1:]) if a.startswith("#") else [a]
            known = [self.stage[i] for i in members if i in self.stage]
            if not known:
                out.append(f"{a} (cannot be obtained at all)")
            else:
                name = self.stages.names[min(known)] if self.stages else min(known)
                out.append(f"{a} (first in {name})")
        return " | ".join(out)

    def explain(self, item, depth=0, seen=None):
        seen = seen or set()
        pad = "  " * depth
        if item in self.how:
            when = f" [{self.stages.names[self.stage[item]]}]" if self.stages else ""
            print(f"{pad}{item}{when}: {self.how[item]}")
            m = re.match(r"recipe (\S+)", self.how[item])
            if m and depth < 6 and item not in seen:
                seen.add(item)
                for alts in self.live.recipes[m.group(1)]["i"]:
                    pick = next((a for a in alts if self.has(a)), alts[0])
                    if pick.startswith("#"):
                        pick = next(i for i in self.live.tag_items(pick[1:]) if i in self.how)
                    if pick not in seen:
                        self.explain(pick, depth + 1, seen)
            return
        print(f"{pad}{item}: NOT obtainable")
        makers = [(rid, self.live.recipes[rid]) for rid in self.makers.get(item, [])]
        for rid, r in makers[:4]:
            lacking = [" | ".join(alts) for alts in r["i"] if not any(self.has(a) for a in alts)]
            print(f"{pad}  recipe {rid} lacks: {'; '.join(lacking)}")
        if not makers:
            print(f"{pad}  no recipe makes it and no loot table drops it")


def check_obtainable(rep, live, obtain, docs, rules):
    n = 0
    for group in rules.get("granted") or []:
        for item in group["items"]:
            if item not in live.ids["item"]:
                rep.error("obtainable", f"src/validation.yaml grants {item}, which is not a registered item")
    for doc in docs:
        for q in doc["quests"]:
            qid = f"{doc['chapter']}/{q['key']}"
            for i, t in enumerate(q.get("tasks") or []):
                where = f"{qid} task {i}"
                if "item" in t:
                    wanted = [item_id(t["item"])]
                elif "filter" in t:
                    wanted = [tag + v for tag, v in ATOM.findall(t["filter"])]
                elif "tag" in t:
                    wanted = ["#" + t["tag"]]
                else:
                    continue
                n += 1
                # a filter or tag is satisfied by any one of its items
                if not any(obtain.has(w) for w in wanted if w.startswith("#") or w in live.ids["item"]):
                    rep.error("obtainable", f"{where}: cannot be obtained in survival: {', '.join(wanted)}")
    rep.stats["obtainable"] = f"{n} item tasks, {len(obtain.how)} of {len(live.ids['item'])} items obtainable"


# ---------------------------------------------------------------- the pack's own recipes
def check_forge(rep, live, obtain):
    own = {rid: r for rid, r in live.recipes.items() if rid.startswith("remnants:")}
    for rid, r in sorted(own.items()):
        for o in r["o"]:
            if o not in live.ids["item"]:
                rep.error("forge", f"{rid}: makes unknown item {o}")
        for alts in r["i"]:
            real = [a for a in alts if (a.startswith("#") and live.tag_items(a[1:])) or a in live.ids["item"]]
            if not real:
                rep.error("forge", f"{rid}: ingredient {' | '.join(alts)} is not registered (or an empty tag)")
            elif not any(obtain.has(a) for a in real):
                rep.error("forge", f"{rid}: ingredient {' | '.join(alts)} cannot be obtained in survival")
    custom = sorted(i for i in live.ids["item"] if i.startswith("remnants:"))
    for item in custom:
        if item not in obtain.how:
            rep.error("forge", f"{item}: nothing makes or drops it")
    rep.stats["forge"] = f"{len(own)} recipes, {len(custom)} custom items"


def wanted_items(task):
    """The alternatives an item task accepts (any one of them satisfies it), or None for other tasks."""
    if "item" in task:
        return [item_id(task["item"])]
    if "filter" in task:
        return [tag + v for tag, v in ATOM.findall(task["filter"])]
    if "tag" in task:
        return ["#" + task["tag"]]
    return None


# ---------------------------------------------------------------- stages
def check_stages(rep, live, obtain, stages, index):
    n = 0
    for qid, q in index.items():
        now = stages.of_quest(qid)
        extra = stages.provided(qid)
        for i, t in enumerate(q.get("tasks") or []):
            wanted = wanted_items(t)
            if not wanted:
                continue
            n += 1
            real = [w for w in wanted if w.startswith("#") or w in live.ids["item"]]
            if real and not any(obtain.makeable(w, now, extra) for w in real) and any(obtain.has(w) for w in real):
                rep.error("stages", f"{qid} task {i} ({stages.names[now]}): {obtain.lacking(real, now, extra)}")
    per = defaultdict(int)
    for qid in index:
        per[stages.of_quest(qid)] += 1
    rep.stats["stages"] = f"{n} item tasks; quests per stage: " + ", ".join(
        f"{stages.names[k]} {per[k]}" for k in sorted(per))


# ---------------------------------------------------------------- gates
def gate_recipes(live, item):
    return [(rid, r) for rid, r in live.recipes.items() if item in r["o"]]


def check_gates(rep, live, obtain, stages, index, spec):
    rows = []
    for g in spec.get("gates") or []:
        item, qid = g["item"], g["quest"]
        where = f"gate {item}"
        if item not in live.ids["item"]:
            rep.error("gates", f"{where}: not a registered item")
            continue
        if qid not in index:
            rep.error("gates", f"{where}: unknown quest {qid}")
            continue
        recipes = gate_recipes(live, item)
        if not recipes:
            rep.error("gates", f"{where}: no recipe makes it")
            continue
        if not any(rid.startswith("remnants:") for rid, _ in recipes):
            rep.error("gates", f"{where}: made by {recipes[0][0]}, not by one of the pack's own recipes")
        now, extra = stages.of_quest(qid), stages.provided(qid)
        problems = []
        ok = None
        for rid, r in recipes:
            missing = [obtain.lacking(alts, now, extra) for alts in r["i"]
                       if not any(obtain.makeable(a, now, extra) for a in alts)]
            if not missing:
                ok = (rid, r)
                break
            problems.append(f"{rid} needs {'; '.join(sorted(set(missing)))}")
        if not ok:
            rep.error("gates", f"{where}: not craftable when {qid} opens ({stages.names[now]}): " + " // ".join(problems))
        # the quest that needs the output must not be an ancestor of a quest that hands out an ingredient
        rid, r = ok or recipes[0]
        for alts in r["i"]:
            for a in alts:
                for giver, q in index.items():
                    gives = {item_id(x["item"]) for x in (q.get("rewards") or []) if "item" in x}
                    if a in gives and qid in stages.ancestors(giver) and not obtain.has(a):
                        rep.error("gates", f"{where}: {a} is only handed out by {giver}, which comes after {qid}")
        rows.append({"gate": g, "stage": now, "recipe": rid, "inputs": r["i"]})
    rep.stats["gates"] = f"{len(rows)} gated recipes"
    return rows


# ---------------------------------------------------------------- fragments
def check_fragments(rep, stages, index, rows, spec):
    conf = spec.get("fragments") or {}
    item, share = conf.get("item"), float(conf.get("guaranteed_share", 0))
    if not item:
        return []
    need, paid = defaultdict(int), defaultdict(int)
    for row in rows:
        need[row["stage"]] += sum(1 for alts in row["inputs"] if item in alts)
    for qid, q in index.items():
        if q["_group"] != "main" or q.get("optional"):
            continue
        for r in q.get("rewards") or []:
            if "item" in r and item_id(r["item"]) == item:
                paid[stages.of_quest(qid)] += int(r.get("count", 1))
    table, total_need, total_paid = [], 0, 0
    for k in range(len(stages.names)):
        total_need += need[k]
        total_paid += paid[k]
        table.append((stages.names[k], need[k], paid[k], total_need, total_paid))
        if total_need and total_paid < share * total_need:
            rep.error("fragments", f"by the end of {stages.names[k]} the story has asked for {total_need} and required "
                                   f"main-line quests have paid {total_paid} (under {share:.0%})")
    rep.stats["fragments"] = f"{total_need} asked for by the gates, {total_paid} paid by required main-line quests"
    return table


# ---------------------------------------------------------------- the design doc's generated tables
def item_names():
    names = {}
    for f in sorted((ROOT / "research" / "registry").glob("*_en_us.json")) + sorted(
            (ROOT / "pack" / "kubejs" / "assets").glob("*/lang/en_us.json")):
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        for k, v in data.items():
            parts = k.split(".")
            if len(parts) == 3 and parts[0] in ("item", "block") and isinstance(v, str):
                names.setdefault(f"{parts[1]}:{parts[2]}", v)
    return names


def doc_tables(live, stages, index, rows, budget):
    names = item_names()

    def name(alt):
        if alt.startswith("#"):
            return f"any `{alt}`"
        return names.get(alt) or alt.split(":", 1)[1].replace("_", " ").title()

    def inputs(alts_list):
        counts = defaultdict(int)
        for alts in alts_list:
            counts[" or ".join(name(a) for a in alts)] += 1
        return ", ".join(f"{n} × {k}" if n > 1 else k for k, n in counts.items())

    lines = ["| Stage | Recipe makes | Ingredients (the game's real recipe) | Needed by quest | From | Opens |",
             "|---|---|---|---|---|---|"]
    for row in sorted(rows, key=lambda r: r["stage"]):
        g = row["gate"]
        title = re.sub(r"&[0-9a-fk-or]", "", index[g["quest"]]["title"])
        lines.append(f"| {stages.names[row['stage']]} | **{name(g['item'])}** | {inputs(row['inputs'])} | "
                     f"{title} (`{g['quest']}`) | {', '.join(g.get('from', []))} | {g.get('to', '')} |")
    gates = "\n".join(lines)
    lines = ["| Stage | Fragments the gates ask for | Paid by required main-line quests | Asked so far | Paid so far |",
             "|---|---|---|---|---|"]
    for stage, need, paid, tneed, tpaid in budget:
        if need or paid:
            lines.append(f"| {stage} | {need} | {paid} | {tneed} | {tpaid} |")
    return {"gates": gates, "fragments": "\n".join(lines)}


def check_doc(rep, tables, write):
    if not DOC.exists():
        rep.error("doc", f"{DOC.relative_to(ROOT)} is missing")
        return
    text = DOC.read_text()
    new = text
    for key, table in tables.items():
        pattern = re.compile(rf"(<!-- generated:{key} -->\n).*?(<!-- /generated:{key} -->)", re.S)
        if not pattern.search(new):
            rep.error("doc", f"{DOC.relative_to(ROOT)} has no <!-- generated:{key} --> block")
            continue
        new = pattern.sub(lambda m: m.group(1) + table + "\n" + m.group(2), new)
    if new != text:
        if write:
            DOC.write_text(new)
            print(f"rewrote the generated tables in {DOC.relative_to(ROOT)}")
        else:
            rep.error("doc", f"{DOC.relative_to(ROOT)}: the generated tables are out of date; run "
                             "tools/validate_pack.py --write-doc")
    rep.stats["doc"] = f"{len(tables)} generated tables"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the findings to this file")
    ap.add_argument("--why", metavar="ITEM", help="print how an item is obtained (or what is missing) and exit")
    ap.add_argument("--write-doc", action="store_true", help="rewrite the generated tables in the design doc")
    args = ap.parse_args()
    live = Live()
    rules = yaml.safe_load(RULES.read_text()) if RULES.exists() else {}
    spec = yaml.safe_load(PROGRESSION.read_text())
    docs, tables = load_chapters(), load_tables()
    index = quest_index(docs)
    stages = Stages(spec.get("stages"), index)
    obtain = Obtain(live, rules, stages)
    if args.why:
        obtain.explain(args.why)
        return 0
    rep = Report()
    checks = ["book", "graph", "ids", "obtainable", "forge", "stages", "gates", "fragments", "doc"]
    check_book(rep)
    check_graph(rep, index)
    check_ids(rep, live, docs, tables)
    check_obtainable(rep, live, obtain, docs, rules)
    check_forge(rep, live, obtain)
    for opener in stages.opens:
        if opener not in index:
            rep.error("stages", f"src/progression.yaml stages.opens names an unknown quest: {opener}")
    check_stages(rep, live, obtain, stages, index)
    rows = check_gates(rep, live, obtain, stages, index, spec)
    budget = check_fragments(rep, stages, index, rows, spec)
    check_doc(rep, doc_tables(live, stages, index, rows, budget), args.write_doc)
    failed = rep.print(checks)
    if args.json:
        Path(args.json).write_text(json.dumps({"errors": rep.errors, "warnings": rep.warnings, "stats": rep.stats},
                                              indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
