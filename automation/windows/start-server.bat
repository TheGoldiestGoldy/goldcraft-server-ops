@echo off
setlocal
cd /d "%~dp0"

rem =============================================================
rem Fabric Minecraft 1.21.1 - 2-player server startup (Java 21)
rem Generational ZGC, 12 GB maximum heap, rotating GC diagnostics
rem Preserves world safety check, port 25566 guard, VSS/DH config
rem =============================================================

rem Allow only the original optional argument.
if /I not "%~1"=="with-vss" if not "%~1"=="" (
    echo Unknown server mode: %~1
    exit /b 1
)

rem Do not start until the intended world is present.
if not exist "world\level.dat" (
    echo Restored world not imported yet.
    echo Save and Quit Minecraft, then run import-restored-world.bat.
    pause
    exit /b 1
)

rem Do not launch a second server on port 25566.
set "SERVER_PID="
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "$connection = Get-NetTCPConnection -State Listen -LocalPort 25566 -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess; if ($connection) { $connection }"`) do set "SERVER_PID=%%P"
if defined SERVER_PID (
    echo A server is already running on port 25566. Process ID: %SERVER_PID%
    echo Connect to it, or run /restart in-game as an operator.
    echo Do not launch a second copy.
    pause
    exit /b 1
)

echo Preserving VSS/DH settings from config.
echo Use /vsslod reload after changing them.

rem Java 21 HotSpot required for the -XX:+ZGenerational option below.
set "JAVA_EXE=C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot\bin\java.exe"
if not exist "%JAVA_EXE%" (
    echo Java not found at: %JAVA_EXE%
    echo Update JAVA_EXE to the path of your Java 21 HotSpot installation.
    pause
    exit /b 1
)

if not exist "fabric-server-launch.jar" (
    echo Missing fabric-server-launch.jar in this folder.
    pause
    exit /b 1
)

rem 4 GB minimum; up to 12 GB on demand; 10 GB soft target.
rem Generational ZGC is opt-in on Java 21 and manages GC threads itself.
rem Unused committed heap can be returned after 5 minutes (default).
set "JAVA_FLAGS=-Xms4G -Xmx12G -XX:+UseZGC -XX:+ZGenerational -XX:SoftMaxHeapSize=10G -XX:ZUncommitDelay=300"

if not exist "logs" mkdir "logs"

echo.
echo Starting Fabric 1.21.1 server
"%JAVA_EXE%" -version
echo JVM flags: %JAVA_FLAGS%
echo GC log: logs\server-gc.log
echo.

"%JAVA_EXE%" %JAVA_FLAGS% -Xlog:gc*,safepoint:file=logs/server-gc.log:time,uptime,level,tags:filecount=4,filesize=10M -jar "fabric-server-launch.jar" nogui

set "SERVER_EXIT=%ERRORLEVEL%"
echo.
echo Server stopped with exit code %SERVER_EXIT%.
pause
exit /b %SERVER_EXIT%
