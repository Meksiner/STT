@echo off
chcp 65001 >nul
title Установка зависимостей
echo Установка необходимых библиотек Python...
echo.

pip install flask sounddevice vosk soundfile

if errorlevel 1 (
    echo.
    echo ERROR: Не удалось установить зависимости
    echo Попробуйте установить вручную:
    echo pip install flask sounddevice vosk soundfile
    pause
    exit /b 1
)

echo.
echo Все зависимости успешно установлены!
echo Теперь вы можете запустить приложение через start_app.bat
pause