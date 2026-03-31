@echo off
echo.
echo ========================================
echo INSTALLING DEPENDENCIES...
echo ========================================
pip install -r requirements.txt

echo.
echo ========================================
echo STARTING NEWS API SERVER...
echo ========================================
echo.
python news_api.py

pause
