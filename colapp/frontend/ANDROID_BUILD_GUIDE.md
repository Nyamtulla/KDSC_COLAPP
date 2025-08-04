# Android Build Guide for ColApp

This guide will help you build and export your Flutter app to Android.

## Prerequisites

1. **Flutter SDK** - Already installed (version 3.32.3)
2. **Android Studio** - For Android SDK and tools
3. **Android SDK** - API level 21 or higher
4. **Java Development Kit (JDK)** - Version 11 or higher
5. **At least 2GB free disk space** - For build process

## Quick Build (Windows)

1. **Free up disk space** - Ensure you have at least 2GB free space
2. **Run the build script**:
   ```bash
   cd colapp/frontend
   build_android.bat
   ```

## Manual Build Steps

### 1. Clean and Prepare
```bash
cd colapp/frontend
flutter clean
flutter pub get
```

### 2. Build Debug APK
```bash
flutter build apk --debug
```

### 3. Build Release APK (for distribution)
```bash
flutter build apk --release
```

### 4. Build App Bundle (recommended for Play Store)
```bash
flutter build appbundle --release
```

## Output Locations

- **Debug APK**: `build/app/outputs/flutter-apk/app-debug.apk`
- **Release APK**: `build/app/outputs/flutter-apk/app-release.apk`
- **App Bundle**: `build/app/outputs/bundle/release/app-release.aab`

## Installing on Device

### Using ADB (Android Debug Bridge)
```bash
# Enable USB debugging on your Android device
adb install build/app/outputs/flutter-apk/app-debug.apk
```

### Manual Installation
1. Transfer the APK file to your Android device
2. Enable "Install from unknown sources" in device settings
3. Open the APK file and install

## Troubleshooting

### Disk Space Issues
If you encounter "not enough space on the disk" errors:

1. **Free up space**:
   - Delete temporary files: `flutter clean`
   - Clear Gradle cache: Delete `%USERPROFILE%\.gradle\caches`
   - Clear Android build cache: Delete `android\.gradle`

2. **Build for specific architecture**:
   ```bash
   flutter build apk --debug --target-platform android-arm64
   ```

3. **Use external storage** (if available):
   - Move project to drive with more space
   - Set `GRADLE_USER_HOME` environment variable to different location

### Build Failures

1. **Check Flutter installation**:
   ```bash
   flutter doctor -v
   ```

2. **Update dependencies**:
   ```bash
   flutter pub upgrade
   ```

3. **Check Android SDK**:
   - Open Android Studio
   - Go to SDK Manager
   - Install required SDK platforms and tools

4. **Verify Java version**:
   ```bash
   java -version
   ```

### Common Issues

1. **Gradle sync failed**: 
   - Check internet connection
   - Clear Gradle cache
   - Update Gradle wrapper

2. **Permission denied**:
   - Run as administrator
   - Check file permissions

3. **Missing dependencies**:
   - Run `flutter pub get`
   - Check `pubspec.yaml` for errors

## Alternative Build Methods

### 1. Using Android Studio
1. Open the project in Android Studio
2. Open `android/` folder as Android project
3. Build → Build Bundle(s) / APK(s) → Build APK(s)

### 2. Using VS Code
1. Install Flutter extension
2. Open command palette (Ctrl+Shift+P)
3. Run "Flutter: Build APK"

### 3. Cloud Build (if local build fails)
Consider using:
- GitHub Actions
- Codemagic
- Bitrise
- Firebase App Distribution

## Release Configuration

For production releases, update `android/app/build.gradle.kts`:

```kotlin
android {
    defaultConfig {
        applicationId = "com.yourcompany.colapp"  // Change this
        versionCode = 1
        versionName = "1.0.0"
    }
    
    signingConfigs {
        create("release") {
            // Add your signing configuration
        }
    }
    
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            minifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

## Next Steps

After successful build:
1. Test the APK on different devices
2. Configure app signing for release
3. Prepare for Play Store submission
4. Set up CI/CD pipeline for automated builds

## Support

If you continue to have issues:
1. Check Flutter documentation: https://flutter.dev/docs/deployment/android
2. Review Android build logs for specific errors
3. Consider using cloud build services
4. Contact development team for assistance 