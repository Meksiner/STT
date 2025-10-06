@echo off
chcp 65001 >nul
title Speech Recognition App
echo ===============================
echo    Flask Speech Recognition
echo ===============================
echo.

:: Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python не установлен или не добавлен в PATH
    echo Установите Python с официального сайта: https://python.org
    pause
    exit /b 1
)

:: Проверяем наличие app.py
if not exist "app.py" (
    echo ERROR: Файл app.py не найден
    echo Убедитесь, что start_app.bat находится в той же папке что и app.py
    pause
    exit /b 1
)

echo Запуск приложения...
echo Откройте браузер и перейдите по адресу: http://127.0.0.1:5000
echo.
echo Для остановки приложения нажмите Ctrl+C в этом окне
echo.

:: Запускаем приложение
python app.py

:: Если приложение закрылось с ошибкой
if errorlevel 1 (
    echo.
    echo ERROR: Приложение завершилось с ошибкой
    echo Возможные причины:
    echo - Не установлены необходимые библиотеки
    echo - Порт 5000 занят другим приложением
    echo - Проблемы с моделью Vosk
    echo.
    echo Установите зависимости командой:
    echo pip install flask sounddevice vosk soundfile
    echo.
    pause
)