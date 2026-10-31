@echo off
rem @NAME@ @VERSION@: dedicated server start script (Windows).
rem   start.bat     first run installs NeoForge @NEOFORGE@ (needs internet once), then starts the server
rem   set JAVA=C:\path\to\java.exe before running to use a specific Java 21+ install
rem Memory and JVM flags live in user_jvm_args.txt. Read SERVER.md for the rest.
setlocal
cd /d "%~dp0"

set "NEOFORGE_VERSION=@NEOFORGE@"
set "INSTALLER=neoforge-%NEOFORGE_VERSION%-installer.jar"
set "ARGS_FILE=libraries\net\neoforged\neoforge\%NEOFORGE_VERSION%\win_args.txt"
if not defined JAVA set "JAVA=java"

"%JAVA%" -version >nul 2>&1
if errorlevel 1 (
  echo Java was not found. Install Java 21 from https://adoptium.net or set JAVA to your java.exe.
  goto :fail
)
set "JAVA_MAJOR="
"%JAVA%" -version 2> "%TEMP%\remnants-java-version.txt"
for /f "tokens=3" %%v in ('findstr /i /c:" version " "%TEMP%\remnants-java-version.txt"') do if not defined JAVA_MAJOR set "JAVA_MAJOR=%%~v"
for /f "delims=." %%m in ("%JAVA_MAJOR%") do set "JAVA_MAJOR=%%m"
if not defined JAVA_MAJOR set "JAVA_MAJOR=0"
if %JAVA_MAJOR% LSS 21 (
  echo This server needs Java 21 or newer; "%JAVA%" is version %JAVA_MAJOR%.
  echo Install Java 21 from https://adoptium.net or set JAVA to its java.exe.
  goto :fail
)

if not exist "%ARGS_FILE%" (
  echo Installing NeoForge %NEOFORGE_VERSION% ^(first start only^)...
  "%JAVA%" -jar "%INSTALLER%" --install-server .
  if errorlevel 1 (
    echo NeoForge install failed; see %INSTALLER%.log
    goto :fail
  )
)

findstr /i /b /c:"eula=true" eula.txt >nul 2>&1
if errorlevel 1 goto :eula
goto :run

:eula
echo You must accept the Minecraft EULA to run a server: https://aka.ms/MinecraftEULA
set "ANSWER="
set /p "ANSWER=Do you accept the Minecraft EULA? [y/N] "
if /i "%ANSWER%"=="y" goto :accept
if /i "%ANSWER%"=="yes" goto :accept
> eula.txt echo eula=false
goto :fail

:accept
> eula.txt echo eula=true

:run
"%JAVA%" @user_jvm_args.txt @%ARGS_FILE% nogui %*
pause
exit /b

:fail
pause
exit /b 1
