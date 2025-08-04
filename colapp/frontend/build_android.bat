@echo off
echo ========================================
echo ColApp Android Build Script
echo ========================================

echo Checking Flutter installation...
flutter --version
if %errorlevel% neq 0 (
    echo ERROR: Flutter is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Cleaning previous builds...
flutter clean

echo.
echo Getting dependencies...
flutter pub get

echo.
echo Building debug APK...
flutter build apk --debug

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Debug APK location: build\app\outputs\flutter-apk\app-debug.apk
    echo.
    echo To install on device:
    echo adb install build\app\outputs\flutter-apk\app-debug.apk
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Possible solutions:
    echo 1. Free up disk space (at least 2GB recommended)
    echo 2. Check if Android SDK is properly installed
    echo 3. Try building for specific architecture:
    echo    flutter build apk --debug --target-platform android-arm64
    echo 4. Try building app bundle instead:
    echo    flutter build appbundle --debug
)

echo.
pause 