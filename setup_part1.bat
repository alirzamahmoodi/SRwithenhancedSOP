@echo off
REM ### CONFIGURATION ###
set ENV_NAME=google-ai 
REM ### END CONFIGURATION ###

echo Checking if Conda environment '%ENV_NAME%' already exists...
conda env list | findstr /B /C:"%ENV_NAME% " > nul
if %errorlevel% == 0 (
    echo Environment '%ENV_NAME%' already exists. Skipping creation.
) else (
    echo Environment '%ENV_NAME%' not found. Creating...
    conda env create -f environment.yml
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create conda environment. Please check environment.yml and conda installation.
        pause
        exit /b %errorlevel%
    )
    echo Environment '%ENV_NAME%' created successfully.
)


echo Initializing Conda for your shell (powershell)...
conda init powershell
REM You could use "conda init cmd.exe" if you primarily use Command Prompt instead of PowerShell

echo.
echo --- IMPORTANT ---
echo Conda has been initialized (or was already initialized).
echo If this is the first time running this script or if conda commands didn't work before, please CLOSE this terminal window now.
echo Then, OPEN a NEW terminal window and run setup_part2.bat as ADMINISTRATOR.
echo If you are sure conda is initialized correctly for new terminals, you might not need to restart.
echo --- IMPORTANT ---
echo.
pause 