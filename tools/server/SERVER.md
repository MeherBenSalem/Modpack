# @NAME@ @VERSION@: dedicated server

Everything the server needs is in this folder: the server-side mods (`mods/`), the pack's configs and scripts
(`config/`, `kubejs/`), the NeoForge @NEOFORGE@ installer, start scripts, tuned `server.properties` and JVM flags.
Client-only mods (shaders, sound, HUD, menus) are left out; players join with the client pack of the same version.

## Requirements

- **Java 21** (64-bit). [Adoptium Temurin 21](https://adoptium.net) is a good choice.
- **RAM:** the server is set to 6 GB (`user_jvm_args.txt`). Use 8 GB for 5+ players or a large world, and leave
  1-2 GB free for the operating system. A CPU with strong single-core speed matters more than core count.
- **Disk:** about 1 GB plus the world (a 3,000-block pregenerated overworld is several GB).
- **Network:** players connect on **TCP 25565** (`server-port`); open or forward that port. Query (UDP) and RCON
  (TCP 25575) are off by default.

## First start

1. Unzip into an empty folder.
2. Run `./start.sh` (Linux/macOS; `chmod +x start.sh` if needed) or double-click `start.bat` (Windows).
   The first start installs NeoForge into `libraries/` (needs internet once) and asks you to accept the
   [Minecraft EULA](https://aka.ms/MinecraftEULA); you can also put `eula=true` in `eula.txt` yourself.
3. Wait for `Done (...)! For help, type "help"`, then `op <your name>` in the console.

Keep `online-mode=true`: it checks every player's Mojang account. Change memory in `user_jvm_args.txt` (keep -Xms
equal to -Xmx) and server settings in `server.properties`.

## What is tuned

- `server.properties`: gameplay as in singleplayer (normal difficulty, view distance 10, simulation distance 8, no
  spawn protection); `sync-chunk-writes=false` (async saves), `allow-flight=true` (modded dashes, leaps and mounts
  aren't kicked as flying) and `max-tick-time=180000` (heavy structure worldgen can't trip the 60 s watchdog; a truly
  hung server still stops after 3 minutes).
- `user_jvm_args.txt`: G1 with Aikar's flags for short, steady GC pauses.
- Performance mods already included: ModernFix, FerriteCore, Lithium, Clumps, Packet Fixer and spark.

## Pregenerate the world with Chunky (recommended)

This pack's terrain and structures are expensive to generate. Generate the area players will explore before they
join, with nobody online (it takes a while; "Can't keep up" messages during the run are normal):

```
chunky world minecraft:overworld
chunky center 0 0
chunky radius 3000
chunky start
```

`chunky progress` shows the progress, `chunky pause` / `chunky continue` pause and resume (a stopped server resumes
with `chunky continue`). Do the Nether afterwards with `chunky world minecraft:the_nether` and `chunky radius 1000`.
A matching `worldborder set 6000` keeps players inside the pregenerated area.

## Lag and troubleshooting

- `spark tps` and `spark health` show tick time and memory; `spark profiler start --timeout 120` makes a shareable
  report of what the server spends its time on.
- Players see "mod mismatch" or can't join: their client pack version must match this server pack.
- Crash reports land in `crash-reports/`, logs in `logs/latest.log`.

## Updating to a new pack version

Back up first. Replace `mods/`, `config/`, `kubejs/` and the start scripts with the new ones; keep `world/`,
`server.properties`, `eula.txt`, `ops.json`, `whitelist.json` and your own config changes. If the NeoForge version
changed, the start script installs it on the next start.
