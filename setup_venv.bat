@echo off
set ENV_NAME=agentframework

echo Creating virtual environment: %ENV_NAME%
python -m venv %ENV_NAME%

echo Activating environment
call %ENV_NAME%\Scripts\activate

echo Upgrading pip
pip install --upgrade pip

echo Installing dependencies from requirements.txt
pip install -r requirements.txt

echo.
echo ✅ Setup complete.
echo To activate the environment later, run:
echo call %ENV_NAME%\Scripts\activate
