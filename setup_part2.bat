@echo off
setlocal

REM ### CONFIGURATION ###
set ENV_NAME=google-ai
set SERVICE_NAME=PG_Transcriber_Service
set SCRIPT_DIR=%~dp0
set APP_EXE_PATH=%SCRIPT_DIR%dist\PG_Transcriber\PG_Transcriber.exe
set APP_WORK_DIR=%SCRIPT_DIR%dist\PG_Transcriber
set CONFIG_SOURCE_PATH=%APP_WORK_DIR%\_internal\config.yaml
set CONFIG_DEST_PATH=%APP_WORK_DIR%\config.yaml
set NSSM_PATH=%SCRIPT_DIR%nssm.exe
REM ### END CONFIGURATION ###

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges.
) else (
    echo ERROR: This script must be run as Administrator to install the service.
    echo Please right-click the script and select 'Run as administrator'.
    pause
    exit /b 1
)

REM Check if NSSM exists
if not exist "%NSSM_PATH%" (
    echo ERROR: nssm.exe not found at %NSSM_PATH%
    echo Please download NSSM from https://nssm.cc/download and place it here, or add it to your PATH.
    pause
    exit /b 1
)

echo Activating Conda environment: %ENV_NAME%...
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate conda environment '%ENV_NAME%'.
    echo Make sure you closed and reopened the terminal after running part 1.
    echo Also, ensure '%ENV_NAME%' is the correct name from environment.yml.
    pause
    exit /b %errorlevel%
)

REM --- Build Step ---
echo Checking if application executable already exists: %APP_EXE_PATH%
if exist "%APP_EXE_PATH%" (
    echo Executable found. Skipping PyInstaller build.
    echo To force a rebuild, delete the '%SCRIPT_DIR%dist' folder first.
) else (
    echo Executable not found. Building application with PyInstaller...
    cd /d "%SCRIPT_DIR%"
    pyinstaller PG_Transcriber.spec
    if %errorlevel% neq 0 (
        echo ERROR: PyInstaller build failed.
        pause
        exit /b %errorlevel%
    )
    echo Build successful.
    REM Check again for executable after build
    if not exist "%APP_EXE_PATH%" (
        echo ERROR: Built executable still not found at %APP_EXE_PATH% after build.
        echo Check PyInstaller output and PG_Transcriber.spec configuration.
        pause
        exit /b 1
    )
)

REM --- Config File Copy Step ---
echo Checking config file location...
if exist "%CONFIG_DEST_PATH%" (
    echo Config file already exists at %CONFIG_DEST_PATH%. Skipping copy.
) else (
    if exist "%CONFIG_SOURCE_PATH%" (
        echo Config file found in _internal. Copying to %CONFIG_DEST_PATH%...
        copy /Y "%CONFIG_SOURCE_PATH%" "%CONFIG_DEST_PATH%" > nul
        if %errorlevel% neq 0 (
            echo ERROR: Failed to copy config.yaml from _internal directory.
            pause
            exit /b %errorlevel%
        ) else (
            echo config.yaml successfully copied next to the executable.
        )
    ) else (
        echo WARNING: config.yaml not found in %CONFIG_SOURCE_PATH% or %CONFIG_DEST_PATH%.
        echo Service might not run correctly if it requires this file.
    )
)

REM --- Service Management Step ---
echo Checking service status: %SERVICE_NAME%...
"%NSSM_PATH%" status %SERVICE_NAME% > nul 2>&1
set SERVICE_EXISTS=%errorlevel%

if %SERVICE_EXISTS% == 0 (
    echo Service '%SERVICE_NAME%' already exists.
    REM Check if it needs configuration (optional - could compare existing params)
    echo Verifying service configuration (AppDirectory and AppParameters)... 
    REM We assume if it exists, it's configured. Re-run script after deleting service to force reconfig.
) else (
    echo Service '%SERVICE_NAME%' does not exist. Installing...
    
    REM Stop and remove just in case (NSSM remove handles non-existence gracefully)
    "%NSSM_PATH%" stop %SERVICE_NAME% >nul 2>&1
    "%NSSM_PATH%" remove %SERVICE_NAME% confirm >nul 2>&1

    echo Installing service...
    "%NSSM_PATH%" install %SERVICE_NAME% "%APP_EXE_PATH%"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install service using NSSM.
        pause
        exit /b %errorlevel%
    )

    echo Configuring service parameters...
    "%NSSM_PATH%" set %SERVICE_NAME% AppParameters --monitor
    "%NSSM_PATH%" set %SERVICE_NAME% AppDirectory "%APP_WORK_DIR%"
    echo Service installed and configured.
)

REM --- Service Start Step ---
echo Checking service status before starting...
"%NSSM_PATH%" status %SERVICE_NAME% | findstr /R /C:"SERVICE_RUNNING" > nul
if %errorlevel% == 0 (
    echo Service '%SERVICE_NAME%' is already running.
) else (
    echo Starting service %SERVICE_NAME%...
    "%NSSM_PATH%" start %SERVICE_NAME%
    if %errorlevel% neq 0 (
        echo WARNING: Failed to start service %SERVICE_NAME%. Check the Windows Event Log for details.
        echo You might need to start it manually via services.msc.
    ) else (
        echo Service %SERVICE_NAME% started successfully.
    )
)

echo.
echo Setup complete.
echo You can manage the service using 'services.msc' or NSSM commands (e.g., nssm start/stop/restart %SERVICE_NAME%).

pause
endlocal 