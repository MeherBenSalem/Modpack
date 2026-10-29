#!/usr/bin/env bash
# Remnants | The Modpack: dedicated-server installer.
# Downloads NeoForge and every server-side mod from its official host (Modrinth or CurseForge), checks each file's
# sha1, and leaves a ready server. No mod jars are re-hosted in this zip.
#   ./install.sh            then accept the EULA in eula.txt and start with ./run.sh
set -euo pipefail
cd "$(dirname "$0")"
NEOFORGE="@NEOFORGE@"

for tool in java curl sha1sum; do
  command -v "$tool" >/dev/null || { echo "Missing $tool. Install Java 21, curl and coreutils first." >&2; exit 1; }
done

if [ ! -f "run.sh" ]; then
  echo "Installing NeoForge $NEOFORGE..."
  curl -fsSL -o neoforge-installer.jar \
    "https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEOFORGE/neoforge-$NEOFORGE-installer.jar"
  java -jar neoforge-installer.jar --install-server .
  rm -f neoforge-installer.jar neoforge-installer.jar.log
fi

mkdir -p mods
total=$(grep -c . server-mods.tsv)
n=0
while IFS=$'\t' read -r name url sha1; do
  [ -n "$name" ] || continue
  n=$((n + 1))
  if [ -f "mods/$name" ] && echo "$sha1  mods/$name" | sha1sum -c --status; then
    continue
  fi
  echo "[$n/$total] $name"
  curl -fsSL -A "Remnants-Modpack-Installer" -o "mods/$name" "$url"
  echo "$sha1  mods/$name" | sha1sum -c --status || { echo "Checksum mismatch: $name" >&2; exit 1; }
done < server-mods.tsv

[ -f user_jvm_args.txt ] && grep -q Xmx user_jvm_args.txt || printf -- "-Xms4G\n-Xmx8G\n" >> user_jvm_args.txt
[ -f eula.txt ] || echo "eula=false" > eula.txt
echo "Done. Read https://aka.ms/MinecraftEULA, set eula=true in eula.txt, then run ./run.sh"
