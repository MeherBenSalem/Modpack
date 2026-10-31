#!/usr/bin/env bash
# @NAME@ @VERSION@: dedicated server start script (Linux and macOS).
#   ./start.sh            first run installs NeoForge @NEOFORGE@ (needs internet once), then starts the server
#   JAVA=/path/to/java ./start.sh    use a specific Java 21+ install
# Memory and JVM flags live in user_jvm_args.txt. Read SERVER.md for the rest.
set -eu
cd "$(dirname "$0")"

NEOFORGE_VERSION="@NEOFORGE@"
INSTALLER="neoforge-$NEOFORGE_VERSION-installer.jar"
ARGS_FILE="libraries/net/neoforged/neoforge/$NEOFORGE_VERSION/unix_args.txt"
JAVA="${JAVA:-java}"

if ! command -v "$JAVA" >/dev/null 2>&1; then
  echo "Java was not found. Install Java 21 (https://adoptium.net) or set JAVA=/path/to/java." >&2
  exit 1
fi
JAVA_MAJOR=$("$JAVA" -version 2>&1 | awk -F'"' '/ version "/ { split($2, v, "."); print v[1]; exit }')
if [ -z "$JAVA_MAJOR" ] || [ "$JAVA_MAJOR" -lt 21 ]; then
  echo "This server needs Java 21 or newer; '$JAVA' is version ${JAVA_MAJOR:-unknown}." >&2
  echo "Install Java 21 (https://adoptium.net) or set JAVA=/path/to/java21/bin/java." >&2
  exit 1
fi

if [ ! -f "$ARGS_FILE" ]; then
  echo "Installing NeoForge $NEOFORGE_VERSION (first start only)..."
  "$JAVA" -jar "$INSTALLER" --install-server . || { echo "NeoForge install failed; see $INSTALLER.log" >&2; exit 1; }
fi

if ! grep -qi '^eula=true' eula.txt 2>/dev/null; then
  echo "You must accept the Minecraft EULA to run a server: https://aka.ms/MinecraftEULA"
  if [ -t 0 ]; then
    printf "Do you accept the Minecraft EULA? [y/N] "
    read -r answer
    case "$answer" in
      [yY]*) echo "eula=true" > eula.txt ;;
      *) echo "eula=false" > eula.txt; exit 1 ;;
    esac
  else
    echo "eula=false" > eula.txt
    echo "Set eula=true in eula.txt, then run ./start.sh again." >&2
    exit 1
  fi
fi

exec "$JAVA" @user_jvm_args.txt "@$ARGS_FILE" nogui "$@"
