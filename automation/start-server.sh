#!/bin/bash
# Fabric Minecraft 1.21.1 server startup for Linux
# Mirrors start-server.bat: Java 21, Generational ZGC, 4-12 GB heap

set -euo pipefail

cd "$(dirname "$0")"

# Require Java 21 — use Adoptium Temurin from home directory
JAVA_EXE="$HOME/adoptium-jdk21/bin/java"
if [ ! -x "$JAVA_EXE" ]; then
    echo "Java not found at $JAVA_EXE"
    echo "Install Adoptium Temurin 21 or place it at $JAVA_EXE"
    exit 1
fi

# Do not start until the intended world is present.
if [ ! -f "world/level.dat" ]; then
    echo "Restored world not imported yet."
    echo "Save and Quit Minecraft, then run import-restored-world.bat (Windows) or import the world manually."
    exit 1
fi

if [ ! -f "fabric-server-launch.jar" ]; then
    echo "Missing fabric-server-launch.jar in this folder."
    exit 1
fi

mkdir -p logs

# Protect the world from duplicate launches, including near-simultaneous starts.
# The lock stays held until the server process exits.
exec 9> .fabric-server-start.lock
if ! flock -n 9; then
    echo "A Fabric server launch is already in progress or running. Aborting."
    exit 1
fi
# Also guard against a server started before this lock was added.
if ss -ltnH '( sport = :25566 )' | grep -q .; then
    echo "Port 25566 is already in use. Refusing to launch a duplicate server."
    exit 1
fi

JAVA_FLAGS="-Xms4G -Xmx12G -XX:+UseZGC -XX:+ZGenerational -XX:SoftMaxHeapSize=10G -XX:ZUncommitDelay=300"

echo ""
echo "Starting Fabric 1.21.1 server"
"$JAVA_EXE" -version
echo "JVM flags: $JAVA_FLAGS"
echo "GC log: logs/server-gc.log"
echo ""

"$JAVA_EXE" $JAVA_FLAGS \
    -Xlog:gc*,safepoint:file=logs/server-gc.log:time,uptime,level,tags:filecount=4,filesize=10M \
    -jar "fabric-server-launch.jar" nogui

SERVER_EXIT=$?
echo ""
echo "Server stopped with exit code $SERVER_EXIT."
exit "$SERVER_EXIT"